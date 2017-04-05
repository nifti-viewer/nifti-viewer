#!/usr/bin/python3
import os
import sys

import nibabel
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('mainwindow.ui', self)

        self.sliders = [self.image_slider_0, self.image_slider_1, self.image_slider_2]
        self.action_open.triggered.connect(self.openFile)
        self.setWindowTitle('Nifti viewer')
        self.show()

    def openFile(self):
        fileInfo = QFileDialog.getOpenFileName(parent=self, directory=os.path.expanduser('~'), filter='*.nii *.nii.gz')

        if not os.path.isfile(fileInfo[0]): return

        nb_img = nibabel.load(fileInfo[0])
        data = nb_img.get_data()

        for i, slider in enumerate(self.sliders):
            slider.setMaximum(data.shape[i])
            slider.setValue(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())
