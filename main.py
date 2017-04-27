#!/usr/bin/python3
import os
import sys

import nibabel
from PyQt5 import uic
from PyQt5.QtGui import QBrush, QColor, QPen
from PyQt5.QtWidgets import QApplication, QFileDialog, QGraphicsScene, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('mainwindow.ui', self)

        self.sliders = [self.image_slider_0, self.image_slider_1, self.image_slider_2]
        self.viewers = [self.image_viewer_0, self.image_viewer_1, self.image_viewer_2]
        self.action_open.triggered.connect(self.openFile)
        self.setWindowTitle('Nifti viewer')
        self.show()

        for i, slider in enumerate(self.sliders): slider.valueChanged.connect(lambda value: self.drawViewer(i))

    def openFile(self):
        fileInfo = QFileDialog.getOpenFileName(parent=self, directory=os.path.expanduser('~'), filter='*.nii *.nii.gz')
        if not os.path.isfile(fileInfo[0]): return

        self.niba_img = nibabel.load(fileInfo[0])
        data = self.niba_img.get_data()

        for i, slider in enumerate(self.sliders):
            slider.setMaximum(data.shape[i] - 1)
            slider.setValue(0)

        for i, viewer in enumerate(self.viewers):
            self.drawViewer(i)

        print(self.niba_img.header)

    def drawViewer(self, num_slider: int):
        data = self.niba_img.get_data()
        if data is None: return

        r = (self.sliders[0].value(), slice(None), slice(None))
        if len(data.shape) == 4: r = r + (0,)

        plane = data[r]
        scene = QGraphicsScene(0, 0, len(plane), len(plane[0]))

        for i, arr in enumerate(plane):
            for j, val in enumerate(arr):
                grey = int((val + 2048) / 16)
                scene.addRect(i, 6 * j, 1, 6, QPen(QColor(grey, grey, grey, 0xff)),
                              QBrush(QColor(grey, grey, grey, 0xff)))

        self.viewers[0].setScene(scene)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())
