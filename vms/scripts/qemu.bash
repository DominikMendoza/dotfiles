#!/bin/bash

# Define variables for directory paths
VM_DIR="/home/dev/VMM/win11/"
VM_SWTPM_SOCK="${VM_DIR}swtpm-sock"
VM_OVMF_VARS="${VM_DIR}OVMF_VARS.fd"
VM_OVMF_CODE="${VM_DIR}OVMF_CODE.fd"
VM_WINDISK="${VM_DIR}windisk.qcow2"

# Rm
rm "${VM_DIR}tpm2-00.permall" &
# Activar TMP
swtpm socket --tpmstate dir="$VM_DIR" --ctrl type=unixio,path="$VM_SWTPM_SOCK" --tpm2 &

# Qemu
(qemu-system-x86_64 \
  --enable-kvm \
  -m 12G \
  -M q35 \
  -cpu host \
  -smp 8 \
  -drive "if=pflash,format=raw,readonly=on,file=$VM_OVMF_CODE" \
  -drive "if=pflash,format=raw,file=$VM_OVMF_VARS" \
  -chardev socket,id=chrtpm,path="$VM_SWTPM_SOCK" \
  -tpmdev emulator,id=tpm0,chardev=chrtpm \
  -device tpm-tis,tpmdev=tpm0 \
  -drive file="$VM_WINDISK",index=0,media=disk,if=virtio,cache=unsafe \
  -rtc base=localtime \
  -vga none \
  -nographic \
  -net nic,model=virtio-net-pci \
  -net user,hostfwd=tcp::3389-:3389 \
  -usb -usbdevice tablet \
) &

# Record the process ID of the virtual machine
VM_PID=$!

# Check if the execution was successful
if [ $? -eq 0 ]; then
  echo "The virtual machine has been started successfully with PID $VM_PID."
else
  echo "Error starting the virtual machine."
fi
