import os
import subprocess
import time

os.system('clear')

def welcome(time_left):
    while time_left > 0:
        os.system('clear')
        print("This program comes with absolutely NO warranty. By running this, you permit this program to make changes to your system that are irreversible.")
        if time_left == 1:
            print(f"This message dismisses in {time_left} second.")
        else:
            print(f"This message dismisses in {time_left} seconds.")
        time.sleep(1)
        time_left -= 1
def init_install():
    os.system('clear')
    print("WELCOME TO ARCH+JELLYFIN INSTALLATION")
    print("")
    print("This program installs Arch Linux and Jellyfin. To get started, I need to check for repository updates. I am running this in the background. Errors should halt the program.")
    _ = os.system("pacman -Sy")
    print("Done!")
    time.sleep(2)

is_efi = False
efi_type = 0
hostname_ans = ""
disk_to_install = ""
media_drives = []
time_zone = ""
is_meshnet = False
username = ""

startup_script = """#!/bin/bash
# Startup script for Jellyfin container
docker run -d \
 --name jellyfin \
 --user uid:gid \
 --net=host \
 --volume jellyfin-config:/config \
 --volume jellyfin-cache:/cache \
 --mount type=bind,source=/path/to/media,target=/media \
 --restart=unless-stopped \
 jellyfin/jellyfin"""

def questions():
    global is_efi
    global efi_type
    global hostname_ans
    global disk_to_install
    global media_drives
    global time_zone
    global is_meshnet

    os.system("clear")
    print("Doing some preliminary checks...")
    print("Checking EFI...")
    try:
        with open("/sys/firmware/efi/fw_platform_size", "r") as efi_bin:
            efi_type = int(efi_bin.read())
        is_efi = True
        print(f"EFI: Found, architecture is {efi_type} bit") 
    except FileNotFoundError:
        print("EFI: NOT FOUND, likely BIOS boot.")
    print("Updating time...")
    _ = os.system("timedatectl")
    print("Time updated.")
    time.sleep(2)
    while True:
        os.system('clear')
        print("DISK PARTITIONING\n")
        print("To actually use Arch Linux, I need a disk to install it to.")
        print("Select your disk you want to install the system to. To identify the disk, see the disk size.")
        os.system('lsblk')
        print("Type the full name of the disk ('/dev/sda', '/dev/sdb', '/dev/nvme0n1', etc.)")
        disk_to_install = input("> ")
        print("If I am hearing you right, you selected:")
        print(disk_to_install)
        print("to install to. Is this correct? [y/N]")
        if input("> ").lower() == "y":
            break
    print("Do you have any media drives that need to be formatted? [y/N]")
    if input("> ").lower() == "y":
        while True:
            print("Select the disk that you want to be formatted for media. Use full disk names.")
            temp = input("> ")
            print("If I am hearing you right, you selected:")
            print(temp)
            print("to format as a media drive. Is this correct? [y/N]")
            if input("> ").lower() == "y":
                media_drives.append(temp)
            print("Any more drives I should format? [y/N]")
            if input("> ").lower() != "y":
                break
    os.system('clear')
    print("Now, I need to give your device a name. Please provide a hostname.")
    while True:
        hostname_ans = input("HOSTNAME: ")
        print(f"Your hostname is: {hostname_ans}. Is this right? [Y/n]")
        if input("> ").lower() != "n":
            break
    print("Assuming locale is in UTF-8...")
    time.sleep(5)
    while True:
        os.system("clear")
        print("TIMEZONE\n")
        print("Now, timezones. I need to make sure that the time is actually the time. Please input a timezone in tz format (Region/City). See en.wikipedia.org/wiki/List_of_tz_database_time_zones for more details. A list is under the List heading.")
        time_zone = input("> ")
        print(f"Timezone selected: {time_zone}. Is this correct? [Y/n]")
        if input("> ").lower() != "n":
            break
    print("Outside Access via NordVPN MeshNet\n")
    print("All preliminary questions are done. Now, one last question:")
    print("Are you planning to access the server from outside your home? This relies on NordVPN MeshNet and needs an account. [y/N]")
    if input("> ").lower() == "y":
        print("Added NordVPN MeshNet to install list.")
        is_meshnet = True
    os.system('clear')
    print("Fun fact: It actually is a serious security risk to always use the root account for everything. In order to mitigate this, I will create a user account for you. Please provide a username for the account.")
    while True:
        username = input("> ")
        print(f"Your username is: {username}. Is this right? [Y/n]")
        if input("> ").lower() != "n":
            break
    os.system('clear')
    print("REVIEW\n")
    print("These are your settings:")
    print(f"""EFI:            {is_efi} ({efi_type} bits)
Install Disk:   {disk_to_install}
Media Disks:    {media_drives}
Hostname:       {hostname_ans}
Time Zone:      {time_zone}
MeshNet:        {is_meshnet}
Username:       {username}""")
    print("Do you want to install?")
    print("Beware, as once you do this, it is IRREVERSIBLE.")
    print("[y/n]")
    while True:
        ans = input("> ")
        if ans.lower() == "y":
            print("ARE YOU SURE YOU WANT TO INSTALL? YOU WILL BE UNABLE TO ACCESS YOUR OLD OS AFTER THIS. TYPE 'YES I WANT TO INSTALL' IN ALL CAPS TO CONTINUE.")
            if input("> ") == "YES I WANT TO INSTALL":
                install_arch()
                print(f"Done Installing! Reboot the system and log in with '{username}' and the password you set during installation. Jellyfin should start automatically on boot and should be accessible from http://localhost:8096 or http://<your-ip>:8096 If it doesn't, run '/home/{username}/jellyfin_startup.sh' to start it.")
                quit()
            else:
                print("Cancelling install...")
                quit()
        elif ans.lower() == "n":
            print("Cancelling install...")
            quit()
        else:
            print("Please provide an answer.")
def install_arch():
    os.system("clear")
    print("INSTALL PART 1/3: BASE\n")
    print("""Summary of this section:
1. Disk partitioning
2. Formatting partitions
3. Mounting partitions
4. Installing base system
5. Generating fstab""")
    print("Installing parted...")
    subprocess.call(["pacman", "-Syy", "parted"])
    if is_efi:
        print("Installed. Partitioning {disk_to_install} as efi...")
        print("    [1/5] Label Creation (GPT)")
        subprocess.call(["parted", "-s", disk_to_install, "mklabel", "gpt"])
        print("    [2/5] Partitioning boot partition...")
        subprocess.call(["parted", "-s", "-a", disk_to_install, "mkpart", "primary", "fat32", "0M", "500MiB"])
        print("    [3/5] Making swap partition...")
        subprocess.call(["parted", "-s", "-a", disk_to_install, "mkpart", "primary", "linux-swap", "500MiB", "8.5GiB"])
        print("    [4/5] Making root partition...")
        subprocess.call(["parted", "-s", "-a", disk_to_install, "mkpart", "primary", "ext4", "8.5GiB", "100%"])
        print("    [5/5] Listing partition table...")
        os.system("lsblk")
        print("DONE PARTITIONING INSTALL DRIVE")
    else:
        print("Placeholder")
    for drive in media_drives:
        print(f"Formatting {drive} as NTFS...")
        print("    [1/2] Label Creation (GPT)")
        subprocess.call(["parted", "-s", drive, "mklabel", "gpt"])
        print("    [2/2] Formatting partition as NTFS")
        subprocess.call(["parted", "-s", "-a", drive, "mkpart", "primary", "ntfs", "0%", "100%"])
        print(f"DONE PARTITIONING MEDIA DRIVE {drive.upper()}")
    print("Formatting partitions...")
    if is_efi:
        print("    ROOT: ", end="")
        _ = os.system(f"mkfs.ext4 {disk_to_install}3")
        print("OK")
        print("    SWAP: ", end="")
        _ = os.system(f"mkswap {disk_to_install}2")
        print("OK")
        print("    BOOT: ", end="")
        _ = os.system(f"mkfs.fat -F32 {disk_to_install}1")
        print("OK")
    print("Formatting media drives...")
    for drive in media_drives:
        print(f"    {drive.upper()}: ", end="")
        _ = os.system(f"mkfs.ntfs -f {drive}1")
        print("OK")
    print("DONE FORMATTING PARTITIONS")
    
    print("Mounting...")
    if is_efi:
        print("    ROOT: ", end="")
        _ = os.system(f"mount {disk_to_install}3 /mnt")
        print("OK")
        print("    SWAP: ", end="")
        _ = os.system(f"swapon {disk_to_install}2")
        print("    BOOT: ", end="")
        _ = os.system(f"mount --mkdir {disk_to_install}1 /mnt/boot")
        print("OK")
    print("Initiating install of base system...")
    install_process = subprocess.Popen(["pacstrap", "-K", "/mnt", "base", "linux", "base-devel", "linux-firmware", "networkmanager", "wpa_supplicant"], stdout=subprocess.PIPE, shell=True)

    (output, err) = install_process.communicate()
    
    _ = install_process.wait()

    if install_process.returncode != 0:
        print("CRITICAL ERROR: Something has gone wrong during the installation of the base system. The error code is:", install_process.returncode)
        print("Debug details:")
        print(err)
        print("I cannot continue with the installation. Sometimes this is because of a network error, so please check your connection and try again.")
        quit()

    print("DONE INSTALLING")
    print("Generating fstab...")
    os.system("genfstab -U /mnt >> /mnt/etc/fstab")
    print("DONE")
    time.sleep(2)
    os.system("clear")
    print("INSTALL PART 2/3: SYSTEM CONFIG\n")
    print("""Summary of this section:
1. Setting time zone
2. Setting up locales
3. Setting hostname
4. Setting root password
5. Installing bootloader
6. Enabling NetworkManager
7. Making user account
8. Adding user to docker group""")
    
    print("Setting time zone...")
    os.system(f"ln -sf /usr/share/zoneinfo/{time_zone} /etc/localtime")
    os.system("hwclock --systohc")
    print("DONE SETTING TIME ZONE")
    print("Setting up locales...")
    print("    [1/3] Uncommenting en_US.UTF-8 UTF-8 in locale.gen...")
    locale_gen_text = ""
    with open("/mnt/etc/locale.gen", "r") as localegen:
        locale_gen_text = localegen.read()
        localegen.close()
    locale_gen_text = locale_gen_text.replace("#en_US.UTF-8 UTF-8", "en_US.UTF-8 UTF-8")
    with open("/mnt/etc/locale.gen", "w") as localegen:
        localegen.write(locale_gen_text)
        localegen.close()
    print("   [2/3] Generating locales...")
    subprocess.call(["arch-chroot", "/mnt", "locale-gen"])
    print("   [3/3] Setting LANG...")
    with open("/mnt/etc/locale.conf", "w") as localeconf:
        localeconf.write("LANG=en_US.UTF-8")
        localeconf.close()
    print("DONE SETTING UP LOCALES")
    print("Making hostname...")
    with open("/mnt/etc/hostname", "w") as hostname_file:
        hostname_file.write(hostname_ans)
        hostname_file.close()
    print("For security, we didn't ask for a root password during setup. We will allow you to type it directly into the command itself.")
    subprocess.call(["arch-chroot", "/mnt", "passwd"])
    print("INSTALLING BOOTLOADER")
    print("    [1/2] Installing GRUB...")
    subprocess.call(["arch-chroot", "/mnt", "pacman", "-Syy", "grub"])
    if is_efi:
        subprocess.call(["arch-chroot", "/mnt", "pacman", "-Syy", "efibootmgr"])
        if efi_type == 64:
            subprocess.call(["arch-chroot", "/mnt", "grub-install", "--target=x86_64-efi", "--efi-directory=/boot", "--bootloader-id=GRUB"])
        elif efi_type == 32:
            subprocess.call(["arch-chroot", "/mnt", "grub-install", "--target=i386-efi", "--efi-directory=/boot", "--bootloader-id=GRUB"])
    else:
        print("placeholder")
    print("    [2/2] Generating GRUB config...")
    subprocess.call(["arch-chroot", "/mnt", "grub-mkconfig", "-o", "/boot/grub/grub.cfg"])
    print("DONE INSTALLING BOOTLOADER")
    print("Enabling NetworkManager...")
    subprocess.call(["arch-chroot", "/mnt", "systemctl", "enable", "NetworkManager"]) # no need to enable it now as it is already enabled in the base system
    print("NETWORKMANAGER ENABLED")
    print("Making user account...")
    subprocess.call(["arch-chroot", "/mnt", "useradd", "-m", "-G", "wheel", username])
    print(f"User account created. I can't make passwords for you, so you will have to do that yourself. I am running passwd {username}. Please make it different from the root password. If its the same, it pretty much negates the security benefits.")
    subprocess.call(["arch-chroot", "/mnt", "passwd", username])
    print("ADDING USER TO DOCKER GROUP")
    subprocess.call(["arch-chroot", "/mnt", "usermod", "-aG", "docker", username]) # Add user to docker group
    # no need for visudo since docker group already is root equivalent
    print("USER ADDED TO DOCKER GROUP")
    print("\nDONE INSTALLING ARCH LINUX BASE")
    time.sleep(5)
    os.system("clear")
    print("INSTALL PART 3/3: JELLYFIN\n")
    print("Installing Docker...")
    subprocess.call(["arch-chroot", "/mnt", "pacman", "-Syy", "docker"])
    print("DOCKER INSTALLED")
    print("Enabling Docker service...")
    subprocess.call(["arch-chroot", "/mnt", "systemctl", "enable", "--now", "docker"])
    print("DOCKER SERVICE ENABLED")
    print("Installing Jellyfin...")
    subprocess.call(["arch-chroot", "/mnt", "docker", "pull", "jellyfin/jellyfin"])
    subprocess.call(["arch-chroot", "/mnt", "docker", "volume", "create", "jellyfin-config"])
    subprocess.call(["arch-chroot", "/mnt", "docker", "volume", "create", "jellyfin-cache"])
    print("Jellyfin pulled.")
    print("Since this entire script is dedicated to installing Arch Linux and Jellyfin, I will add a startup script to run the jellyfin container on boot.")

    with open(f"/mnt/home/{username}/jellyfin_startup.sh", "w") as startup_script_file:
        startup_script_file.write(startup_script)
        startup_script_file.close()
    print("Marking script as executable...")
    os.system(f"chmod +x /mnt/home/{username}/jellyfin_startup.sh")
    print("Script marked as executable.")
    print("Adding script to bashrc...")
    os.system(f"echo '~/jellyfin_startup.sh' >> /mnt/home/{username}/.bashrc")
    print("Script added to bashrc.")
    print("DONE INSTALLING JELLYFIN")
    time.sleep(5)
    if is_meshnet:
        print("Installing yay...")
        subprocess.call(["arch-chroot", "/mnt", "git", "clone", "https://aur.archlinux.org/yay.git"])
        _ = os.system("arch-chroot /mnt pacman -S --needed git base-devel && git clone https://aur.archlinux.org/yay.git && cd yay && makepkg -si")
        print("yay installed.")
        print("Installing NordVPN MeshNet...")
        subprocess.call(["arch-chroot", "/mnt", "pacman", "-Syy", "nordvpn-bin"])
        print("NordVPN MeshNet installed.")
        print("Enabling NordVPN service...")
        subprocess.call(["arch-chroot", "/mnt", "systemctl", "enable", "--now", "nordvpnd"])
        print("NordVPN service enabled.")
        print("Please run 'nordvpn login' to log in to your account and 'nordvpn meshnet on' to enable MeshNet. You can do this after the installation is complete.")

welcome(2)
init_install()
questions()
