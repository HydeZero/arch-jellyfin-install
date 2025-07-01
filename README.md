# Arch Linux Jellyfin Install Script
This script installs Arch Linux with Jellyfin using simple text-based questions. It also (optionally) installs NordVPN to take advantage of [Meshnet](https://meshnet.nordvpn.com/getting-started/meshnet-explained) (allows you to access Jellyfin from outside without any firewall changes).

> [!WARNING]
> This program is designed to do a fresh install of Arch Linux with Jellyfin on multiple drives. Please be advised that this script doesn't support dual-boot as each config is unique. So, by running this script, your OS will be replaced with Arch Linux. Please make a backup of any important info before installing.

## REQUIREMENTS
* Arch Live CD ([can be acquired from here](https://archlinux.org/download/))
* A good wifi/ethernet connection
* See the [Jellyfin Documentation](https://jellyfin.org/docs/general/administration/hardware-selection/) for more details.

## Running
From the Arch Live CD terminal, type:
```bash
pacman -Sy && pacman -S git --noconfirm && git clone https://github.com/HydeZero/arch-jellyfin-install.git && cd arch-jellyfin-install && python main.py
```
This will install git, clone this repository, and run the installation script.

## Features
* Can install to EFI
* (mostly) unattended (you do need to input passwords manually)
* Makes a startup script to run jellyfin every bootup
* Simple to install
* Installs AMD/Intel gpu drivers via `mesa`

## TO ADD:
* BIOS install
* Nvidia GPU detection/install
