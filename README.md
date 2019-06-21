![The first fully automated lunar bird tracker](https://i.imgur.com/jRGf8h6.jpg "The first fully automated lunar bird tracker")

# LunAero
LunAero is a hardware and software project using OpenCV to automatically track birds as they migrate in front of the moon.  This repository contains information related to the construction of LunAero hardware and the software required for running the moon tracking program.  Bird detection has "migrated" to a new repository at https://github.com/BlueNalgene/Birdtracker_LunAero.

Created by @BlueNalgene, working in the lab of @Eli-S-Bridge.

## Hardware Recommendations

- Computer (see notes)
- Camera (see notes)
- Motors (2)
- TB6612FNG motor controller
- 1/4" Acrylic (about 18"x24")
- 1/8" Acetal (about 3"x3")
- Screws and Wires

For best results, we recommend running this on a Linux computer with USB 3 slots.  For a low cost option, the ODROID N2 single board computer has been found to be effective.  The installation instructions in this README are based on that hardware.

A hard drive capable of storing data at high transfer rates is required.  This can take the form of USB 3 compliant memory device, the ODROID eMMC modules, or a SATA drive.  For cost reasons, we recommend the eMMC module, and have found it to be effective.

This installation uses a USB 3 CCD camera.  Customization can be made for other cameras which use other interfaces, such as a CSI MIPI port.  Feel free to contact the repo maintainer if you are interested in this and need some help implementing it.

A TB6612FNG breakout board is required to control two motors.  If you don't have one of these laying around (we made our own board in house), you can get them from Sparkfun https://www.sparkfun.com/products/14451.

This hardware implementation requires two low speed/high torque 5V motors.  We used 0.5 rpm motors purchased from Amazon (uxcell DC 5V 0.5RPM Worm Gear Motor 6mm Shaft High Torque Turbine Reducer).  If you change motors, be sure that the CAD designs match the drill holes required for the motor to attach to the plastic.

This project include designs for plastic parts to be cut from 1/4" acrylic plastic and 1/8" acetal plastic.  You can change these materials if you like.  E.g. it would be reasonable to swap the acetal for some of the 1/4" acyrlic if you are low on funds.  HOWEVER, the acetal makes much better gears and will give you much smoother motion.

You also need a bunch of bolts and screws and whatnot.  One of these days I will measure the ones I used and report back with numbers.

## Using the 2D CAD files

The CAD files in the 2D CAD folder are used to construct parts for LunAero including gears and mounting brackets.  The parts are designed to be cut on a laser CNC machine.  They can also be used as templates for cutting on a band saw or using another CNC machine.

The units are in mm for all parts.

Assembly information will be provided in the 2D CAD subfolder dedicated for that purpose.

### USB 3 and LunAero

Why is USB 3 so important?  The data lanes on USB 2 and below are too small for what we need.  In order to record and process footage at a high frame rate (~30 fps) and large image size (1920x1080), we need to move 187 Mb/s.  USB 2 is only capable of 60 Mb/s.  This means that if we try to record from a USB 2 connection, we will lose frames and data.  Eventually, the extra data we are trying to push through the small pipe will overrun (as our tests demonstrated empirically), and some major lag will occur in the tracking.  This has often caused early LunAero prototypes to lose the moon while attempting to track it.

## Software Install Instructions
When you install this for the first time on to a 'blank' ODROID N2, you will need to use `git` to pull this repository.  Then you can pull everything in and run it.  To do this, execute the lines in the terminal (ctrl+alt+t):
```
sudo apt update
sudo apt -y install git
git clone https://github.com/BlueNalgene/LunAero.git
cd LunAero
```

This script downloads the `git` program and then pulls in the repository posted here.  Once you have the repo on your N2, you go into the folder, then execute the install script.  This should take less than a minute on a modern internet connection.

```
sudo ./ODROID_INSTALL.sh
```

When the INSTALL script is executed, it will go through all of the dependencies you need for this program.  If you don't have them installed, it will do that for you.  Note that this **TAKES A LONG TIME**.  You have been warned.

When you are finished, you can copy the desktop file to the N2's desktop and you will be ready to go.

```
cp ./odroid_moontracker.desktop /home/odroid/Desktop
```

## Running LunAero

Double-click the desktop icon you made for LunAero.  This will open a window with a very simple graphical user interface.

### Time Confirmation

The first screen will ask you to check the time.  LunAero calculations are performed by referencing the system time of the computer you are using.  Check to see that the time displayed on the screen is accurate against another known source (e.g. your watch or phone).  If the time is correct, select `y` and you will move on to the next mode.  Otherwise, you will enter in the date and time for your location in the next series of prompts using 2 digit entries, pressing enter each time.  Example: If you were witness to the meteor impact on the moon which occurred on September 11th 2013 at 8:07:28 PM UTC, you would type:

```
13
[enter]
09
[enter]
11
[enter]
20
[enter]
07
[enter]
28
[enter]
```

Select the correct time zone.  The only available options right now are in North America.  For international users, please use UTC time.

This will not change the system time of your computer.  There are other ways to do that, and I won't go into them here.  This just tells LunAero what time you started recording.

### Manual Adjustment Mode

Once you have confirmed the time is correct in LunAero, you will enter the manual tracking mode.  This is a screen that shows a video feed from the camera in the top right corner of the screen.  You can move the scope around with arrow keys, and adjust some camera parameters.

Move the scope position such that it is looking at the moon.  There will be a red ellipse on drawn on the screen.  Try to get the size of the moon in the viewer to match that circle by adjusting the zoom of your scope.

Adjust the camera settings (mostly the "exposure" value) such that you are able to see all of the craters of the moon as crisp as possible, while making sure the view is not too dark.  Empirically, we found that this is an exposure setting between 5-100 units.  There is a special key that adjusts the settings to where I personally had the best results, and this makes for a good reference point.

Check the "computer vision" version of the image by pressing `v`.  This will show a black and white image in the lower right hand corner of the screen.  This is what LunAero "sees".  Make sure that it can see the entirety of the moon.  If the computer vision just shows part of what you can see in the normal view, you may have set the exposure too low.

### Automatic Mode

Once you are happy with the settings, press `Enter` or `r` to run the automatic mode.  Then step away.  Watch with joy and wonder as the scope automatically follows the moon as it moves across the sky.  LunAero is recording everything that happens in view of the scope now.  You can walk away from it and it will continue recording.  Be sure to check that the weather is good and you are in a secure location.  Members of the LunAero team are not responsible for anything that happens to your scope if left outside during inclement weather or sticky fingers.


## Bird Detection Software

As of June 21st, 2019, the software for tracking birds in video of the moon has been migrated to a new repository at https://github.com/BlueNalgene/Birdtracker_LunAero.  The repo now only contains the hardware information and the software required to run the moon tracking program and record video.
