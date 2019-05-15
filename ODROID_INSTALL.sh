sudo apt update
sudo apt -y install git python3-pip python3-setuptools mercurial python3-dev python3-numpy libsdl-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libportmidi-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libportmidi-dev libfreetype6-dev libconfuse-dev libboost-all-dev libusb-1.0-0-dev doxygen swig python3-opencv v4l-utils
cd /home/$USER/Documents
hg clone https://bitbucket.org/pygame/pygame
cd pygame
python3 setup.py build
sudo python3 setup.py install
sudo -H pip3 install Adafruit-GPIO
cd /home/$USER/Documents
wget https://www.intra2net.com/en/developer/libftdi/download/libftdi1-1.3.tar.bz2
tar xvf libftdi1-1.3.tar.bz2
cd libftdi1-1.3
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX="/usr/" -DPYTHON_INCLUDE_DIR="/usr/include/python3.6" -DPYTHON_LIBRARIES="/usr/lib/python3.6/" ../
make
sudo make install
sudo -H pip3 install Adafruit-blinka
sudo -H pip3 install Adafruit-PCA9685
sudo mv /usr/local/lib/python3.6/dist-packages/Adafruit-GPIO/FT232H.py /usr/local/lib/python3.6/dist-packages/Adafruit-GPIO/FT232H.py.old
sudo rm /usr/local/lib/python3.6/dist-packages/Adafruit-GPIO/FT232H.py
sudo curl https://gist.githubusercontent.com/BlueNalgene/f2324cbb7bd9b3060b46ebcaaf7d8a15/raw/4a5fdfc4f0a064d2b7a8a75724b49a78662af108/gistfile1.txt > FT232H.py
cd /home/$USER/Documents
git clone --recursive https://github.com/hardkernel/WiringPi2-Python
cd WiringPi2-Python
sudo python3 setup.py
cd ../
sudo rm -r /home/$USER/Documents/libftdi1-1.3
sudo rm -r /home/$USER/Documents/pygame
sudo rm -r /home/$USER/Documnets/WiringPi2-Python
rm /home/$USER/Documents/libftdi1-1.3.tar.bz2
sudo chown odroid /dev/gpiomem
sudo chmod g+rw /dev/gpiomem
