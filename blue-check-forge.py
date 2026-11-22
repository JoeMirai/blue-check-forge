#!/usr/bin/python3

import fcntl
import os
from pathlib import Path
import subprocess
import sys

from gi.repository import Gio, GLib


EMBLEMS = "metadata::emblems"
DONE_BADGE = "blue-check-forge-done"
NO_FOLLOW = Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS


def refresh_file(file, file_type):
    path = file.get_path()
    if path is None or file_type != Gio.FileType.REGULAR:
        return

    # GVfs metadata changes alone do not notify the open Nautilus folder.
    # Reapply the existing timestamps to send a file attribute change event.
    try:
        info = os.stat(path, follow_symlinks=False)
        os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns), follow_symlinks=False)
    except OSError:
        # Nautilus will pick up the badge on the next folder reload.
        pass


def set_done(file, done):
    info = file.query_info(f"standard::type,{EMBLEMS}", NO_FOLLOW)
    emblems = info.get_attribute_stringv(EMBLEMS)
    if (DONE_BADGE in emblems) == done:
        return

    if done:
        emblems.append(DONE_BADGE)
    else:
        emblems = [emblem for emblem in emblems if emblem != DONE_BADGE]

    if emblems:
        update = Gio.FileInfo.new()
        update.set_attribute_stringv(EMBLEMS, emblems)
        saved = file.set_attributes_from_info(update, NO_FOLLOW)
    else:
        saved = file.set_attribute(EMBLEMS, Gio.FileAttributeType.INVALID, None, NO_FOLLOW)

    if not saved:
        raise OSError("Could not save badge metadata")

    refresh_file(file, info.get_file_type())


def report_errors(errors):
    message = "\n".join(errors)
    print(message, file=sys.stderr)
    if "NAUTILUS_SCRIPT_CURRENT_URI" in os.environ:
        try:
            subprocess.run(
                ["notify-send", "--app-name=Blue Check Forge", "Could not update done badge", message],
                check=False,
            )
        except OSError:
            pass
    return 1


def main():
    action = Path(sys.argv[0]).name.removeprefix("✅ ").removeprefix("❌ ")
    if action not in ("Mark as Done", "Remove Done Mark"):
        return report_errors(["Run Mark as Done or Remove Done Mark from the Nautilus Scripts menu."])

    uris = os.environ.get("NAUTILUS_SCRIPT_SELECTED_URIS", "")
    if uris:
        files = [Gio.File.new_for_uri(uri) for uri in uris.split("\n") if uri]
    else:
        files = [Gio.File.new_for_commandline_arg(arg) for arg in sys.argv[1:]]
    if not files:
        return report_errors(["Select at least one file."])

    errors = []
    lock_path = Path(GLib.get_user_runtime_dir()) / "blue-check-forge.lock"
    try:
        with lock_path.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            for file in files:
                try:
                    set_done(file, action == "Mark as Done")
                except (GLib.Error, OSError) as error:
                    message = error.message if isinstance(error, GLib.Error) else str(error)
                    errors.append(f"{file.get_parse_name()} — {message}")
    except OSError as error:
        errors.append(str(error))

    return report_errors(errors) if errors else 0


if __name__ == "__main__":
    sys.exit(main())
