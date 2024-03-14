#!/bin/bash

# Define variables for directory paths
VM_DIR="/home/dev/VMM/win11/"
# Conectar mediante RDP
wlfreerdp /u:$rdpuser /p:$rdppass /v:localhost /drive:Linux,/home/dev/VMM/win11 /size:1920x1080

# Verificar el código de salida de FreeRDP
if [ $? -ne 0 ]; then
  echo "Error: Failed to establish RDP connection."
  exit 1
fi
