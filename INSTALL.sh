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
	echo "git already installed..."
fi

if ! [ -x "$(command -v pip)" ]; then
	echo 'Installing pip' >&2
	sudo apt -y install python-pip
else
	echo "pip already installed..."
fi

if ! [ -x "$(command -v lshw)" ]; then
	echo 'Installing lshw' >&2
	sudo apt -y install lshw
else
	echo "lshw already installed..."
fi

# Scipy is required for some other array math
python -c 'import scipy'
if [ $? != '0' ]; then
	sudo apt -y install python-scipy
fi
echo "scipy is installed"

# # Optional, fim is used to view images in terminal and ssh
# if ! [ -x "$(command -v fim)" ]; thenif $? = 1; then
# 	echo 'Installing fim' >&2
# 	sudo apt -y install fim
# else
# 	echo "fim installed..."
# fi
# 
# # Optional, omxplayer is used to view videos in terminal.  Only available to RasPi
# if ! [ -x "$(command -v omxplayer)" ]; then
# 	echo 'Installing omxplayer' >&2
# 	sudo apt -y install omxplayer
# else
# 	echo "omxplayer installed..."
# fi
# 
# # Optional, imagemagick has millions of uses for image manipulation
# if ! [ -x "$(command -v identify)" ]; then
# 	echo 'Installing imagemagick' >&2
# 	sudo apt -y install imagemagick
# else
# 	echo "imagemagick installed..."
# fi








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
    if line:match("^#?%s*"..key.."=.*$") thenget_rgpio() {
      if test -e /etc/systemd/system/pigpiod.service.d/public.conf; then
        echo 0
      else
        echo 1
      fi
    }
EOF

if [ "$(get_rgpio)" -eq 1 ]; then
	mkdir -p /etc/systemd/system/pigpiod.service.d/
	cat > /etc/systemd/system/pigpiod.service.d/public.conf << EOF
  [Service]
  ExecStart=
  ExecStart=/usr/bin/pigpiod
EOF
	systemctl daemon-reload
	if systemctl -q is-enabled pigpiod ; then
		systemctl restart pigpiod
	fi
fi
		made_change=true

if not made_change; then
end
mv "$3.bak" "$3"
fi
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






# Checks to see if GPIO is enabled.  If not, it enables the GPIO
# This is also stolen from rasp-config
get_rgpio() {
	if test -e /etc/systemd/system/pigpiod.service.d/public.conf; then
		echo 0
	else
		echo 1
	fi
}

if [ "$(get_rgpio)" -eq 1 ]; then
	mkdir -p /etc/systemd/system/pigpiod.service.d/
	cat > /etc/systemd/system/pigpiod.service.d/public.conf << EOF
[Service]
ExecStart=
ExecStart=/usr/bin/pigpiod
EOF
	systemctl daemon-reload
	if systemctl -q is-enabled pigpiod ; then
		systemctl restart pigpiod
	fi
fi




# This checks if the correct permissions are set for the output stream of the camera
# If not, it corrects this.
if [[ "$(ls -l /dev/gpiomem)" != *'root gpio'* ]]; then
	echo "Setting correct permissions for RPi camera"
	sudo chown root.gpio /dev/gpiomem
	sudo chmod g+rw /dev/gpiomem
fi
echo "RPi camera permissions are set"


# Now that everything apt is set up, we begin checking the pip packages.
# Numpy is required for much of the array math
python -c 'import numpy'
if [ $? != '0' ]; then
	pip install numpy
fi
echo "numpy is installed"


# Install Pillow for Pillow
python -c 'import PIL'
if [ $? != '0' ]; then
	pip install pillow
fi
echo "pillow installed"


# Picamera is required to work with the picamera in imutils
python -c 'import picamera'
if [ $? != '0' ]; then
	pip install picamera
fi
echo "picamera is installed"


# Imutils is required to use picamera and opencv together
python -c 'import imutils'
if [ $? != '0' ]; then
	pip install imutils
fi
echo "imutils is installed"





# # This installs a bunch of dependencies for opencv. 
# # Note that it does not check for the packages,
# # nor does it report their installation.
# # This is because these are handled simply by apt.
# # The user will not interact with these things directly,
# # So telling the user about them is not necessary.
# 
# # zzzzzzzzzzzzz add to /etc/apt/sources.list
# 
# sudo apt -y install libgtk-3-dev
# sudo apt -y install libpng12-dev
# sudo apt -y install build-essential cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran python2.7-dev python3-dev
# 
# wget -O opencv.zip https://github.com/opencv/opencv/archive/3.4.1.zip
# unzip opencv.zip
# wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/3.4.1.zip
# unzip opencv_contrib.zip
# cd ~/opencv-3.4.1/
# mkdir build
# cd build
# cmake -D CMAKE_BUILD_TYPE=RELEASE \
# 	-D CMAKE_INSTALL_PREFIX=/usr/local \
# 	-D INSTALL_PYTHON_EXAMPLES=ON \
# 	-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.4.1/modules \
# 	-D BUILD_EXAMPLES=ON ..
# sudo sed -i -e 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/g' /etc/dphys-swapfile
# sudo /etc/init.d/dphys-swapfile stop
# sudo /etc/init.d/dphys-swapfile start
# make -j4
# sudo make install
# sudo ldconfig
# sudo sed -i -e 's/CONF_SWAPSIZE=1024/CONF_SWAPSIZE=100/g' /etc/dphys-swapfile
# sudo /etc/init.d/dphys-swapfile stop
# sudo /etc/init.d/dphys-swapfile start
# # 





# Set Up WiFi Access Point on Raspberry Pi
# First, download the required packages.
sudo apt -y install hostapd dnsmasq
# Ignore the wireless interface
sudo cat >> /etc/dhcpcd.conf << EOF
denyinterfaces wlan0
EOF
# Next, we set up a static IP for wlan0
sudo cat >> /etc/network/interfaces << EOF
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp

allow-hotplug wlan0
iface wlan0 inet static
    address 192.168.42.1
    netmask 255.255.255.0
    network 192.168.42.0
    broadcast 192.168.42.255
EOF
# Now we set up hostapd to act like an access point
sudo cat >> /etc/hostapd/hostapd.conf << EOF
interface=wlan0
driver=nl80211
ssid=RPiAccessPoint
hw_mode=g
channel=5
ieee80211n=1
wmm_enabled=1
ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_passphrase=raspberryBridge
rsn_pairwise=CCMP
EOF
# Note here that the password needs to be changed. I used wifi channel=5 for a reason.
# We tell hostapd to use the config we set up by uncommenting the DAEMON_CONF line and adding the path
sudo sed -i -e 's/\#DAEMON_CONF\=\"\"/DAEMON_CONF\=\"\/etc\/hostapd\/hostapd.conf\"/g' /etc/default/hostapd
# Let's now configure the dnsmasq program using:
sudo cat >> /etc/dnsmasq.conf << EOF
interface=wlan0 
listen-address=192.168.42.1
bind-interfaces 
server=8.8.8.8
domain-needed
bogus-priv
dhcp-range=192.168.42.100,192.168.42.200,24h
EOF
# Finish and reboot
sudo reboot
