# Encrypting Your OpenRecall Data

A sensible option to protect your (potentially sensitive) OpenRecall data is to use an external storage device, such as a USB stick or SD card (for MacBook Pro or laptops) with real-time disk encryption enabled. On Windows, BitLocker can be used. On macOS, you can create an encrypted disk image. On Linux, LUKS can be used to encrypt the disk. Before encrypting/formatting your storage device, ensure you have backed up any important data as the process will erase all existing data on the device. The OpenRecall project or its maintainers are not responsible for any data that can be damaged or lost during the below process or due to the use of OpenRecall.

There are several benefits to using an encrypted disk for your OpenRecall data:
- **Privacy**: Your data is encrypted and can only be accessed with the correct password.
- **Security**: In the event of loss or theft, your data is protected.
- **Portability**: You can easily move your OpenRecall data between different devices (using the same encryption software).
- **Peace of Mind**: You can rest easy knowing your data is secure.
- **Physical Control**: You have full, physical, control over your data, unlike cloud storage solutions. If you take the disk out of your computer, your data is safe and offline.

We strongly recommend to choose a strong password for your encrypted disk. A strong password should be at least 12 characters long and contain a mix of uppercase and lowercase letters, numbers, and special characters.

## Requirements
- A recent USB stick or (micro) SD card with sensible read/write speeds

## Windows (BitLocker)
1. Insert your USB stick or SD card into your computer.
2. Open **File Explorer** and right-click on your USB stick or SD card.
3. Select **Turn on BitLocker**.
4. Choose **Use a password to unlock the drive** and enter a secure password.
5. Save your recovery key to a file or print it out (do not skip this step).
6. Choose **Encrypt used disk space only** (faster) or **Encrypt entire drive** (slower but more secure).
7. Select **Compatible mode** to use the drive on older versions of Windows.
8. Click **Start Encrypting**.
9. Wait for the encryption process to complete.
10. Create an OpenRecall folder on the encrypted disk.
11. Launch OpenRecall with the argument`--storage-path "<path to your OpenRecall folder on the encrypted disk>"`

## macOS (Encrypted Disk Image)
1. Insert your USB stick or SD card into your Mac.
2. Open **Disk Utility** from Applications > Utilities.
3. Click **File** > **New Image** > **Blank Image**.
4. Name your disk image and select a location (save it to your USB stick or SD card).
5. Choose a size for your disk image.
6. Set **Format** to **Mac OS Extended (Journaled)**.
7. Set **Encryption** to **128-bit AES encryption** and enter a secure password.
8. Set **Partitions** to **Single partition - GUID Partition Map**.
9. Set **Image Format** to **read/write**.
10. Click **Save** and wait for the disk image to be created.
11. Mount the disk image, and find its path in Finder by right-clicking on the disk image and selecting **Get Info**. The path is displayed next to **Where**.
12.  and launch OpenRecall with the argument `--storage-path "/Volumes/<name of your volume>"`.

## Linux (LUKS)
1. Insert your USB stick or SD card into your computer.
2. Open a terminal.
3. Install necessary tools (if not already installed): `sudo apt-get install cryptsetup`.
4. Unmount the drive if it is automatically mounted: `sudo umount /dev/sdX1` (replace `sdX1` with your actual device identifier).
5. Initialize the LUKS partition: `sudo cryptsetup luksFormat /dev/sdX1`.
6. Confirm the action and enter a secure password.
7. Open the LUKS partition: `sudo cryptsetup luksOpen /dev/sdX1 encrypted_drive`.
8. Create a filesystem on the encrypted partition: `sudo mkfs.ext4 /dev/mapper/encrypted_drive`.
9. Mount the encrypted partition: `sudo mount /dev/mapper/encrypted_drive /mnt`.
10. Launch OpenRecall with the argument `--storage-path "/mnt"`.
11.  To unmount and close the encrypted partition: `sudo umount /mnt` followed by `sudo cryptsetup luksClose encrypted_drive`.

