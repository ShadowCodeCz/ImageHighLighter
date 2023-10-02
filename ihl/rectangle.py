import ctypes
import glob
import os.path
import subprocess
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QMimeData, QRectF, QPoint
from PyQt5.QtGui import QIcon, QTextOption, QFont
from PyQt5.QtWidgets import QApplication, QFileDialog


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
        self.number_alpha_modifier = 50
        self.font_size = 12

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

        self.action = None
        self.scroll_area = None
        self.counter = 1
        self.note_text = ""

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
            dlg.setStyleSheet("background-color: white")
            dlg.setMinimumWidth(250)
            self.text, ok = dlg.getMultiLineText(self, 'Text', 'Text:', self.text)

            self.undos.append(self.pixmap().copy())

            painter = self.rectangle_painter(self.pixmap())
            # painter.drawText(event.x(), event.y(), f"{text}\naaa")
            # text_rect = QRectF(event.x(), event.y(), self.pixmap().rect().width() - event.y(), self.pixmap().rect().height() - event.x())
            text_rect = QRectF(QPoint(event.x(), event.y()), QPoint(self.pixmap().rect().width(), self.pixmap().rect().height()))
            painter.setFont(QFont("Arial", self.font_size))
            painter.drawText(text_rect, Qt.AlignTop | Qt.AlignLeft, self.text)

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
        font = QFont("Arial", self.font_size)
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
        dlg.setStyleSheet("background-color: white")
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

        font = QFont("Arial", self.font_size)
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
        dlg.setStyleSheet("background-color: white")
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

        font = QFont("Arial", self.font_size)
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

        self.setWindowTitle(os.path.abspath(path))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            self.canvas.rotate_color()

        if event.key() == Qt.Key_P:
            self.canvas.counter += 1

        if event.key() == Qt.Key_M:
            self.canvas.counter -= 1

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

        if event.key() == Qt.Key_Escape:
            self.close_dialog()
            self.close()

    def closeEvent(self, event):
        self.close_dialog()

    def close_dialog(self):
        if len(self.canvas.undos) > 0:
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("UNSAVED CHANGES")
            dlg.setText("Do you want save changes?")
            dlg.setStyleSheet("background-color: white")
            dlg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            button = dlg.exec()

            if button == QtWidgets.QMessageBox.Yes:
                self.canvas.save(self.path)

def run(arguments):
    app = QtWidgets.QApplication(sys.argv)
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