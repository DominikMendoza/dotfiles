#!/bin/bash

# Find the process ID of the virtual machine
VM_PROCESS_ID=$(pgrep -f "qemu-system-x86_64")

# Check if the virtual machine is running
if [ -n "$VM_PROCESS_ID" ]; then
  # Stop the virtual machine
  kill "$VM_PROCESS_ID"

  # Check if it stopped successfully
  if [ $? -eq 0 ]; then
    echo "The virtual machine has been stopped successfully."
  else
    echo "Error stopping the virtual machine."
  fi
else
  echo "No running instance of the virtual machine was found."
fi
