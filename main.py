#!/usr/bin/python3
import os
import sys

import nibabel
import numpy
from PIL import Image
from PyQt5 import uic
from PyQt5.QtGui import QTransform
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtWidgets import QApplication, QFileDialog, QGraphicsScene, QMainWindow


class MainWindow(QMainWindow):
    niba_img = None
    num_image = -1
    image_min = 0
    image_max = 0

    def __init__(self):
        super().__init__()
        uic.loadUi('mainwindow.ui', self)

        self.image_sliders = [self.image_slider_0,
                              self.image_slider_1, self.image_slider_2]
        self.viewers = [self.image_viewer_0,
                        self.image_viewer_1, self.image_viewer_2]
        self.action_open.triggered.connect(self.open_file)
        self.setWindowTitle('Nifti viewer')
        self.show()

        self.image_sliders[0].valueChanged.connect(lambda value: self.draw_viewer(0))
        self.image_sliders[1].valueChanged.connect(lambda value: self.draw_viewer(1))
        self.image_sliders[2].valueChanged.connect(lambda value: self.draw_viewer(2))

        for viewer in self.viewers:
            viewer.setViewport(QGLWidget())

        self.image_cycle_slider.valueChanged.connect(self.cycle_images)

    def open_file(self):
        file_info = QFileDialog.getOpenFileName(parent=self, directory=os.path.expanduser('~'), filter='*.nii *.nii.gz')
        if not os.path.isfile(file_info[0]): return

        self.niba_img = nibabel.load(file_info[0])
        data = self.niba_img.get_data()
        self.image_min = data.min()
        self.image_max = data.max()

        if len(data.shape) == 4:
            self.num_image = 0
            self.image_cycle_slider.setMaximum(data.shape[3] - 1)

        for i, slider in enumerate(self.image_sliders):
            slider.setMaximum(data.shape[i] - 1)
            slider.setValue(0)

        for i, viewer in enumerate(self.viewers):
            self.draw_viewer(i)

    def draw_viewer(self, num_slider: int):
        data = self.niba_img.get_data()
        header = self.niba_img.get_header()
        if data is None: return

        slice_range = [slice(None)] * 3
        slice_range[num_slider] = self.image_sliders[num_slider].value()
        slice_range = tuple(slice_range)

        if len(data.shape) == 4: slice_range = slice_range + (self.num_image,)
        # TODO : integrate 4th slider for multiple images

        plane = data[slice_range]
        # minimum = plane.min()
        # maximum = plane.max()

        if self.image_min == self.image_max: self.image_max = 1

        converted = numpy.require(
            numpy.divide(numpy.subtract(plane, self.image_min), (self.image_max - self.image_min) / 256), numpy.uint8,
            'C')
        transform = QTransform()
        scales_indexes = [((x + num_slider) % 3) + 1 for x in [1, 2]]

        transform.scale(header['pixdim'][min(scales_indexes)], header['pixdim'][max(scales_indexes)])
        transform.rotate(-90)

        pixmap = Image.fromarray(converted).toqpixmap().transformed(transform)
        scene = QGraphicsScene(0, 0, pixmap.width(), pixmap.height())

        scene.addPixmap(pixmap)
        self.viewers[num_slider].setScene(scene)

    def cycle_images(self, value):
        self.num_image = value
        for i in range(3): self.draw_viewer(i)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow()
    sys.exit(app.exec())
