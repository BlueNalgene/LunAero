![The first fully automated lunar bird tracker](https://i.imgur.com/jRGf8h6.jpg "The first fully automated lunar bird tracker")

# LunAero
LunAero is a hardware and software project using OpenCV to automatically track birds as they migrate in front of the moon.

More information as project develops.

Created by @BlueNalgene, working in the lab of @Eli-S-Bridge.

## Install Instructions
When you install this for the first time on to a 'blank' Raspberry Pi, you will need to enable `git` to pull this repository.  To do this, execute the lines in the terminal (ctrl+alt+t):
```
sudo apt update
sudo apt -y install git
git clone https://github.com/BlueNalgene/LunAero.git
cd LunAero
sudo chmod +x ./INSTALL.sh
./INSTALL.sh
```

This script downloads the `git` program and then pulls in the repository posted here.  Once you have the repo on your Raspberry Pi, you go into the folder, make the install file executable, then execute the install script.  This should take less than a minute on a modern internet connection.

When the INSTALL script is executed, it will go through all of the dependencies you need for this program.  If you don't have them installed, it will do that for you.  Note that this **TAKES A LONG TIME**.  You have been warned.

As there are updates to the LunAero version available (as more features become available to users), the install will change and get longer.  If you have already executed INSTALL.sh, you can safely execute it again to catch anything new that you might have missed the first time.

## The targeting reticle: `framechecker.py`

To make sure you have the moon in view when first starting the camera for the evening, use `framechecker.py`.  This program simply turns on a preview screen while you do some manual adjustment of the camera.  To prevent user error, it automatically quits after 10 minutes.  To finish before that, press any key.

To run it, use:
```
python framechecker.py
```

## Running `altsimple.py`

`altsimple.py` is a simple tracking program.  It is executed with the command
```
python altsimple.py
```

This program simply records a video (a raw h264 video, you will need `VLC` if you want to look at it), and takes snapshots every x seconds.  The value for x is written at the beginning of the program with the variable name `DELAY`.

There is currently no nice/clean/elegant way to exit this program.  To exit use **ctrl+c**

Presumably, it is dark outside when you are using this, and light pollution from the screen may be unwanted.  There is output in the terminal for debugging which tells you the direction that the motors are attempting to move the scope, but you may want to turn you screen off once you have it figured out.
