import math
import ctypes
import glob
import os.path
import subprocess
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QMimeData, QRectF, QPoint, QSizeF
from PyQt5.QtGui import QIcon, QTextOption, QFont, QFontMetricsF
from PyQt5.QtWidgets import QApplication, QFileDialog, QStatusBar, QFontDialog

import qdarktheme

class Canvas(QtWidgets.QLabel):

    colors = ['#FF0000', '#13A613', '#475ECE', '#FFFF00', '#5e5e5e', '#F68757', '#00FF00', '#0000FF', '#C752C7']
    color_index = 0

    def __init__(self, img_path):
        super().__init__()

        pixmap = QtGui.QPixmap(img_path)
        # self.pm = pixmap
        self.setPixmap(pixmap)
        self.text = ""

        self.pen_width = 1
        self.alpha = 55
        self.number_alpha_modifier = 90
        self.text_alpha_modifier = 150
        self.font_size = 12

        self.font = QFont("Arial", self.font_size)
        self.font.setBold(False)

        # self.last_x, self.last_y = None, None

        self.pen_color = QtGui.QColor('#FF0000')
        self.brush_color = QtGui.QColor('#FF0000')
        self.brush_color.setAlpha(self.alpha)

        self.begin, self.destination = QtCore.QPoint(), QtCore.QPoint()
        self.last_begin, self.last_destination = QtCore.QPoint(), QtCore.QPoint()
        self.begin_crop, self.destination_crop = QtCore.QPoint(), QtCore.QPoint()

        cursor = Qt.CrossCursor
        self.setCursor(cursor)
        self.undos = []
        self.rects = []

        self.action = None
        self.scroll_area = None
        self.counter = 1
        self.note_text = ""
        self.full_comment_border = True

    def rotate_color(self):
        self.color_index = (self.color_index + 1) % len(self.colors)

        self.pen_color = QtGui.QColor(self.colors[self.color_index])
        self.brush_color = QtGui.QColor(self.colors[self.color_index])
        self.brush_color.setAlpha(self.alpha)

    def update_pen_and_brush(self):
        self.pen_color = QtGui.QColor(self.colors[self.color_index])
        self.brush_color = QtGui.QColor(self.colors[self.color_index])
        self.brush_color.setAlpha(self.alpha)

    def rectangle_painter(self, obj):
        painter = QtGui.QPainter(obj)

        pen = painter.pen()
        pen.setWidth(self.pen_width)
        pen.setColor(self.pen_color)
        painter.setPen(pen)

        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.brush_color)))
        return painter

    def crop_painter(self, obj):
        painter = QtGui.QPainter(obj)

        pen = painter.pen()
        pen.setWidth(self.pen_width)
        pen.setColor(QtGui.QColor('#000000'))
        pen.setStyle(Qt.DashDotLine)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.brush_color)))

        return painter

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(QtCore.QPoint(), self.pixmap())

        # if self.action == "crop.finish":
        #     rect = QtCore.QRect(self.begin_crop, self.destination_crop)
        #     # self.setPixmap(self.pixmap().copy(rect))
        #     painter = QtGui.QPainter(self.pixmap().copy(rect))
        #     print("crop.finish")
        #     painter.drawPixmap(QtCore.QPoint(), self.pixmap().copy(rect))
        #     self.action = None
        # else:
        #     painter = QtGui.QPainter(self)
        #     painter.drawPixmap(QtCore.QPoint(), self.pixmap())

        if self.action == "rect" and not self.begin.isNull() and not self.destination.isNull():
            pen = painter.pen()
            pen.setWidth(self.pen_width)
            pen.setColor(self.pen_color)
            painter.setPen(pen)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(self.brush_color)))

            painter.drawPixmap(QtCore.QPoint(), self.pixmap())
            rect = QtCore.QRect(self.begin, self.destination)
            painter.drawRect(rect.normalized())

        if self.action == "crop" and not self.begin_crop.isNull() and not self.destination_crop.isNull():
            pen = painter.pen()
            pen.setWidth(2)
            pen.setColor(QtGui.QColor('#8A2BE2'))
            pen.setStyle(Qt.DashDotLine)
            painter.setPen(pen)

            brush_color = QtGui.QColor('#8A2BE2')
            brush_color.setAlpha(10)
            # pixmap.fill(QtCore.Qt.transparent)

            painter.setBrush(QtGui.QBrush(brush_color))

            painter.drawPixmap(QtCore.QPoint(), self.pixmap())
            rect = QtCore.QRect(self.begin_crop, self.destination_crop)

            painter.drawRect(rect.normalized())

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton and event.modifiers() != Qt.ControlModifier:
            self.begin = event.pos()
            self.destination = self.begin
            self.action = "rect"
            self.update()

        if event.buttons() & Qt.MidButton:
            self.begin_crop = event.pos()
            self.destination_crop = self.begin_crop
            self.action = "crop"
            self.update()

        if event.buttons() & Qt.RightButton:
            dlg = QtWidgets.QInputDialog(self)
            # dlg.setStyleSheet("background-color: white")
            dlg.setMinimumWidth(250)
            self.text, ok = dlg.getMultiLineText(self, 'Text', 'Text:', self.text)

            self.undos.append(self.pixmap().copy())

            painter = self.rectangle_painter(self.pixmap())
            # painter.drawText(event.x(), event.y(), f"{text}\naaa")
            # text_rect = QRectF(event.x(), event.y(), self.pixmap().rect().width() - event.y(), self.pixmap().rect().height() - event.x())


            # text_rect = QRectF(QPoint(event.x(), event.y()), QPoint(self.pixmap().rect().width(), self.pixmap().rect().height()))

            font = self.get_font()
            rows = self.text.split("\n")
            longest_rows = max(rows, key=lambda r: len(r))
            bounding_text_rect = QFontMetricsF(font).boundingRect(longest_rows)
            lines = self.text.count("\n") + 1
            modifier = 10
            full_rect = QRectF(QPoint(event.x() - modifier, event.y() - modifier),
                               QPoint(int(event.x() + bounding_text_rect.width() + modifier), int(event.y() + bounding_text_rect.height() * lines + modifier))
                               )

            text_rect = QRectF(QPoint(int(full_rect.x() + modifier), int(full_rect.y() + modifier)),
                               QSizeF(full_rect.width(), full_rect.height()))

            # painter = self.rectangle_painter(self.pixmap())

            pen = painter.pen()
            pen.setWidth(self.pen_width)
            pen.setColor(self.pen_color)
            painter.setPen(pen)

            color = QtGui.QColor(self.brush_color)
            color.setAlpha(190)
            brush = QtGui.QBrush(QtGui.QColor(color))
            painter.setBrush(brush)
            painter.drawRect(full_rect)

            # font.setBold(True)
            painter.setFont(font)

            pen = painter.pen()
            pen.setWidth(self.pen_width)
            pen.setColor(QtGui.QColor('#000000'))
            painter.setPen(pen)

            color = QtGui.QColor(self.brush_color)
            brush = QtGui.QBrush(QtGui.QColor(color))
            painter.setBrush(brush)

            if self.text.strip() != "":
                painter.drawText(text_rect, Qt.AlignTop | Qt.AlignLeft, self.text)
                self.rects.append(full_rect)

            # color = painter.brush().color()
            # color.setAlpha(self.alpha + self.text_alpha_modifier)
            # brush = QtGui.QBrush(QtGui.QColor(color))
            # painter.setBrush(brush)
            #
            # pen = painter.pen()
            # pen.setWidth(self.pen_width)
            # pen.setColor(QtGui.QColor("#000000"))
            # painter.setPen(pen)
            #
            # painter.drawRect(full_rect)
            #
            # painter.setFont(font)
            #
            # text_rect = QRectF(QPoint(int(full_rect.x() + modifier), int(full_rect.y() + modifier)),
            #                    QSizeF(full_rect.width(), full_rect.height()))
            # painter.drawText(text_rect, Qt.AlignTop | Qt.AlignLeft, self.text)


    def mouseDoubleClickEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            # self.undos.append(self.pixmap().copy())
            #
            # painter = self.rectangle_painter(self.pixmap())
            # text_rect = QRectF(event.x(), event.y(), self.font_size * 2, self.font_size * 2)
            # font = QFont("Arial", self.font_size)
            # font.setBold(True)
            # painter.setFont(font)
            # painter.drawText(text_rect, Qt.AlignCenter, str(self.counter))
            #
            # pen = painter.pen()
            # pen.setWidth(self.pen_width)
            # pen.setColor(self.pen_color)
            # painter.setPen(pen)
            # painter.setBrush(QtGui.QBrush(QtGui.QColor(self.brush_color)))
            #
            # painter.drawPixmap(QtCore.QPoint(), self.pixmap())
            # painter.drawRect(text_rect.normalized())
            #
            # self.counter += 1
            # self.update()
            text_rect = QRectF(event.x() - self.font_size, event.y() - self.font_size, self.font_size * 2, self.font_size * 2)
            self.draw_number(text_rect)


    def draw_number(self, rect):
        self.undos.append(self.pixmap().copy())

        painter = self.rectangle_painter(self.pixmap())
        # text_rect = QRectF(event.x(), event.y(), self.font_size * 2, self.font_size * 2)
        font = self.get_font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, str(self.counter))

        pen = painter.pen()
        pen.setWidth(self.pen_width)
        pen.setColor(self.pen_color)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.brush_color)))

        # painter.drawPixmap(QtCore.QPoint(), self.pixmap())
        color = painter.brush().color()
        color.setAlpha(self.alpha + self.number_alpha_modifier)
        brush = QtGui.QBrush(QtGui.QColor(color))
        painter.setBrush(brush)

        painter.drawRect(rect.normalized())

        self.counter += 1
        self.update()
        self.rects.append(rect)


    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and event.modifiers() != Qt.ControlModifier:
            self.destination = event.pos()
            self.action = "rect"
            self.update()

        if event.buttons() & Qt.MidButton:
            self.destination_crop = event.pos()
            self.action = "crop"
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() & Qt.LeftButton and event.modifiers() != Qt.ControlModifier:
            rect = QtCore.QRect(self.begin, self.destination)
            painter = self.rectangle_painter(self.pixmap())

            self.undos.append(self.pixmap().copy())

            painter.drawRect(rect.normalized())
            rect_fixed = QtCore.QRect(self.begin, QPoint(self.destination.x() + 1, self.destination.y() + 1))
            self.rects.append(rect_fixed)

            self.last_begin = self.begin
            self.last_destination = self.destination

            self.begin, self.destination = QtCore.QPoint(), QtCore.QPoint()
            self.action = "rect"
            self.update()

        if event.button() & Qt.MidButton:
            rect = QtCore.QRect(self.begin_crop, self.destination_crop)
            # painter = self.crop_painter(self.pixmap().copy(rect))

            self.undos.append(self.pixmap().copy())

            # painter.drawRect(rect.normalized())
            self.setPixmap(self.pixmap().copy(rect))
            self.action = "crop.finish"

            #  QImage image("initial_image.jpg");
            #     QImage copy ;
            #     copy = image.copy( 0, 0, 128, 128);
            #     copy.save("cropped_image.jpg");

            self.update()
            self.begin_crop, self.destination_crop = QtCore.QPoint(), QtCore.QPoint()
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().minimum()
            )
            self.scroll_area.horizontalScrollBar().setValue(
                self.scroll_area.horizontalScrollBar().minimum()
            )

    def undo(self):
        if len(self.undos) > 0:
            self.setPixmap(self.undos.pop())
            self.update()

    def save(self, path):
        self.pixmap().save(os.path.abspath(path))
        self.undos = []

    def increase_pen_width(self):
        self.pen_width += 1
        self.update_pen_and_brush()

    def decrease_pen_width(self):
        self.pen_width -= 1
        if self.pen_width < 1:
            self.pen_width = 1
        self.update_pen_and_brush()

    def increase_font_size(self):
        self.font_size += 1
        self.update_pen_and_brush()

    def decrease_font_size(self):
        self.font_size -= 1
        if self.font_size < 7:
            self.font_size = 7
        self.update_pen_and_brush()

    def increase_alpha(self):
        self.alpha += 5
        self.update_pen_and_brush()

    def decrease_alpha(self):
        self.alpha -= 5
        if self.alpha < 0:
            self.alpha = 0
        self.update_pen_and_brush()

    def increase_number_alpha_modifier(self):
        self.number_alpha_modifier += 5
        self.update_pen_and_brush()

    def decrease_number_alpha_modifier(self):
        self.number_alpha_modifier -= 5
        if self.number_alpha_modifier < 0:
            self.number_alpha_modifier = 0
        self.update_pen_and_brush()

    def draw_number_to_left_top_inside_corner(self):
        if not self.last_begin.isNull() and not self.last_destination.isNull():
            last_rect = QtCore.QRect(self.last_begin, self.last_destination)
            text_rect = QRectF(last_rect.topLeft().x(), last_rect.topLeft().y(), self.font_size * 2, self.font_size * 2)
            self.draw_number(text_rect)

    def draw_number_to_right_top_inside_corner(self):
        if not self.last_begin.isNull() and not self.last_destination.isNull():
            last_rect = QtCore.QRect(self.last_begin, self.last_destination)
            text_rect = QRectF(last_rect.topLeft().x() + last_rect.width() - self.font_size * 2, last_rect.topLeft().y(), self.font_size * 2, self.font_size * 2)
            self.draw_number(text_rect)

    def draw_number_to_left_bottom_inside_corner(self):
        if not self.last_begin.isNull() and not self.last_destination.isNull():
            last_rect = QtCore.QRect(self.last_begin, self.last_destination)
            text_rect = QRectF(last_rect.topLeft().x(), last_rect.topLeft().y() + last_rect.height() - self.font_size * 2, self.font_size * 2, self.font_size * 2)
            self.draw_number(text_rect)

    def draw_number_to_right_bottom_inside_corner(self):
        if not self.last_begin.isNull() and not self.last_destination.isNull():
            last_rect = QtCore.QRect(self.last_begin, self.last_destination)
            text_rect = QRectF(
                last_rect.topLeft().x() + last_rect.width() - self.font_size * 2,
                last_rect.topLeft().y() + last_rect.height() - self.font_size * 2,
                self.font_size * 2,
                self.font_size * 2)
            self.draw_number(text_rect)

    def draw_top_note(self):
        dlg = QtWidgets.QInputDialog(self)
        # dlg.setStyleSheet("background-color: white")
        dlg.setMinimumWidth(250)
        self.note_text, ok = dlg.getMultiLineText(self, 'Text', 'Text:', self.note_text)

        text = self.note_text.strip()
        lines = text.count("\n") + 1
        self.undos.append(self.pixmap().copy())

        painter = self.rectangle_painter(self.pixmap())

        pen = painter.pen()
        pen.setWidth(self.pen_width)
        pen.setColor(self.pen_color)
        painter.setPen(pen)

        color = QtGui.QColor(self.brush_color)
        color.setAlpha(210)
        brush = QtGui.QBrush(QtGui.QColor(color))
        painter.setBrush(brush)

        last_rect = QtCore.QRect(self.last_begin, self.last_destination)
        rect = QRectF(
            last_rect.topLeft().x(),
            last_rect.topLeft().y() - (self.font_size * 2 * lines),
            last_rect.width(),
            self.font_size * 2 * lines
        )
        painter.drawRect(rect.normalized())

        font = self.get_font()
        font.setBold(True)
        painter.setFont(font)

        pen = painter.pen()
        pen.setWidth(self.pen_width)
        pen.setColor(QtGui.QColor('#000000'))
        painter.setPen(pen)

        color = QtGui.QColor(self.brush_color)
        brush = QtGui.QBrush(QtGui.QColor(color))
        painter.setBrush(brush)

        painter.drawText(rect.normalized(), Qt.AlignCenter | Qt.AlignHCenter | Qt.AlignVCenter, text)

        self.update()

    def draw_bottom_note(self):
        dlg = QtWidgets.QInputDialog(self)
        # dlg.setStyleSheet("background-color: white")
        dlg.setMinimumWidth(250)
        self.note_text, ok = dlg.getMultiLineText(self, 'Text', 'Text:', self.note_text)

        text = self.note_text.strip()
        lines = text.count("\n") + 1
        self.undos.append(self.pixmap().copy())

        painter = self.rectangle_painter(self.pixmap())

        pen = painter.pen()
        pen.setWidth(self.pen_width)
        pen.setColor(self.pen_color)
        painter.setPen(pen)

        color = QtGui.QColor(self.brush_color)
        color.setAlpha(210)
        brush = QtGui.QBrush(QtGui.QColor(color))
        painter.setBrush(brush)

        last_rect = QtCore.QRect(self.last_begin, self.last_destination)
        rect = QRectF(
            last_rect.bottomLeft().x(),
            last_rect.bottomLeft().y(),
            last_rect.width(),
            self.font_size * 2 * lines
        )
        painter.drawRect(rect.normalized())

        font = self.get_font()
        font.setBold(True)
        painter.setFont(font)

        pen = painter.pen()
        pen.setWidth(self.pen_width)
        pen.setColor(QtGui.QColor('#000000'))
        painter.setPen(pen)

        color = QtGui.QColor(self.brush_color)
        brush = QtGui.QBrush(QtGui.QColor(color))
        painter.setBrush(brush)

        painter.drawText(rect.normalized(), Qt.AlignCenter | Qt.AlignHCenter | Qt.AlignVCenter, text)

        self.update()

    def connect_two_last_rects(self):
        if (len(self.rects) >= 2 ):
            self.undos.append(self.pixmap().copy())
            # print("connect")
            r1 = self.rects[-1]
            r2 = self.rects[-2]
            painter = self.rectangle_painter(self.pixmap())
            painter.setRenderHints(painter.Antialiasing)
            painter.drawLine(*self.closest_corners(r1, r2))
            self.update()

    def connect_two_last_rects_by_direct_lines(self):
        if (len(self.rects) >= 2 ):
            self.undos.append(self.pixmap().copy())
            # print("connect")
            r1 = self.rects[-1]
            r2 = self.rects[-2]

            painter = self.rectangle_painter(self.pixmap())
            # painter.setRenderHints(painter.Antialiasing)

            closest_corners = self.closest_corners(r1, r2)
            cc1 = closest_corners[0]
            cc2 = closest_corners[1]
            painter.drawLine(cc1, QPoint(int(cc2.x()), int(cc1.y())))
            painter.drawLine(cc2, QPoint(int(cc2.x()), int(cc1.y())))

            self.update()

    def connect_two_last_mid_rects_by_direct_lines(self):
        if (len(self.rects) >= 2 ):
            self.undos.append(self.pixmap().copy())
            # print("connect")
            r1 = self.rects[-1]
            r2 = self.rects[-2]

            r1_mid_points = self.mid_points_of_rectangle(r1)
            r2_mid_points = self.mid_points_of_rectangle(r2)

            painter = self.rectangle_painter(self.pixmap())
            painter.setRenderHints(painter.Antialiasing)

            closest_corners = self.closest_points(r1_mid_points, r2_mid_points)

            cc1 = closest_corners[0]
            cc2 = closest_corners[1]

            painter.drawLine(cc1, QPoint(int(cc2.x()), int(cc1.y())))
            painter.drawLine(cc2, QPoint(int(cc2.x()), int(cc1.y())))

            self.update()

    def connect_two_last_mid_2_rects_by_direct_lines(self):
        if (len(self.rects) >= 2 ):
            self.undos.append(self.pixmap().copy())
            # print("connect")
            r1 = self.rects[-1]
            r2 = self.rects[-2]

            r1_mid_points = self.mid_points_of_rectangle(r1)
            r2_mid_points = self.mid_points_of_rectangle(r2)

            painter = self.rectangle_painter(self.pixmap())
            painter.setRenderHints(painter.Antialiasing)

            closest_corners = self.closest_points(r1_mid_points, r2_mid_points)

            cc1 = closest_corners[0]
            cc2 = closest_corners[1]

            if cc1.x() > cc2.x():
                cc1, cc2 = cc2, cc1

            x_diff = cc2.x() - cc1.x()
            x_diff_half = int(x_diff // 2)
            painter.drawLine(cc1, QPoint(int(cc1.x() + x_diff_half), int(cc1.y())))
            painter.drawLine(QPoint(int(cc1.x() + x_diff_half), int(cc1.y())), QPoint(int(cc2.x() - x_diff_half), int(cc2.y())))
            painter.drawLine(cc2, QPoint(int(cc2.x() - x_diff_half), int(cc2.y())))

            self.update()

    def closest_corners(self, r1: QRectF, r2: QRectF):
        min = []
        min_dist = 1000000

        r1_corners = [r1.topLeft(), r1.topRight(), r1.bottomLeft(), r1.bottomRight()]
        r2_corners = [r2.topLeft(), r2.topRight(), r2.bottomLeft(), r2.bottomRight()]

        for r1c in r1_corners:
            for r2c in r2_corners:
                distance = self.two_points_distance(r1c, r2c)
                if distance < min_dist:
                    min_dist = distance
                    min = [r1c, r2c]

        return min

    def closest_points(self, points_left, points_right):
        min = []
        min_dist = 1000000
        for r1c in points_left:
            for r2c in points_right:
                distance = self.two_points_distance(r1c, r2c)
                if distance < min_dist:
                    min_dist = distance
                    min = [r1c, r2c]

        return min

    def mid_points_of_rectangle(self, rect):
        top_center = QPoint(int((rect.topLeft().x() + rect.topRight().x()) // 2), int(rect.topLeft().y()))
        bottom_center = QPoint(int((rect.bottomLeft().x() + rect.bottomRight().x()) // 2), int(rect.bottomLeft().y()))
        left_center = QPoint(int(rect.topLeft().x()), int((rect.topLeft().y() + rect.bottomLeft().y()) // 2))
        right_center = QPoint(int(rect.topRight().x()), int((rect.topRight().y() + rect.bottomRight().y()) // 2))

        return [top_center, bottom_center, left_center, right_center]

    # def have_closest_corners_same_coordinate(self, closest_corners):
    #     if closest_corners[0].x()

    def two_points_distance(self, p1, p2):
        return int(math.sqrt((p2.x() - p1.x())**2 + (p2.y() - p1.y())**2))


    def extend(self):
        self.undos.append(self.pixmap().copy())
        new_pixmap = QtGui.QPixmap(self.pixmap().width() + 80, self.pixmap().height() + 80)
        new_pixmap.fill(Qt.black)

        painter = QtGui.QPainter(new_pixmap)
        painter.drawPixmap(40, 40, self.pixmap())

        # self.pm = pixmap
        self.setPixmap(new_pixmap)
        painter.end()
        self.update()

    def extend_top(self, height):
        self.undos.append(self.pixmap().copy())
        new_pixmap = QtGui.QPixmap(self.pixmap().width(), self.pixmap().height() + height)
        new_pixmap.fill(Qt.black)

        painter = QtGui.QPainter(new_pixmap)
        painter.drawPixmap(0, height, self.pixmap())

        # self.pm = pixmap
        self.setPixmap(new_pixmap)
        painter.end()
        self.update()

    def extend_bottom(self, height):
        self.undos.append(self.pixmap().copy())
        new_pixmap = QtGui.QPixmap(self.pixmap().width(), self.pixmap().height() + height)
        new_pixmap.fill(Qt.black)

        painter = QtGui.QPainter(new_pixmap)
        painter.drawPixmap(0, 0, self.pixmap())

        # self.pm = pixmap
        self.setPixmap(new_pixmap)
        painter.end()
        self.update()

    def getText(self):
        dlg = QtWidgets.QInputDialog(self)
        # dlg.setStyleSheet("background-color: white")
        dlg.setMinimumWidth(250)
        self.text, ok = dlg.getMultiLineText(self, 'Text', 'Text:', self.text)

    def add_full_top_comment(self):
        self.undos.append(self.pixmap().copy())
        self.getText()
        self.text = self.text.strip()

        font_size = self.font_size + 10
        height = int((self.text.count("\n") + 1) * 1.5 * font_size)
        self.extend_top(height)

        rect = QRectF(QPoint(0, 0), QSizeF(self.pixmap().width() - 1, height - 1))

        painter = self.rectangle_painter(self.pixmap())
        pen = painter.pen()
        pen.setWidth(self.pen_width)
        pen.setColor(self.pen_color)
        painter.setPen(pen)

        color = QtGui.QColor(self.brush_color)
        color.setAlpha(105)
        brush = QtGui.QBrush(Qt.black)
        # brush = QtGui.QBrush(QtGui.QColor(color))
        painter.setBrush(brush)
        if self.full_comment_border:
            painter.drawRect(rect)

        font = self.get_font()
        font.setBold(True)
        painter.setFont(font)

        pen = painter.pen()
        pen.setWidth(self.pen_width)
        # pen.setColor(QtGui.QColor('#000000'))
        painter.setPen(pen)

        color = QtGui.QColor(self.brush_color)
        brush = QtGui.QBrush(QtGui.QColor(color))
        painter.setBrush(brush)

        if self.text.strip() != "":
            painter.drawText(rect, Qt.AlignCenter | Qt.AlignHCenter | Qt.AlignVCenter, self.text)
        painter.end()
        self.update()

    def add_full_bottom_comment(self):
        self.undos.append(self.pixmap().copy())
        self.getText()
        self.text = self.text.strip()
        pixmap_height = self.pixmap().height()
        height = (self.text.count("\n") + 1) * 2 * self.font_size
        print(height)
        self.extend_bottom(height)

        rect = QRectF(QPoint(0, pixmap_height), QSizeF(self.pixmap().width(), height))

        painter = self.rectangle_painter(self.pixmap())
        pen = painter.pen()
        pen.setWidth(self.pen_width)
        pen.setColor(self.pen_color)
        painter.setPen(pen)

        color = QtGui.QColor(self.brush_color)
        color.setAlpha(90)
        # brush = QtGui.QBrush(QtGui.QColor(color))
        brush = QtGui.QBrush(QtGui.QColor(Qt.black))
        painter.setBrush(brush)
        # painter.drawRect(rect)

        font = self.get_font()
        font.setBold(False)
        painter.setFont(font)

        pen = painter.pen()
        pen.setWidth(self.pen_width)
        pen.setColor(QtGui.QColor(self.pen_color))
        painter.setPen(pen)

        color = QtGui.QColor(self.brush_color)
        brush = QtGui.QBrush(QtGui.QColor(color))
        painter.setBrush(brush)

        if self.text.strip() != "":
            painter.drawText(rect, Qt.AlignCenter | Qt.AlignHCenter | Qt.AlignVCenter, self.text)
        painter.end()
        self.update()

    def get_font(self):
        self.font.setPointSize(self.font_size)
        return self.font

    def font_dialog(self):
        font = self.get_font()
        font, ok = QFontDialog.getFont(font)

        if ok:
            self.font = font
            self.font_size = font.pointSize()

    def switch_full_comment_board(self):
        self.full_comment_border = not self.full_comment_border


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, path):
        super().__init__()

        my_app_id = 'shadowcode.ihl.rectangle.02'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

        logo_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources", 'logo.png')
        self.setWindowIcon(QIcon(logo_path))

        # self.scroll = QtWidgets.QScrollArea()

        self.path = path
        self.canvas = Canvas(path)
        # self.setStyleSheet("background-color: black;")

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setBackgroundRole(QtGui.QPalette.Dark)
        self.scroll_area.setWidget(self.canvas)
        self.setCentralWidget(self.scroll_area)

        self.canvas.scroll_area = self.scroll_area

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.updateStatusBar()
        self.setWindowTitle(os.path.abspath(path))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            self.canvas.rotate_color()
            self.setWindowTitle(f"{os.path.abspath(self.path)} [{self.canvas.color_index}]")

        if event.key() == Qt.Key_X:
            self.canvas.connect_two_last_rects()

        if event.key() == Qt.Key_Y:
            self.canvas.connect_two_last_rects_by_direct_lines()

        if event.key() == Qt.Key_Q:
            self.canvas.connect_two_last_mid_rects_by_direct_lines()

        if event.key() == Qt.Key_W:
            self.canvas.connect_two_last_mid_2_rects_by_direct_lines()

        if event.key() == Qt.Key_E:
            self.canvas.extend()

        if event.key() == Qt.Key_T:
            self.canvas.add_full_top_comment()

        if event.key() == Qt.Key_B:
            self.canvas.add_full_bottom_comment()

        if event.key() == Qt.Key_F:
            self.canvas.font_dialog()

        if event.key() == Qt.Key_P:
            self.canvas.counter += 1

        if event.key() == Qt.Key_M:
            self.canvas.counter -= 1

        if event.key() == Qt.Key_R:
            self.canvas.switch_full_comment_board()

        if event.modifiers() & Qt.ShiftModifier:
            if event.key() == Qt.Key_Plus:
                self.canvas.increase_font_size()
            if event.key() == Qt.Key_Minus:
                self.canvas.decrease_font_size()

        if event.modifiers() & Qt.AltModifier:
            if event.key() == Qt.Key_Minus:
                self.canvas.decrease_alpha()

            if event.key() == Qt.Key_Plus:
                self.canvas.increase_alpha()

            if event.key() == Qt.Key_I:
                self.canvas.increase_number_alpha_modifier()

            if event.key() == Qt.Key_D:
                self.canvas.decrease_number_alpha_modifier()

        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Z:
                self.canvas.undo()
            if event.key() == Qt.Key_S:
                self.canvas.save(self.path)
            if event.key() == Qt.Key_C:
                clipboard = QApplication.clipboard()
                data = QMimeData()
                data.setImageData(self.canvas.pixmap())
                clipboard.setMimeData(data)

            if event.key() == Qt.Key_O:
                file_path, _ = QFileDialog.getOpenFileName(self,
                                                        'Open file',
                                                        os.getcwd(),
                                                        'Image files (*.jpg *.jpeg *.png *.bmp *.gif)')
                subprocess.Popen(f"ihl rect -p {file_path}")

            # TODO: N - Next, P - Previous (in current working directory)
            # if event.key() == Qt.Key_N:
            #     subprocess.Popen(f"ihl rect -p {self.path}")

            if event.key() == Qt.Key_Plus:
                self.canvas.increase_pen_width()

            if event.key() == Qt.Key_Minus:
                self.canvas.decrease_pen_width()

            if event.key() == Qt.Key_7:
                self.canvas.draw_number_to_left_top_inside_corner()

            if event.key() == Qt.Key_9:
                self.canvas.draw_number_to_right_top_inside_corner()

            if event.key() == Qt.Key_1:
                self.canvas.draw_number_to_left_bottom_inside_corner()

            if event.key() == Qt.Key_3:
                self.canvas.draw_number_to_right_bottom_inside_corner()

            if event.key() == Qt.Key_8:
                self.canvas.draw_top_note()

            if event.key() == Qt.Key_2:
                self.canvas.draw_bottom_note()

        self.updateStatusBar()

        if event.key() == Qt.Key_Escape:
            self.close_dialog()
            self.close()


    def updateStatusBar(self):
        m = f"color: {self.canvas.color_index} [TAB], font.size: {self.canvas.font_size} [SHIFT +, SHIFT -], pen.width: {self.canvas.pen_width} [CTRL +, CTRL -], alpha: {self.canvas.alpha} [ALT +, ALT -], text.alpha.modifier: {self.canvas.text_alpha_modifier}, number.alpha.modifier: {self.canvas.number_alpha_modifier} [ALT I, ALT D], counter: {self.canvas.counter} [P, M], undos: {len(self.canvas.undos)}, border {self.canvas.full_comment_border},  [CTRL Z], extend [E], top.comment [T], top.comment.board [R], bottom.comment [B], connect [x, y, q, w], font [F], open [CTRL O]"
        self.statusBar.showMessage(m)


    def closeEvent(self, event):
        self.close_dialog()

    def close_dialog(self):
        if len(self.canvas.undos) > 0:
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("UNSAVED CHANGES")
            dlg.setText("Do you want save changes?")
            # dlg.setStyleSheet("background-color: white")
            dlg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            button = dlg.exec()

            if button == QtWidgets.QMessageBox.Yes:
                self.canvas.save(self.path)

def run(arguments):
    app = QtWidgets.QApplication(sys.argv)
    qdarktheme.setup_theme()
    window = MainWindow(arguments.path)
    if arguments.frameless:
        window.setWindowFlags(Qt.FramelessWindowHint)
        window.showMaximized()
    else:
        if arguments.minimize:
            window.showMinimized()
        else:
            window.showMaximized()
    app.exec_()


def run_for_all(arguments):
    images = []
    suffixes = ["*.png", "*.jpg", "*.jpeg", "*.bmp"]
    for s in suffixes:
        for p in glob.glob(s):
            cmd = f"ihl rect -p {p}"
            if arguments.rect_minimize:
                subprocess.Popen(f"{cmd} -z")
            else:
                subprocess.Popen(cmd)