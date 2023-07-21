import os.path
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

class Canvas(QtWidgets.QLabel):

    colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00']
    color_index = 0

    def __init__(self, img_path):
        super().__init__()

        pixmap = QtGui.QPixmap(img_path)
        self.pm = pixmap
        self.setPixmap(pixmap)

        # self.last_x, self.last_y = None, None

        self.pen_color = QtGui.QColor('#FF0000')
        self.brush_color = QtGui.QColor('#FF0000')
        self.brush_color.setAlpha(55)

        self.begin, self.destination = QtCore.QPoint(), QtCore.QPoint()

        cursor = Qt.CrossCursor
        self.setCursor(cursor)
        self.undos = []

    def rotate_color(self):
        self.color_index = (self.color_index + 1) % len(self.colors)

        self.pen_color = QtGui.QColor(self.colors[self.color_index])
        self.brush_color = QtGui.QColor(self.colors[self.color_index])
        self.brush_color.setAlpha(55)

    def rectangle_painter(self, obj):
        painter = QtGui.QPainter(obj)

        pen = painter.pen()
        pen.setWidth(1)
        pen.setColor(self.pen_color)
        painter.setPen(pen)

        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.brush_color)))

        return painter

    def paintEvent(self, event):
        painter = self.rectangle_painter(self)
        painter.drawPixmap(QtCore.QPoint(), self.pixmap())

        if not self.begin.isNull() and not self.destination.isNull():
            rect = QtCore.QRect(self.begin, self.destination)
            painter.drawRect(rect.normalized())

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.begin = event.pos()
            self.destination = self.begin
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.destination = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() & Qt.LeftButton:
            rect = QtCore.QRect(self.begin, self.destination)
            painter = self.rectangle_painter(self.pixmap())

            self.undos.append(self.pixmap().copy())

            painter.drawRect(rect.normalized())

            self.begin, self.destination = QtCore.QPoint(), QtCore.QPoint()
            self.update()

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
        self.setStyleSheet("background-color: black;")

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
    window.showMaximized()
    app.exec_()
