# CNC14Camera
A simple camera tool for the CNC14 machine (https://www.cnc14.de) which was designed by
Birgit Hellendahl.
However, you may use this tool for any other CNC machine as well.

The purpose of this tool is to zero the XY-coordinates of a CNC machine.
It permanently displays the image grabbed from a video device, e.g. a camera
plugged into an USB port. The image contains a red cross indicating the X-
and Y-axis of the machine. The center of the cross is a green circle, the radius
of which can be adjusted with a slide control next to the resolution
combo-box-button.
By clicking on the image it is possible to setup some parameters which are
used by default. In the first line you can choose the camera device if there
are several ones attached to the computer.
The next line rotates the red cross in order to match the actual X-
and Y-axis of the machine. In addition the camera parameters, like brightness,
contrast and saturation, can be adjusted as well.
All of the slider values as well as the current resolution and the current
device are stored in user's settings and will be restored at the next start.


![image](CNC14Camera.png "Default view")
![image](CNC14Camera_setup.png "Setup view")

# Prerequisites
This program is a python3-script using the modules PyQt5,cv2,math,numpy and
platform.

Usage: Just run the python script without any parameters in your favorite way.

Installed python:<br>
Linux: /usr/bin/python3 CNC14Camera.py<br>
Windows 10/11: double click on CNC14Camera.py<br>

Windows 7: Since Windows 7 is not supported anymore, you need to install an
older version of python (tested Python 3.8.9 https://www.python.org/ftp/python/3.8.9/python-3.8.9.exe).


# Single executables
You may want to have a single executable so that you don't have to take care
about installing python3 and the required modules - especially on computers
using Windows.
You can do this by using PyInstaller on a machine with all of the
prerequisites and PyInstaller (pip install pyinstaller)
1. open command shell
2. create a new directory, e.g. by "mkdir cam_distrib", and copy the python
   script CNC14Camera.py into it
3. change into this directory by "cd cam_distrib"
4. call "PyInstaller --onefile CNC14Camera.py"

Afterwards the single executable is located in the sub-directory "dist". 
It contains a python interpreter and all of the required modules so that
the executable may be run on computers which don't have python installed

**NOTE**: There have been newer versions of PyInstaller and OpenCV (cv2) which
      are currently incompatible. A known working combination is:
      opencv-python: 4.5.5.64
      pyinstaller: 5.2

      you may check your current version by:
        pip show opencv-python pyinstaller

      if you have newer version installed, you may override them by
        pip install --ignore-installed opencv-python==4.5.5.64
        pip install --ignore-installed pyinstaller==5.2

This procedure works for Windows machines as well as for MacOS machines
and for Linux machines. However, the executables only run on machines
using the same OS - or at least very similar. This means that Linux-
executables build on a specific distribution may not run on a different
Linux distribution.

The bin-directory already contains a compiled single executable for
Windows (build on Win7 32-bit and Python 3.8.9) and MacOS (camera access may be required for terminal).

# FAQ
**Q**: My camera does not show up in the camera-menu anymore. How can I fix it?

**A**: At the first start, all found cameras are put into the menu and some default settings are used.
   When the program exits, the settings and the used camera are stored in the registry (Windows registry:
   Computer\HKEY_CURRENT_USER\Software\CNC14Camera) or in a config-file (e.g. .config/CNC14Camera/CNC14Camera.conf
   on Ubuntu-Linux). On MacOS the config-file is located at $HOME/Library/Preferences/com.cnc14camera.CNC14Camera.plist.
   When the camera-software is run again, the settings of the config-file are applied. If the device
   for the camera does not match exactly, it is ignored. This may happen if the order of USB devices has
   changed, e.g. if you have added a new USB device or removed one.
   In that case please delete the config file or delete the registry entry with the registry editor on
   Windows.
