#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
data_dir=${XDG_DATA_HOME:-"$HOME/.local/share"}
scripts_dir="$data_dir/nautilus/scripts"
icon_theme="$data_dir/icons/hicolor"
badge="emblem-blue-check-forge-done.svg"

is_blue_check_script() {
    [ -f "$1" ] && grep -Fq 'DONE_BADGE = "blue-check-forge-done"' "$1"
}

# Check the runtime before adding the menu entries.
/usr/bin/python3 -c 'from gi.repository import Gio'

for name in '✓ Mark as Done' '✕ Remove Done Mark'; do
    script="$scripts_dir/$name"
    if [ -L "$script" ] || { [ -e "$script" ] && ! is_blue_check_script "$script"; }; then
        printf 'A different script already uses this name: %s\n' "$script" >&2
        exit 1
    fi
done

install -d "$scripts_dir" "$icon_theme/scalable/emblems"
install -m 644 "$project_dir/$badge" "$icon_theme/scalable/emblems/$badge"

if command -v gtk4-update-icon-cache >/dev/null 2>&1; then
    gtk4-update-icon-cache --force --ignore-theme-index --quiet "$icon_theme"
elif command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache --force --ignore-theme-index --quiet "$icon_theme"
fi

for name in '✓ Mark as Done' '✕ Remove Done Mark'; do
    install -m 755 "$project_dir/blue-check-forge.py" "$scripts_dir/$name"
done

for name in 'Mark as Done' 'Remove Done Mark'; do
    script="$scripts_dir/$name"
    if [ ! -L "$script" ] && is_blue_check_script "$script"; then
        rm -- "$script"
    fi
done

printf '%s\n' 'Installed ✓ Mark as Done and ✕ Remove Done Mark in GNOME Files.'
