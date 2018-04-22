# LunAero
LunAero is a hardware and software project using OpenCV to automatically track birds as they migrate in front of the moon.

More information as project develops.

Created by @BlueNalgene, working in the lab of @Eli-S-Bridge.

###### Installed from APT
# This is a list of programs installed from apt.  This will be formatted as an install scri$
sudo apt update
sudo apt -y install

# Essential
python-pip
python-opencv
python-pygame # see notes below

# Makes life easier
lshw
##fbi
fim ## better than fbi for ssh
pqiv
omxplayer

# Required before installing pygame
# uses the SDL Library
tar -xzvf SDL-1.2.14.tar.gz
cd SDL-1.2.14
./configure
sudo make all
sudo make install
## Edit: this may not be necessary.  Try instead:
sudo nano /etc/apt/sources.list
# uncomment the dev-src Raspbian link
sudo apt update
sudo apt install python-pygame

# I could not access GPIO without changing permissions
# To test this:
ls -l /dev/gpiomem
# The permissions should be:
# crw-rw---- 1 root gpio 244, 0 Dec 28 22:51 /dev/gpiomem
# If not, run:
sudo chown root.gpio /dev/giomem
sudo chmod g+rw /dev/gpiomem



###### Installed from PIP
# This is a list of packages installed from pip to make LunAero work.  It will be formatted$
sudo pip install

# Essential
numpy
picamera
pynput
imutils

# Deprecated
pygame

