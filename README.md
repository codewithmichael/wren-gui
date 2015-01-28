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

Clone or extract anywhere and run via `sudo wren-gui` (requires root permissions).

### Requirements

Wren GUI is written primarily in Python/GTK+ and is currently designed around:

* [Wren 0.1.0](https://github.com/trynd/wren/releases/tag/v0.1.0)
* [Ubuntu Desktop 14.04.1 LTS](http://releases.ubuntu.com/14.04.1/) (32-bit) root image

All necessary libraries are available in a base Ubuntu Desktop 14.04.1 LTS root image (installed from `ubuntu-14.04.1-desktop-i386.iso`).

Your mileage may vary on other configurations.
