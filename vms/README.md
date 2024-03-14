# Virtual Machine Setup for Windows 11 with QEMU

## Prerequisites
- Downloaded [Windows 11 ISO file](https://www.microsoft.com/software-download/windows11) (`Win11_23H2_English_x64v2.iso`).
- Downloaded [Virtio drivers ISO file](https://github.com/virtio-win/virtio-win-pkg-scripts/blob/master/README.md) (`virtio-win.iso`).

## Dependencies
- ovmf
- qemu
- libtpms0
- swtpm
- freerdp2-wayland or freerdp2-x11

## Setup Instructions

### 1. Create a custom directory and copy OVMF files
```bash
# Set your custom directory path
custom_directory="/home/dev/VMM/win11/"

# Copy OVMF files to the custom directory
cp /usr/share/OVMF/OVMF_VARS.fd "$custom_directory"
cp /usr/share/OVMF/OVMF_CODE.fd "$custom_directory"
```
These commands copy the OVMF files that we need.

### 2. Create Virtual Disk
```bash
# Set your virtual disk path
virtual_disk_path="/home/dev/VMM/win11/windisk.qcow2"

qemu-img create -f qcow2 "$virtual_disk_path" 250G
```
This command creates a virtual disk `windisk.qcow2` with a size of 250 GB.

### 3. Create TPM Socket
```bash
# Set your TPM socket directory path
tpm_socket_directory="/home/dev/VMM/win11/"

swtpm socket --tpmstate dir="$tpm_socket_directory" --ctrl type=unixio,path="$tpm_socket_directory/swtpm-sock" --tpm2 &
```
This command sets up a TPM socket necessary for TPM emulation.

### 4. Run QEMU with TPM Configuration
```bash
# Set your ISO files paths
iso_path="/home/dev/VMM/win11/"
win11_iso="$iso_path/Win11_23H2_English_x64v2.iso"
virtio_iso="$iso_path/virtio-win-0.1.248.iso"

qemu-system-x86_64 \
  --enable-kvm \
  -m 12G \
  -M q35 \
  -cpu host \
  -smp 8 \
  -drive "if=pflash,format=raw,readonly=on,file=$custom_directory/OVMF_CODE.fd" \
  -drive "if=pflash,format=raw,file=$custom_directory/OVMF_VARS.fd" \
  -chardev socket,id=chrtpm,path="$tpm_socket_directory/swtpm-sock" \
  -tpmdev emulator,id=tpm0,chardev=chrtpm \
  -device tpm-tis,tpmdev=tpm0 \
  -drive file="$virtual_disk_path",index=0,media=disk,if=virtio,cache=unsafe \
  -rtc base=localtime \
  -vga virtio \
  -drive file="$win11_iso",media=cdrom \
  -drive file="$virtio_iso",media=cdrom \
```

- `-m 12G`: Allocates 12 GB of RAM for the virtual machine.
- `-smp 8`: Utilizes 8 CPU cores for the virtual machine.
- `-chardev socket,id=chrtpm,path=/home/dev/VMM/win11/swtpm-sock -tpmdev emulator,id=tpm0,chardev=chrtpm -device tpm-tis,tpmdev=tpm0`: Enables TPM support.
- `-drive file=windisk.qcow2,index=0,media=disk,if=virtio,cache=unsafe`: Attaches the virtual disk to the VM using Virtio interface.
- `-rtc base=localtime`: Uses the local time as the base for the real-time clock (RTC) of the virtual system.

### 5. Use RDP
```bash
# In this case we do not need to place the Windows cdrom or the virtio drivers separately.
qemu-system-x86_64 \
  --enable-kvm \
  -m 12G \
  -M q35 \
  -cpu host \
  -smp 8 \
  -drive "if=pflash,format=raw,readonly=on,file=$custom_directory/OVMF_CODE.fd" \
  -drive "if=pflash,format=raw,file=$custom_directory/OVMF_VARS.fd" \
  -chardev socket,id=chrtpm,path="$tpm_socket_directory/swtpm-sock" \
  -tpmdev emulator,id=tpm0,chardev=chrtpm \
  -device tpm-tis,tpmdev=tpm0 \
  -drive file="$virtual_disk_path",index=0,media=disk,if=virtio,cache=unsafe \
  -rtc base=localtime \
  -vga virtio \
  -net nic,model=virtio-net-pci \
  -net user,hostfwd=tcp::3389-:3389 \
  -usb -usbdevice tablet
```

```bash
# Set your RDP user and password
rdp_user="your_username"
rdp_pass="your_password"
wlfreerdp /u:$rdp_user /p:$rdp_pass /v:localhost /drive:Linux,/home/dev/VMM/win11 /dynamic-resolution
```

### 6. Scripts
You can check the scripts folder where I prepare some to start/stop qemu and connect via rdp

## References
- LastDragon. "Instalar Windows 11 en QEMU y activar las remoteapps o WinApps en Linux". YouTube, 2023. [Video](https://www.youtube.com/watch?v=WhENXFkiOlI)
