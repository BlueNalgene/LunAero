#!/bin/bash
# This is a simple bash script to install the dependencies for LunAero
#
# Instructions:
# sudo chmod +x INSTALL.sh
# ./INSTALL.sh
#
# Script written by Wesley T. Honeycutt

echo "Checking for and installing dependencies for LunAero"

# Always update your package manager
sudo apt update

if ! [ -x "$(command -v git)" ]; then
	echo 'Installing git (how did you get this file?)' >&2
	sudo apt -y install git
else
	echo "git installed..."
fi

if ! [ -x "$(command -v pip)" ]; then
	echo 'Installing pip' >&2
	sudo apt -y install python-pip
else
	echo "pip installed..."
fi

if ! [ -x "$(command -v lshw)" ]; then
	echo 'Installing lshw' >&2
	sudo apt -y install lshw
else
	echo "lshw installed..."
fi

# Optional, fim is used to view images in terminal and ssh
if ! [ -x "$(command -v fim)" ]; thenif $? = 1; then
	echo 'Installing fim' >&2
	sudo apt -y install fim
else
	echo "fim installed..."
fi

# Optional, omxplayer is used to view videos in terminal.  Only available to RasPi
if ! [ -x "$(command -v omxplayer)" ]; then
	echo 'Installing omxplayer' >&2
	sudo apt -y install omxplayer
else
	echo "omxplayer installed..."
fi

# Optional, imagemagick has millions of uses for image manipulation
if ! [ -x "$(command -v identify)" ]; then
	echo 'Installing imagemagick' >&2
	sudo apt -y install imagemagick
else
	echo "imagemagick installed..."
fi








# This checks if the camera is installed
# If so, it enables it via the raspi-config
# This bit of bash code is stolen from raspi-config

# The first part declares some variables and functions
CONFIG=/boot/config.txt

get_config_var() {
  lua - "$1" "$2" <<EOF
local key=assert(arg[1])
local fn=assert(arg[2])
local file=assert(io.open(fn))
local found=false
for line in file:lines() do
  local val = line:match("^%s*"..key.."=(.*)$")
  if (val ~= nil) then
    print(val)
    found=true
    break
  end
end
if not found then
  print(0)
end
EOF
}

set_config_var() {
  lua - "$1" "$2" "$3" <<EOF > "$3.bak"
local key=assert(arg[1])
local value=assert(arg[2])
local fn=assert(arg[3])
local file=assert(io.open(fn))
local made_change=false
for line in file:lines() do
  if line:match("^#?%s*"..key.."=.*$") then
    line=key.."="..value
    made_change=true
  end
  print(line)
end

if not made_change then
  print(key.."="..value)
end
EOF
mv "$3.bak" "$3"
}

# This is the meat.  It actually sets the appropriate stuff.
if [ ! -e /boot/start_x.elf ]; then
	whiptail --msgbox "Your firmware appears to be out of date (no start_x.elf). Please update"
	return 1
fi
sed $CONFIG -i -e "s/^startx/#startx/"
sed $CONFIG -i -e "s/^fixup_file/#fixup_file/"
set_config_var start_x 1 $CONFIG
CUR_GPU_MEM=$(get_config_var gpu_mem $CONFIG)
if [ -z "$CUR_GPU_MEM" ] || [ "$CUR_GPU_MEM" -lt 128 ]; then
	set_config_var gpu_mem 128 $CONFIG
fi

# This checks if the correct permissions are set for the output stream of the camera
# If not, it corrects this.
if [[ "$(ls -l /dev/gpiomem)" != *'root gpio'* ]]; then
	echo "Setting correct permissions for RPi camera"
	sudo chown root.gpio /dev/gpiomem
	sudo chmod g+rw /dev/gpiomem
else
	echo "RPi camera permissions are set"
fi

# Now that everything apt is set up, we begin checking the pip packages.
# Numpy is required for much of the array math
python -c 'import numpy'
if [ $? != '0' ]; then
	pip install numpy
else
	echo "numpy is installed"
fi

# Picamera is required to work with the picamera in imutils
python -c 'import picamera'
if [ $? != '0' ]; then
	pip install picamera
else
	echo "picamera is installed"
fi

# Imutils is required to use picamera and opencv together
python -c 'import imutils'
if [ $? != '0' ]; then
	pip install imutils
else
	echo "imutils is installed"
fi

# This installs a bunch of dependencies for opencv. 
# Note that it does not check for the packages,
# nor does it report their installation.
# This is because these are handled simply by apt.
# The user will not interact with these things directly,
# So telling the user about them is not necessary.

# zzzzzzzzzzzzz add to /etc/apt/sources.list

sudo apt -y install libgtk-3-dev
sudo apt -y install libpng12-dev
sudo apt -y install build-essential cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran python2.7-dev python3-dev

wget -O opencv.zip https://github.com/opencv/opencv/archive/3.4.1.zip
unzip opencv.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/3.4.1.zip
unzip opencv_contrib.zip
cd ~/opencv-3.4.1/
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D INSTALL_PYTHON_EXAMPLES=ON \
	-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.4.1/modules \
	-D BUILD_EXAMPLES=ON ..
sudo sed -i -e 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/g' /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
make -j4
sudo make install
sudo ldconfig
sudo sed -i -e 's/CONF_SWAPSIZE=1024/CONF_SWAPSIZE=100/g' /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
# 
