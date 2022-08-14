#!/usr/bin/python3

###############################################################################
#
# CNC14Camera.py
#
###############################################################################

# This is a rather simple tool for capturing a camera device via OpenCV in
#  python
#
# Author: Gerd Sussner (gerd@sussner.net)
#
# Some parts of the code have been inspired by several tutorials which I don't
# remember anymore. Thanks to everyone who is sharing such information.
#

from PyQt5 import QtGui
from PyQt5.QtWidgets import QComboBox, QWidget, QApplication, QLabel, QGridLayout, QPushButton, QSlider, QLayout
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QSettings
import numpy as np
import math
import platform

versionMajor = 1
versionMinor = 0
versionPatchLevel = 0

class CaptureThread(QThread):
    image_changed = pyqtSignal(np.ndarray)

    def __init__(self, cap):
        super().__init__()
        self.cap = cap

    def run(self):
        # capture from web cam in a stupid endless while-loop
        while 1:
            if self.cap.isOpened():
                ret, cv_img = self.cap.read()
                if ret:
                    self.image_changed.emit(cv_img)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("CNC14Camera","CNC14Camera")
        
        self.resIdx = self.settings.value("resolutionIndex")
        if not self.resIdx:
            self.resIdx = 0
        else:
            self.resIdx = int(self.resIdx)
        
        self.curDeviceIdx = -1
        self.angle = self.settings.value("rotation")
        if not self.angle:
            self.angle = 0
        else:
            self.angle = float(self.angle)
        self.radius = self.settings.value("radius")
        if not self.radius:
            self.radius = 5
        else:
            self.radius = int(self.radius)
        self.brightness = self.settings.value("brightness")
        if not self.brightness:
            self.brightness = 128 # range: 0,255
        else:
            self.brightness = int(self.brightness)
        self.contrast = self.settings.value("contrast")
        if not self.contrast:
            self.contrast = 36    # range: 0,127
        else:
            self.contrast = int(self.contrast)
        self.saturation = self.settings.value("saturation")
        if not self.saturation:
            self.saturation = 38  # range: 0,127
        else:
            self.saturation = int(self.saturation)
        self.lineWidth = self.settings.value("linewidth")
        if not self.lineWidth:
            self.lineWidth = 1
        else:
            self.lineWidth = int(self.lineWidth)

        self.deviceList = []
        self.deviceParams = []
        for idx in [0,1,2,3,4,5,6,7]:
            if platform.system() == "Windows":
              devCap = cv2.VideoCapture(idx,cv2.CAP_DSHOW)
            elif platform.system() == "Darwin":
              devCap = cv2.VideoCapture(idx)
            else:
              devCap = cv2.VideoCapture(idx,cv2.CAP_V4L)
            if devCap.isOpened():
                self.deviceList.append(idx)
                w = devCap.get(cv2.CAP_PROP_FRAME_WIDTH)
                h = devCap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                p = []
                p.append(w / h)
                p.append(devCap.get(cv2.CAP_PROP_BRIGHTNESS))
                p.append(devCap.get(cv2.CAP_PROP_CONTRAST))
                p.append(devCap.get(cv2.CAP_PROP_SATURATION))
                self.deviceParams.append(p)
                devCap.release()

        versionStr = "v"+str(versionMajor) + "." + str(versionMinor) + "." + str(versionPatchLevel)
        self.setWindowTitle("CNC14 Camera "+versionStr)
        self.keyPressEvent = self.keyPressEvent
        # create combobox for video device
        self.cbox_size = QComboBox()
        self.cbox_size.addItem("Res: 320")
        self.cbox_size.addItem("Res: 640")
        self.cbox_size.addItem("Res: 960")
        self.cbox_size.addItem("Res: 1280")
        self.cbox_size.setCurrentIndex(self.resIdx)
        # create label and slider for radius
        self.label_radius = QLabel("Radius")
        self.slider_radius = QSlider(Qt.Horizontal)
        self.slider_radius.setMinimum(2)
        self.slider_radius.setMaximum(50)
        self.slider_radius.setValue(self.radius)
        # create the label that holds the image
        self.image_label = QLabel()
        self.image_label.setMinimumSize(320,240)
        self.image_label.mousePressEvent = self.toggleSliders
        # create combobox for video device
        self.label_device = QLabel("Device")
        self.cbox_device = QComboBox()
        for x in self.deviceList:
            self.cbox_device.addItem("Camera "+str(x))
        self.label_device.setVisible(False)
        self.cbox_device.setVisible(False)
        # create label and slider for rotation angle
        self.label_rot = QLabel("Rotation")
        self.slider_rot = QSlider(Qt.Horizontal)
        self.slider_rot.setMinimum(-900)
        self.slider_rot.setMaximum(900)
        self.slider_rot.setValue(int(self.angle*10))
        self.value_rot = QLabel()
        self.value_rot.setText(str(self.angle))
        self.value_rot.setAlignment(Qt.AlignRight)
        self.label_rot.setVisible(False)
        self.slider_rot.setVisible(False)
        self.value_rot.setVisible(False)
        # create label and slider for brightness
        self.label_brightness = QLabel("Brightness")
        self.slider_brightness = QSlider(Qt.Horizontal)
        self.slider_brightness.setMinimum(0)
        self.slider_brightness.setMaximum(255)
        self.slider_brightness.setValue(int(self.brightness))
        self.value_brightness = QLabel()
        self.value_brightness.setText(str(self.slider_brightness.value()))
        self.value_brightness.setAlignment(Qt.AlignRight)
        self.label_brightness.setVisible(False)
        self.slider_brightness.setVisible(False)
        self.value_brightness.setVisible(False)
        # create label and slider for contrast
        self.label_contrast = QLabel("Contrast")
        self.slider_contrast = QSlider(Qt.Horizontal)
        self.slider_contrast.setMinimum(0)
        self.slider_contrast.setMaximum(127)
        self.slider_contrast.setValue(int(self.contrast))
        self.value_contrast = QLabel()
        self.value_contrast.setText(str(self.slider_contrast.value()))
        self.value_contrast.setAlignment(Qt.AlignRight)
        self.label_contrast.setVisible(False)
        self.slider_contrast.setVisible(False)
        self.value_contrast.setVisible(False)
        # create label and slider for saturation
        self.label_saturation = QLabel("Saturation")
        self.slider_saturation = QSlider(Qt.Horizontal)
        self.slider_saturation.setMinimum(0)
        self.slider_saturation.setMaximum(127)
        self.slider_saturation.setValue(int(self.saturation))
        self.value_saturation = QLabel()
        self.value_saturation.setText(str(self.slider_saturation.value()))
        self.value_saturation.setAlignment(Qt.AlignRight)
        self.label_saturation.setVisible(False)
        self.slider_saturation.setVisible(False)
        self.value_saturation.setVisible(False)

        # button for reset sliders
        self.resetButton = QPushButton("Reset")
        self.resetButton.setVisible(False)

        # create a vertical box layout and add the two labels
        grid = QGridLayout()
        self._grid = grid
        grid.addWidget(self.cbox_size,0,0,1,1)
        grid.addWidget(self.label_radius,0,2)
        grid.addWidget(self.slider_radius,0,1,1,1)
        grid.addWidget(self.image_label,1,0,1,3)
        grid.addWidget(self.label_device,2,0)
        grid.addWidget(self.cbox_device,2,1)
        grid.addWidget(self.resetButton,2,2)
        grid.addWidget(self.label_rot,3,0)
        grid.addWidget(self.slider_rot,3,1)
        grid.addWidget(self.value_rot,3,2)
        grid.addWidget(self.label_brightness,4,0)
        grid.addWidget(self.slider_brightness,4,1)
        grid.addWidget(self.value_brightness,4,2)
        grid.addWidget(self.label_contrast,5,0)
        grid.addWidget(self.slider_contrast,5,1)
        grid.addWidget(self.value_contrast,5,2)
        grid.addWidget(self.label_saturation,6,0)
        grid.addWidget(self.slider_saturation,6,1)
        grid.addWidget(self.value_saturation,6,2)
        grid.setColumnStretch(1,1)
        grid.setRowStretch(0,1)
        grid.setColumnMinimumWidth(2,50)
        # set the vbox layout as the widgets layout
        self.setLayout(grid)
        self.layout().setSizeConstraint(QLayout.SetFixedSize)

        # connect signals
        self.slider_radius.valueChanged.connect(self.radiusChange)
        self.slider_rot.valueChanged.connect(self.rotChange)
        self.slider_brightness.valueChanged.connect(self.brightnessChange)
        self.slider_contrast.valueChanged.connect(self.contrastChange)
        self.slider_saturation.valueChanged.connect(self.saturationChange)
        
        self.cbox_size.currentIndexChanged.connect(self.changeResolution)
        self.cbox_device.currentIndexChanged.connect(self.changeCamera)

        self.resetButton.clicked.connect(self.resetSliders)
 
        # finally set current resolution
        self.changeResolution(self.resIdx)


    def __del__(self):
        # shut down capture system
        if self.curDeviceIdx >= 0:
            self.curCap.release()

    def closeEvent(self, event):
        if self.curDeviceIdx >= 0:
            self.thread.quit()
        event.accept()
        # save current settings
        self.settings.setValue("deviceIndex",self.curDeviceIdx)
        self.settings.setValue("resolutionIndex",self.cbox_size.currentIndex())
        self.settings.setValue("radius",self.radius)
        self.settings.setValue("rotation",self.angle)
        self.settings.setValue("brightness",self.brightness)
        self.settings.setValue("contrast",self.contrast)
        self.settings.setValue("saturation",self.saturation)
        self.settings.setValue("linewidth",self.lineWidth)
        # enforce exit of program
        sys.exit(0)
        
        
    def showEvent(self,event):
        if self.curDeviceIdx < 0:
            devIdx = self.settings.value("deviceIndex")
            if not devIdx:
                devIdx = -1
            else:
                devIdx = int(devIdx)
            numDevices = len(self.deviceList)
            if numDevices > 0:
                if devIdx >= numDevices or devIdx < 0:
                    devIdx = 0
            self.openDevice(devIdx)
            event.accept()

    def keyPressEvent(self, event):
        k = event.key()
        if k == Qt.Key_Escape or k == Qt.Key_Q:
            self.thread.quit()
            event.accept()
            self.close()

    def openDevice(self, deviceListIdx):
        if self.curDeviceIdx >= 0:
            self.thread.quit()
            self.curCap.release()
            self.curDeviceIdx = -1

        numDevices = len(self.deviceList)
        if deviceListIdx >= 0 and deviceListIdx < numDevices:
            idx = self.deviceList[deviceListIdx]
            if platform.system() == "Windows":
              self.curCap = cv2.VideoCapture(idx,cv2.CAP_DSHOW)
            elif platform.system() == "Darwin":
              self.curCap = cv2.VideoCapture(idx)
            else:
              self.curCap = cv2.VideoCapture(idx,cv2.CAP_V4L)
            if self.curCap.isOpened():
                self.curDeviceIdx = deviceListIdx
                # create the video capture thread
                self.thread = CaptureThread(self.curCap)
                # connect its signal to the update_image slot
                self.thread.image_changed.connect(self.update_image)
                # start the thread
                self.thread.start()

    def changeCamera(self,deviceListIdx):
        self.openDevice(deviceListIdx)

    def changeResolution(self,resolutionIdx):
        if self.curDeviceIdx >= 0 and self.curDeviceIdx < len(self.deviceParams):
            aspect = self.deviceParams[self.curDeviceIdx][0]
        else:
            aspect = 1
        resolutions = [320,640,960,1280]
        w = resolutions[resolutionIdx]
        h = int(w/aspect)
        self.image_label.setFixedSize(w,h)
        self.adjustSize()

    def toggleSliders(self,event):
        flag = not self.label_device.isVisible()
        self.label_device.setVisible(flag)
        self.cbox_device.setVisible(flag)
        self.label_rot.setVisible(flag)
        self.slider_rot.setVisible(flag)
        self.value_rot.setVisible(flag)
        self.label_brightness.setVisible(flag)
        self.slider_brightness.setVisible(flag)
        self.value_brightness.setVisible(flag)
        self.label_contrast.setVisible(flag)
        self.slider_contrast.setVisible(flag)
        self.value_contrast.setVisible(flag)
        self.label_saturation.setVisible(flag)
        self.slider_saturation.setVisible(flag)
        self.value_saturation.setVisible(flag)
        self.resetButton.setVisible(flag)

    def radiusChange(self):
        self.radius = self.slider_radius.value()

    def rotChange(self):
        self.angle = self.slider_rot.value() / 10
        self.value_rot.setText(str(self.angle))

    def brightnessChange(self):
        self.brightness = self.slider_brightness.value()
        self.value_brightness.setText(str(self.slider_brightness.value()))
        self.curCap.set(cv2.CAP_PROP_BRIGHTNESS,self.brightness)

    def contrastChange(self):
        self.contrast = self.slider_contrast.value()
        self.value_contrast.setText(str(self.slider_contrast.value()))
        self.curCap.set(cv2.CAP_PROP_CONTRAST,self.contrast)

    def saturationChange(self):
        self.saturation = self.slider_saturation.value()
        self.value_saturation.setText(str(self.slider_saturation.value()))
        self.curCap.set(cv2.CAP_PROP_SATURATION,self.saturation)
        
    def resetSliders(self):
        self.slider_rot.setValue(0)
        self.slider_brightness.setValue(128)
        self.slider_contrast.setValue(36)
        self.slider_saturation.setValue(38)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        # Updates the image_label with a new opencv image
        
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        # Convert from an opencv image to QPixmap
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        new_w = self.image_label.frameGeometry().width()
        new_h = self.image_label.frameGeometry().height()
        p = convert_to_Qt_format.scaled(new_w, new_h, Qt.KeepAspectRatio)

        aspect = self.deviceParams[self.curDeviceIdx][0]

        scl_w = new_w / w
        scl_h = new_h / h
        if scl_w > scl_h:
            new_w = int(new_h * aspect)
        else:
            new_h = int(new_w / aspect)
            
        xctr = new_w / 2
        yctr = new_h / 2
        lineLen = math.sqrt(new_w**2 + new_h**2) / 2
        angle = (self.angle / 180.0) * math.pi
        x0 = math.cos(angle) * self.radius
        y0 = math.sin(angle) * self.radius
        x1 = math.cos(angle) * lineLen
        y1 = math.sin(angle) * lineLen

        qp = QPainter(p)
        pen = QPen()
        pen.setWidth(self.lineWidth)
        pen.setColor(Qt.red)
        qp.setPen(pen)
        qp.drawLine(int(xctr+x0+self.lineWidth),int(yctr-y0),int(xctr+x1),int(yctr-y1))
        qp.drawLine(int(xctr-x0-self.lineWidth),int(yctr+y0),int(xctr-x1),int(yctr+y1))
        qp.drawLine(int(xctr+y0),int(yctr+x0-self.lineWidth),int(xctr+y1),int(yctr+x1))
        qp.drawLine(int(xctr-y0),int(yctr-x0+self.lineWidth),int(xctr-y1),int(yctr-x1))
        pen.setColor(Qt.green)
        qp.setPen(pen)
        qp.drawEllipse(int(xctr-self.radius),int(yctr-self.radius),self.radius*2,self.radius*2)
        qp.end()
        return QPixmap.fromImage(p)
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())

