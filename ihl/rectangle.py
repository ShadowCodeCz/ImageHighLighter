import glob
import os.path
import subprocess
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtWidgets import QApplication


class Canvas(QtWidgets.QLabel):

    colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00']
    color_index = 0

    def __init__(self, img_path):
        super().__init__()

        pixmap = QtGui.QPixmap(img_path)
        # self.pm = pixmap
        self.setPixmap(pixmap)

        # self.last_x, self.last_y = None, None

        self.pen_color = QtGui.QColor('#FF0000')
        self.brush_color = QtGui.QColor('#FF0000')
        self.brush_color.setAlpha(55)

        self.begin, self.destination = QtCore.QPoint(), QtCore.QPoint()
        self.begin_crop, self.destination_crop = QtCore.QPoint(), QtCore.QPoint()

        cursor = Qt.CrossCursor
        self.setCursor(cursor)
        self.undos = []

        self.action = None

    def rotate_color(self):
        self.color_index = (self.color_index + 1) % len(self.colors)

        self.pen_color = QtGui.QColor(self.colors[self.color_index])
        self.brush_color = QtGui.QColor(self.colors[self.color_index])
        self.brush_color.setAlpha(55)

    def rectangle_painter(self, obj):
        painter = QtGui.QPainter(obj)

        pen = painter.pen()
        pen.setWidth(2)
        pen.setColor(self.pen_color)
        painter.setPen(pen)

        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.brush_color)))
        return painter

    def crop_painter(self, obj):
        painter = QtGui.QPainter(obj)

        pen = painter.pen()
        pen.setWidth(2)
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
            pen.setWidth(2)
            pen.setColor(self.pen_color)
            painter.setPen(pen)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(self.brush_color)))

            painter.drawPixmap(QtCore.QPoint(), self.pixmap())
            rect = QtCore.QRect(self.begin, self.destination)
            painter.drawRect(rect.normalized())

        if self.action == "crop" and not self.begin_crop.isNull() and not self.destination_crop.isNull():
            pen = painter.pen()
            pen.setWidth(2)
            pen.setColor(QtGui.QColor('#000000'))
            pen.setStyle(Qt.DashDotLine)
            painter.setPen(pen)

            brush_color = QtGui.QColor('#FFFFFF')
            brush_color.setAlpha(0)
            # pixmap.fill(QtCore.Qt.transparent)

            painter.setBrush(QtGui.QBrush(brush_color))

            painter.drawPixmap(QtCore.QPoint(), self.pixmap())
            rect = QtCore.QRect(self.begin_crop, self.destination_crop)

            painter.drawRect(rect.normalized())

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
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
            text, ok = dlg.getText(self, 'Input Dialog', 'Text:')

            self.undos.append(self.pixmap().copy())

            painter = self.rectangle_painter(self.pixmap())
            painter.drawText(event.x(), event.y(), text)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.destination = event.pos()
            self.action = "rect"
            self.update()

        if event.buttons() & Qt.MidButton:
            self.destination_crop = event.pos()
            self.action = "crop"
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() & Qt.LeftButton:
            rect = QtCore.QRect(self.begin, self.destination)
            painter = self.rectangle_painter(self.pixmap())

            self.undos.append(self.pixmap().copy())

            painter.drawRect(rect.normalized())

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

    def undo(self):
        if len(self.undos) > 0:
            self.setPixmap(self.undos.pop())
            self.update()

    def save(self, path):
        self.pixmap().save(os.path.abspath(path))
        self.undos = []


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, path):
        super().__init__()

        # self.scroll = QtWidgets.QScrollArea()

        self.path = path
        self.canvas = Canvas(path)
        # self.setStyleSheet("background-color: black;")

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.canvas)
        self.setCentralWidget(self.scrollArea)

        self.setWindowTitle(os.path.abspath(path))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            self.canvas.rotate_color()

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



    def closeEvent(self, event):
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