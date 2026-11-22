# Blue Check Forge

Mark files as done in GNOME Files (Nautilus). A blue check appears beside the file icon in grid view.

## Install

Run `./install.sh` from this directory as your regular user. It installs into your user data directory. It needs Nautilus with file emblems, GVfs metadata support, and the system Python with PyGObject (`python3-gi` on Ubuntu).

## Use

Select one or more files and right-click. Choose **Scripts → ✓ Mark as Done** or **Scripts → ✕ Remove Done Mark**. If a badge is slow to update, reload the folder with **Ctrl+R**.

The badge is stored in GNOME file metadata and leaves the file’s contents, icon, and other badges intact. The mark is local to your user account.

For local regular files, the scripts ask Nautilus to refresh by reapplying the existing access and modification times. This updates Linux’s inode change time (`ctime`).
