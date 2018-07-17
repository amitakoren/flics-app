# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 18:20:12 2017

@author: bar23
"""

import os.path
try:
    from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QT_VERSION_STR, QPoint, QPointF, QLineF, QRect
    from PyQt5.QtGui import QImage, QPixmap, QPainterPath, QPen, QPainter, QBrush, QColor
    from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QFileDialog, QGraphicsRectItem, QGraphicsItemGroup, QGraphicsLineItem, QGraphicsTextItem
except ImportError:
    try:
        from PyQt4.QtCore import Qt, QRectF, pyqtSignal, QT_VERSION_STR
        from PyQt4.QtGui import QGraphicsView, QGraphicsScene, QImage, QPixmap, QPainterPath, QFileDialog
    except ImportError:
        raise ImportError("ImageViewerQt: Requires PyQt5 or PyQt4.")

import tifffile
import numpy as np
from PIL import Image
import json


class Imageobj(QGraphicsView):
    leftMouseButtonPressed = pyqtSignal(float, float)
    rightMouseButtonPressed = pyqtSignal(float, float)
    leftMouseButtonReleased = pyqtSignal(float, float)
    rightMouseButtonReleased = pyqtSignal(float, float)
    leftMouseButtonDoubleClicked = pyqtSignal(float, float)
    rightMouseButtonDoubleClicked = pyqtSignal(float, float)

    def __init__(self):
        QGraphicsView.__init__(self)

        # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.rectgroup = QGraphicsItemGroup()
        self.linegroup = QGraphicsItemGroup()
        self._pixmapHandle = None
        self.canZoom = True
        self.canPan = True
        self.zoomStack = []
        self.aspectRatioMode = Qt.KeepAspectRatio
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.begin = QPoint()
        self.end = QPoint()
        self.helper_bool = False
        self.helper_bool2 = False

        self.rect = QGraphicsRectItem()
        self.line = QGraphicsLineItem()

    def hasImage(self):
        """ Returns whether or not the scene contains an image pixmap.
        """
        return self._pixmapHandle is not None

    def pixmap(self):
        """ Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None

    def image(self):
        """ Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def setImage(self, image):
        """ Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        """
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        else:
            raise RuntimeError(
                "ImageViewer.setImage: Argument must be a QImage or QPixmap.")
        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(
            pixmap.rect()))  # Set scene size to image size.
        self.updateViewer()

    def loadImageFromFile(self, fileName=""):
        """ Load an image from file.
        Without any arguments, loadImageFromFile() will popup a file dialog to choose the image file.
        With a fileName argument, loadImageFromFile(fileName) will attempt to load the specified image file directly.
        """
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        results_dir = os.path.join(fileDir,
                                   'results\\200_frames_of_bloodflow_results')
        if len(fileName) == 0:
            if QT_VERSION_STR[0] == '4':
                fileName = QFileDialog.getOpenFileName(self,
                                                       "Open image file.")
            elif QT_VERSION_STR[0] == '5':
                fileName, dummy = QFileDialog.getOpenFileName(
                    self, "Open image file.")
        if len(fileName) and os.path.isfile(fileName):
            imageName, file_data = self.create_image(fileName, results_dir)
            image = QImage(imageName)
            self.setImage(image)
        print(fileName)

    def Extract_image_and_metadata(self, file_data):
        global file_metadata

        im2show_path = file_data["im2show_path"]
        metadata_path = file_data["metadata_path"]
        # fileName = file_data["fileName"]
        filepath = file_data["path"]
        if os.path.isfile(metadata_path):
            with open(metadata_path, 'r') as fp:
                file_metadata = json.load(fp)
        else:
            with tifffile.TiffFile(filepath) as tif:
                file_metadata = tif.scanimage_metadata
                with open(metadata_path, 'w') as fp:
                    json.dump(file_metadata, fp)

        if not os.path.isfile(im2show_path):
            tif_original = tifffile.imread(filepath)
            # first_five = tif_full_original[1:10:2]#selecting 5 image from tif, only vessels
            tif_original_size = tif_original.shape
            if len(tif_original_size) == 2:
                tif = tif_original.copy()
                arr = tif
            else:
                first_five = tif_original[1:10:2].copy()
                if file_metadata["SI.hScan2D.bidirectional"]:
                    num_im, w, h = first_five.shape
                    tif = np.zeros((num_im, int(h / 2), w))
                for i in range(num_im):
                    tif[i] = first_five[i][::2]
                else:
                    tif = tif_original.copy()
                arr = tif[0]
            tif_size = tif.shape
            print(tif_size)
            # image5 = (tif[0]/5)+(tif[1]/5)+(tif[2]/5)+(tif[3]/5)+(tif[4]/5)
            # arr_avg=np.array(np.round(image5),dtype=np.int16) #round the pixels values
            # arr = tif[0]
            im2show = Image.fromarray(arr)
            try:
                im2show.save(im2show_path)
            except OSError:
                im2show = im2show.convert(mode='I')
                im2show.save(im2show_path)

        return file_metadata

    def updateViewer(self):
        """ Show current zoom (if showing entire image, apply current aspect ratio mode).
        """
        if not self.hasImage():
            return
        if len(self.zoomStack) and self.sceneRect().contains(
                self.zoomStack[-1]):
            self.fitInView(self.zoomStack[-1], Qt.IgnoreAspectRatio
                           )  # Show zoomed rect (ignore aspect ratio).
        else:
            self.zoomStack = [
            ]  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(
                self.sceneRect(), self.aspectRatioMode
            )  # Show entire image (use current aspect ratio mode).

    def resizeEvent(self, event):
        """ Maintain current zoom on resize.
        """
        self.updateViewer()

    def mousePressEvent(self, event):
        """ Start mouse pan or zoom mode.
        """

        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            if self.canPan and self.helper_bool:
                self.setDragMode(QGraphicsView.RubberBandDrag)
            elif self.canPan and self.helper_bool2:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
                self.start = scenePos
                #QGraphicsView.mouseMoveEvent(self,event)
                #self.setMouseTracking(True)
            self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        # self.cursorStartPosition = self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        # self.start = QPoint(self.cursorStartPosition.x(),self.cursorStartPosition.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                self.setDragMode(QGraphicsView.RubberBandDrag)
            self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """ Stop mouse pan or zoom mode (apply zoom if valid).
        """

        QGraphicsView.mouseReleaseEvent(self, event)
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            if self.helper_bool:
                viewBBox = self.zoomStack[-1] if len(
                    self.zoomStack) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect(
                ).intersected(viewBBox)
                if selectionBBox.isValid():

                    self.rect.setRect(selectionBBox)
                    self.rect.setPen(QPen(Qt.white))
                    self.scene.addItem(self.rect)

            elif self.helper_bool2:
                viewBBox = self.zoomStack[-1] if len(
                    self.zoomStack) else self.sceneRect()
                self.cursorCurrentPosition = scenePos
                self.current = QPointF(self.cursorCurrentPosition.x(),
                                       self.cursorCurrentPosition.y())
                pen = QPen(Qt.red, 1, Qt.SolidLine)

                self.line.setLine(QLineF(self.start, self.current))
                self.line.setPen(pen)
                self.scene.addItem(self.line)

            self.setDragMode(QGraphicsView.NoDrag)
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())

        elif event.button() == Qt.RightButton:
            if self.canZoom:
                viewBBox = self.zoomStack[-1] if len(
                    self.zoomStack) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect(
                ).intersected(viewBBox)
                self.scene.setSelectionArea(
                    QPainterPath())  # Clear current selection area.
                if selectionBBox.isValid() and (selectionBBox != viewBBox):
                    self.zoomStack.append(selectionBBox)
                    self.updateViewer()
            self.setDragMode(QGraphicsView.NoDrag)
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        # self.scene.addItem(self.group)
        self.updateViewer()

    def mouseDoubleClickEvent(self, event):
        """ Show entire image.
        """

        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:

            self.leftMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                self.zoomStack = []  # Clear zoom stack.
                self.updateViewer()
            self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mouseDoubleClickEvent(self, event)

    def approve_obj(self):
        self.scene.removeItem(self.rect)
        self.scene.removeItem(self.line)

        viewBBox = self.zoomStack[-1] if len(
            self.zoomStack) else self.sceneRect()
        selectionBBox = self.scene.selectionArea().boundingRect().intersected(
            viewBBox)
        rect = QGraphicsRectItem()
        rect.setRect(selectionBBox)
        rect.setPen(QPen(Qt.green))
        self.rectgroup.addToGroup(rect)
        self.scene.addItem(self.rectgroup)

        line = QGraphicsLineItem()
        line.setLine(QLineF(self.start, self.current))
        line.setPen(QPen(Qt.green))
        self.linegroup.addToGroup(line)
        self.scene.addItem(self.linegroup)

        return (selectionBBox, self.start, self.current)

    def create_fromDB(self, pos_list=[], obj_type=""):
        if obj_type == "rois":
            num_rois = len(pos_list)
            for i in range(num_rois):
                points = pos_list[i]
                rect = QGraphicsRectItem()
                rect.setPen(QPen(Qt.green))
                rect.setRect(points[0], points[1], points[2], points[3])
                self.rectgroup.addToGroup(rect)
            self.scene.addItem(self.rectgroup)
        elif obj_type == "vector":
            num_vec = len(pos_list)
            for i in range(num_vec):
                points = pos_list[i]
                vec = QGraphicsLineItem()
                vec.setPen(QPen(Qt.green))
                vec.setLine(points[0][0], points[0][1], points[1][0],
                            points[1][1])
                self.linegroup.addToGroup(vec)
            self.scene.addItem(self.linegroup)

    def mark_item(self, item_num):
        rect_items = self.rectgroup.childItems()
        line_items = self.linegroup.childItems()
        rect_item = rect_items[item_num]
        line_item = line_items[item_num]
        rect_item.setPen(QPen(Qt.red))
        line_item.setPen(QPen(Qt.red))
        rect_items.remove(rect_item)
        line_items.remove(line_item)
        for i in rect_items:
            i.setPen(QPen(Qt.green))
        for i in line_items:
            i.setPen(QPen(Qt.green))

    def delete_roi(self, num):
        self.scene.removeItem(self.rectgroup)
        self.scene.removeItem(self.linegroup)
        rect_item = self.rectgroup.childItems()[num]
        line_item = self.linegroup.childItems()[num]
        self.rectgroup.removeFromGroup(rect_item)
        self.linegroup.removeFromGroup(line_item)
        self.scene.addItem(self.rectgroup)
        self.scene.addItem(self.linegroup)

    def restart_obj(self):
        self.scene.removeItem(self.rectgroup)
        self.scene.removeItem(self.linegroup)
        rect_items = self.rectgroup.childItems()
        line_items = self.linegroup.childItems()
        for rect_item in rect_items:
            self.rectgroup.removeFromGroup(rect_item)
        for line_item in line_items:
            self.linegroup.removeFromGroup(line_item)


if __name__ == '__main__':
    import sys
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        try:
            from PyQt4.QtGui import QApplication
        except ImportError:
            raise ImportError("ImageViewerQt: Requires PyQt5 or PyQt4.")
    print('ImageViewerQt: Using Qt ' + QT_VERSION_STR)

    info_dic = {}
    # Create the application.
    app = QApplication(sys.argv)

    # Create image viewer and load an image file to display.
    viewer = Imageobj()
    viewer.loadImageFromFile()  # Pops up file dialog.

    # Handle left mouse clicks with custom slot.

    # Show viewer and run application.
    viewer.show()
    sys.exit(app.exec_())