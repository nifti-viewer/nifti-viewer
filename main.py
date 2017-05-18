#!/usr/bin/python3
import os
import sys

import nibabel
import numpy
from PIL import Image
from PyQt5 import uic
from PyQt5.QtCore import QPointF, QRegExp, QStringListModel
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QApplication, QFileDialog, QGraphicsScene, QGraphicsView, QLabel, QListView, QMainWindow, \
    QSlider

from CursorGraphicsView import CursorGraphicsView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('mainwindow.ui', self)

        self.action_Open.triggered.connect(self.open_file)
        self.action_Save_points_to_file.triggered.connect(self.save_points_to_file)
        self.image_labels = self.findChildren(QLabel, QRegExp("image_slice_label_."))
        self.image_sliders = self.findChildren(QSlider, QRegExp("image_slider_."))
        self.image_viewers = self.findChildren(QGraphicsView, QRegExp("image_viewer_."))
        self.contrast_sliders = self.findChildren(QSlider, QRegExp("image_contrast_.*_slider"))
        self.points_list = self.findChild(QListView, 'points_list')
        self.points_model = QStringListModel()
        self.points = []

        self.points_list.setModel(self.points_model)
        self.setWindowTitle('Nifti viewer')
        self.show()

        for i in range(3):
            self.image_sliders[i].valueChanged.connect(lambda value, i=i: self.draw_viewer(i))

        for slider in self.contrast_sliders:
            slider.valueChanged.connect(self.draw_viewers)

        self.image_cycle_slider.valueChanged.connect(self.cycle_images)

    def open_file(self):
        file_info = QFileDialog.getOpenFileName(parent=self, directory=os.path.expanduser('~'), filter='*.nii *.nii.gz')
        if not os.path.isfile(file_info[0]): return

        self.action_Save.triggered.connect(self.save_point)
        self.action_Delete.triggered.connect(self.delete_point)
        self.niba_img = nibabel.load(file_info[0])
        data = self.niba_img.get_data()
        self.image_min = data.min()
        self.image_max = data.max()
        self.num_image = 0

        if len(data.shape) == 4:
            self.image_cycle_slider.setMaximum(data.shape[3] - 1)

        for i, slider in enumerate(self.image_sliders):
            slider.setMaximum(data.shape[i] - 1)
            slider.setValue(0)

        for slider in self.contrast_sliders:
            slider.setMinimum(self.image_min)
            slider.setMaximum(self.image_max)

        self.contrast_sliders[0].setValue(self.image_min)
        self.contrast_sliders[1].setValue(self.image_max)

        for i, viewer in enumerate(self.image_viewers):
            viewer.set_num(i)
            viewer.set_viewers(self.image_viewers)
            viewer.set_sliders(self.image_sliders)
            self.draw_viewer(i)

    def save_point(self):
        if CursorGraphicsView.coords is None: return
        self.points.append(str(CursorGraphicsView.coords + [self.num_image or 0]))
        self.points_model.setStringList(self.points)

    def save_points_to_file(self):
        file_info = QFileDialog.getSaveFileName(parent=self, directory=os.path.expanduser('~'), filter='*.txt')

        try:
            file = open(file_info[0], 'w')
            file.write(os.linesep.join(map(str, self.points)))
        except:
            pass

    def delete_point(self):
        pass

    def draw_viewer(self, num_slider: int):
        if self.niba_img is None: return

        data = self.niba_img.get_data()
        header = self.niba_img.get_header()

        if data is None or header is None: return

        self.image_labels[num_slider].setText(self.tr("Slice " + str(self.image_sliders[num_slider].value())))

        slice_range = [slice(None)] * 3
        slice_range[num_slider] = self.image_sliders[num_slider].value()
        slice_range = tuple(slice_range)

        if len(data.shape) == 4: slice_range = slice_range + (self.num_image,)

        plane = numpy.copy(data[slice_range])
        image_min = self.image_contrast_min_slider.value()
        image_max = self.image_contrast_max_slider.value()
        plane[plane < image_min] = image_min
        plane[plane > image_max] = image_max

        if self.image_min == self.image_max: self.image_max = 1

        converted = numpy.require(numpy.divide(numpy.subtract(plane, image_min), (image_max - image_min) / 255),
                                  numpy.uint8, 'C')
        transform = QTransform()
        scales_indexes = [((x + num_slider) % 3) + 1 for x in [1, 2]]
        scale = QPointF(header['pixdim'][min(scales_indexes)], header['pixdim'][max(scales_indexes)])

        transform.scale(scale.x(), scale.y())
        transform.rotate(-90)

        pixmap = Image.fromarray(converted).toqpixmap().transformed(transform)
        scene = QGraphicsScene(0, 0, pixmap.width(), pixmap.height())

        scene.addPixmap(pixmap)
        self.image_viewers[num_slider].setScene(scene)
        self.image_viewers[num_slider].set_scale(scale)
        self.image_viewers[num_slider].make_cursor()

    def draw_viewers(self):
        for i in range(3): self.draw_viewer(i)

    def cycle_images(self, value):
        self.num_image = value
        self.draw_viewers()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow()
    sys.exit(app.exec())
