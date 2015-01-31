# Wren GUI

Wren GUI provides a simple administration interface for a running [Wren](https://github.com/trynd/wren) platform instance.

## Features

Basic features include:

* Active monitors for disk, save-file, RAM, and swap usage
* Save to disk (with drop-down save name selection)
* Increase active save size
* Clean apt caches
* Drop memory caches
* Grub configuration maintenance
  * View current configuration
  * Preview updated configuration
  * Perform configuration update (with built-in backup)

## Installation

To download and install Wren GUI on a running Wren instance:

* **Simple:** Clone or extract anywhere and run `sudo ./wren-gui` from within the project directory.
* **Full Installation:** Copy and paste the following (long and ugly) command into a terminal and press enter (assumes Ubuntu):
  * `pushd /opt && wget https://github.com/trynd/wren-gui/archive/master.tar.gz -O - | sudo tar xz && sudo mv wren-gui-master wren-gui && sudo ln -sf /opt/wren-gui/wren-gui /usr/local/sbin/wren-gui && popd`
  * The above command extracts the latest version of Wren GUI to the `/opt/wren-gui` directory and creates a symbolic link to the application in `usr/local/sbin`
  * Once it's installed you can start Wren GUI from a terminal at any time with the command `sudo wren-gui`


### Requirements

Wren GUI is written primarily in Python/GTK+ and is currently designed around:

* [Wren 0.1.0](https://github.com/trynd/wren/releases/tag/v0.1.0)
* [Ubuntu Desktop 14.04.1 LTS](http://releases.ubuntu.com/14.04.1/) (32-bit) root image

All necessary libraries are available in a base Ubuntu Desktop 14.04.1 LTS root image (installed from `ubuntu-14.04.1-desktop-i386.iso`).

Your mileage may vary on other configurations.
