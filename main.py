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

    def __init__(self):
        super().__init__()
        uic.loadUi('mainwindow.ui', self)

        self.sliders = [self.image_slider_0,
                        self.image_slider_1, self.image_slider_2]
        self.viewers = [self.image_viewer_0,
                        self.image_viewer_1, self.image_viewer_2]
        self.action_open.triggered.connect(self.open_file)
        self.setWindowTitle('Nifti viewer')
        self.show()

        self.sliders[0].valueChanged.connect(lambda value: self.draw_viewer(0))
        self.sliders[1].valueChanged.connect(lambda value: self.draw_viewer(1))
        self.sliders[2].valueChanged.connect(lambda value: self.draw_viewer(2))

        for viewer in self.viewers:
            viewer.setViewport(QGLWidget())

    def open_file(self):
        file_info = QFileDialog.getOpenFileName(parent=self, directory=os.path.expanduser('~'), filter='*.nii *.nii.gz')
        if not os.path.isfile(file_info[0]): return

        self.niba_img = nibabel.load(file_info[0])
        data = self.niba_img.get_data()

        for i, slider in enumerate(self.sliders):
            slider.setMaximum(data.shape[i] - 1)
            slider.setValue(0)

        for i, viewer in enumerate(self.viewers):
            self.draw_viewer(i)

    def draw_viewer(self, num_slider: int):
        data = self.niba_img.get_data()
        header = self.niba_img.get_header()
        if data is None: return

        slice_range = [slice(None)] * 3
        slice_range[num_slider] = self.sliders[num_slider].value()
        slice_range = tuple(slice_range)

        if len(data.shape) == 4: slice_range = slice_range + (0,)  # TODO : integrate 4th slider for multiple images

        plane = data[slice_range]
        minimum = plane.min()
        maximum = plane.max()
        converted = numpy.require(numpy.divide(numpy.subtract(plane, minimum), maximum / 256), numpy.uint8, 'C')
        transform = QTransform()
        scales_indexes = [((x + num_slider) % 3) + 1 for x in [1, 2]]

        transform.scale(header['pixdim'][min(scales_indexes)], header['pixdim'][max(scales_indexes)])
        transform.rotate(-90)

        pixmap = Image.fromarray(converted).toqpixmap().transformed(transform)
        scene = QGraphicsScene(0, 0, pixmap.width(), pixmap.height())

        scene.addPixmap(pixmap)
        self.viewers[num_slider].setScene(scene)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow()
    sys.exit(app.exec())
