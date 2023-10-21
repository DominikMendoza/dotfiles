#!/bin/bash

# Root uwu
if [[ $EUID -ne 0 ]]; then
    echo "Este script debe ejecutarse como root."
    exit 1
fi

apt update

# packages 
apt install -y git stow bspwm sxhkd kitty rofi feh picom zsh

# clone dotfiles
git clone https://github.com/DominikMendoza/dotfiles ~/.dotfiles

# change directory
cd ~/.dotfiles

# in progress


# Finish install
echo "Install complete!" 