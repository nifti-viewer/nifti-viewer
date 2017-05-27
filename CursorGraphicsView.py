from math import floor

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsLineItem, QGraphicsView


class CursorGraphicsView(QGraphicsView):
    coords = None

    def __init__(self, *__args):
        super().__init__(*__args)
        self.num = -1
        self.scale = QPointF(1, 1)

    def mouseReleaseEvent(self, event):
        if not self.scene(): return

        # the event's position is relative to the CursorGraphicsView, but we need it relative to the image
        pos_x = event.x() - (self.width() - self.scene().width() - 1) / 2
        pos_y = event.y() - (self.height() - self.scene().height() - 1) / 2

        # if the position of the click event is on the image, we convert the pixel position on screen to a voxel
        # position in the image, and then update all CursorGraphicsViews to show the corresponding slice as well as a
        # cursor pointing at the clicked voxel
        if pos_x >= 0 and pos_x < self.scene().width() and pos_y >= 0 and pos_y < self.scene().height():
            slider_values = [floor(pos_x / self.scale.x()), floor((self.scene().height() - pos_y) / self.scale.y())]
            CursorGraphicsView.coords = self.get_coords(slider_values)

            for i, slider in enumerate(self.sliders): slider.setValue(self.coords[i])
            for viewer in self.viewers: viewer.show_cursor(self.coords)

    def set_num(self, num: int):
        self.num = num

    def set_scale(self, scale: float):
        self.scale = scale

    def set_viewers(self, viewers):
        self.viewers = viewers

    def set_sliders(self, sliders):
        self.sliders = sliders

    def get_coords(self, pos):
        return [(s.value() if i == self.num else pos.pop(0)) for i, s in enumerate(self.sliders)]

    def make_cursor(self):
        pen = QPen(QColor(0, 255, 0))
        h_line = QGraphicsLineItem(-10, 0, 10, 0)
        v_line = QGraphicsLineItem(0, -10, 0, 10)

        pen.setWidth(1)
        h_line.setPen(pen)
        v_line.setPen(pen)

        self.point_cursor = QGraphicsItemGroup()
        self.point_cursor.addToGroup(h_line)
        self.point_cursor.addToGroup(v_line)
        self.point_cursor.setZValue(1)
        self.point_cursor.setVisible(False)
        self.scene().addItem(self.point_cursor)

    def show_cursor(self, values):
        pos = values.copy()
        pos.pop(self.num)

        self.point_cursor.setVisible(True)
        self.point_cursor.setPos(pos[0] * self.scale.x(), self.scene().height() - pos[1] * self.scale.y())
