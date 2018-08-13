from __future__ import  division 
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors 
import functools
import random

import json
import sys
from BaseControl.TextItem import TextItem, TextItemDlg
from BaseControl.LineItem import LineItem, LineItemDlg
from BaseControl.Location import LocationItem, LocationItemDlg
from BaseControl.VariableItem import VariableItem, VariableItemDlg, CheckWidget
from BaseControl.Edge import EdgeItem, EdgeItemDlg, ImgWidget
from PyQt5.QtCore import (QByteArray, QDataStream, QFile, QFileInfo,QLineF, QLine, 
                          QIODevice, QPoint, QPointF, QRectF, Qt)
from PyQt5.QtWidgets import (QApplication, QDialog, QFrame, 
                             QDialogButtonBox, QFileDialog, QFontComboBox, 
                             QGraphicsItem, QGraphicsPixmapItem,QGraphicsLineItem,    
                             QGraphicsScene, QGraphicsTextItem, QGraphicsView, QGridLayout,
                             QHBoxLayout, QLabel, QMenu, QMessageBox,QPushButton, QSpinBox,
                             QStyle, QTextEdit, QVBoxLayout)
from PyQt5.QtGui import QFont,QCursor,QFontMetrics,QTransform,QPainter,QPen,QPixmap,QBrush
from PyQt5.QtPrintSupport import QPrinter,QPrintDialog
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QTableWidgetItem, QWidget, QHBoxLayout, \
    QApplication

MAC = True
try:
    from PyQt5.QtGui import qt_mac_set_native_menubar
except ImportError:
    MAC = False

#PageSize = (595, 842) # A4 in points
PageSize = (800, 800) # US Letter in points
PointSize = 10

MagicNumber = 0x70616765
FileVersion = 1

Dirty = False
 
        
class GraphicsView(QGraphicsView):

    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)


    def wheelEvent(self, event):
        #factor = 1.41 ** (-event.delta() / 240.0) 
        factor = event.angleDelta().y()/120.0
        if event.angleDelta().y()/120.0 > 0:
            factor=2
        else:
            factor=0.5
        self.scale(factor, factor)

class MainForm(QDialog):

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        self.filename = ""
        self.copiedItem = QByteArray()
        self.pasteOffset = 5
        self.prevPoint = QPoint()
        self.addOffset = 5
        self.borders = []

        self.printer = QPrinter(QPrinter.HighResolution)
        self.printer.setPageSize(QPrinter.Letter)

        self.view = GraphicsView()
 
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, PageSize[0], PageSize[1])
     #   self.addBorders()
        self.view.setScene(self.scene)

        self.wrapped = [] # Needed to keep wrappers alive
        buttonLayout = QVBoxLayout()
        for text, slot in (
                ("Add &Location", self.addLocation), 
                ("Add &Edge", self.addEdge), 
                ("Add &Variable", self.addVariable), 
                ("List &TextName", self.listTextName), 
                ("&Open...", self.open),
                ("&Save", self.save),
                ("&RePaintLine", self.RePaintLine),
                ("&Quit", self.accept), 
                ("&SameX", self.SameX)
                ):
            button = QPushButton(text)
            if not MAC:
                button.setFocusPolicy(Qt.NoFocus)
            if slot is not None:
                button.clicked.connect(slot)
            if text == "&Align":
                menu = QMenu(self)
                for text, arg in (
                        ("Align &Left", Qt.AlignLeft),
                        ("Align &Right", Qt.AlignRight),
                        ("Align &Top", Qt.AlignTop),
                        ("Align &Bottom", Qt.AlignBottom)):
                    wrapper = functools.partial(self.setAlignment, arg)
                    self.wrapped.append(wrapper)
                    menu.addAction(text, wrapper)
                button.setMenu(menu)
            if text == "Pri&nt...":
                buttonLayout.addStretch(5)
            if text == "&Quit":
                buttonLayout.addStretch(1)
            buttonLayout.addWidget(button)
        buttonLayout.addStretch()

        layout = QHBoxLayout()
        layout.addWidget(self.view, 1,)
        layout.addLayout(buttonLayout )
        
        layoutTable = QHBoxLayout()
 
        
        self.EdgeWidget = QTableWidget()
        layoutTable.addWidget(self.EdgeWidget, 1) 
        # setup table widget
        self.EdgeWidget.itemDoubleClicked.connect(self.EdgeWidgetDoubleClicked)
        self.EdgeWidget.setColumnCount(3)
        self.EdgeWidget.setHorizontalHeaderLabels(['EdgeName', 'Guard', 'Reset'])
        self.EdgeWidget.setColumnWidth(0, 40)
        self.EdgeWidget.setColumnWidth(1,200)
        self.EdgeWidget.setColumnWidth(2, 200)
        
        self.EdgeWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.EdgeWidget.setSelectionBehavior(QAbstractItemView.SelectItems)        
        self.EdgeWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.VariablesWidget = QTableWidget()
        layoutTable.addWidget(self.VariablesWidget, 1) 
        # setup table widget
        self.VariablesWidget.itemDoubleClicked.connect(self.VariablesWidgetDoubleClicked)
        self.VariablesWidget.setColumnCount(4)
        self.VariablesWidget.setHorizontalHeaderLabels(['VariableN','Variable', 'Input', 'Output'])
         
        #self.VariablesWidget.hideColumn(0)
        self.VariablesWidget.setColumnWidth(0, 100)        
        self.VariablesWidget.setColumnWidth(1, 100)
        self.VariablesWidget.setColumnWidth(2, 20)
        self.VariablesWidget.setColumnWidth(3, 20)
        self.VariablesWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        #self.VariablesWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.VariablesWidget.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.VariablesWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
       
        layoutMain=QVBoxLayout()
        layoutMain.addLayout(layout)   
        layoutMain.addLayout(layoutTable)  
        layoutMain.setStretchFactor(layout, 8)
        layoutMain.setStretchFactor(layoutTable, 1)
        self.setLayout(layoutMain)

        fm = QFontMetrics(self.font())
        self.resize(self.scene.width() + fm.width(" Delete... ") + 50,
                    self.scene.height() + 50)
        self.setWindowTitle("Page Designer")
        self.dicText= {}
        self.dicLine={}
        self.dicVariable={}
        
        
    def EdgeWidgetDoubleClicked(self, item):
        selectItemText= self.EdgeWidget.item(item.row(), 0).text()
        if selectItemText in self.dicLine:
            dialog = EdgeItemDlg(self.dicLine[selectItemText],   None,self.scene, self )
            dialog.exec_() 
            
            
    def VariablesWidgetDoubleClicked(self, item):
        selectItemText= self.VariablesWidget.item(item.row(), 0).text()
        if selectItemText in self.dicVariable:
            dialog = VariableItemDlg(self.dicVariable[selectItemText],  self )
            dialog.exec_() 
    
    def deleteText (self, LocationItem):
        if LocationItem.boxName in self.dicText:
            self.dicText.pop(LocationItem.boxName)
        self.scene.removeItem(LocationItem)        
        self.scene.update()
    def deleteLine(self, lineItem):
        self.dicLine.pop(lineItem.boxName)
        self.scene.removeItem(lineItem)        
        self.scene.update()
        rowCount=self.EdgeWidget.rowCount()
        for row_index in range(rowCount):
            if self.EdgeWidget.item(row_index, 0).text()==lineItem.boxName: 
                self.EdgeWidget.removeRow(row_index)
                return
                
    def deleteVariable(self, VariableItem):
        self.dicVariable.pop(VariableItem.boxName) 
        rowCount=self.VariablesWidget.rowCount()
        for row_index in range(rowCount):
            if self.VariablesWidget.item(row_index, 0).text()==VariableItem.boxName: 
                self.VariablesWidget.removeRow(row_index)
                return

    def addVariableInTable(self, variableItem):
        row_index=self.VariablesWidget.rowCount()
        self.VariablesWidget.insertRow(row_index)
        row_index=row_index
        self.VariablesWidget.setItem(row_index, 0, QTableWidgetItem( variableItem.boxName, 0))
        self.VariablesWidget.setCellWidget(row_index, 1, ImgWidget(  variableItem.getQPixmap4Variable(), self))
        self.VariablesWidget.setCellWidget(row_index, 2,  CheckWidget(  variableItem.isInput, self)) 
        self.VariablesWidget.setCellWidget(row_index, 3,  CheckWidget(  variableItem.isOutput, self))
    
    def setVariableInTable(self, variableItem):        
        rowCount=self.VariablesWidget.rowCount()
        for row_index in range(rowCount):
            if self.VariablesWidget.item(row_index, 0).text()==variableItem.boxName:                  
                self.VariablesWidget.setCellWidget(row_index, 1, ImgWidget(  variableItem.getQPixmap4Variable(), self))
                self.VariablesWidget.setCellWidget(row_index, 2,  CheckWidget(  variableItem.isInput, self)) 
                self.VariablesWidget.setCellWidget(row_index, 3,  CheckWidget(  variableItem.isOutput, self))
    
                return
    def addEdgeInTable(self, edgeItem):
        row_index=self.EdgeWidget.rowCount()
        self.EdgeWidget.insertRow(row_index)
        row_index=row_index
        self.EdgeWidget.setItem(row_index, 0, QTableWidgetItem( edgeItem.boxName, 0))
        self.EdgeWidget.setCellWidget(row_index, 1, ImgWidget(  edgeItem.getQPixmap4Guard(), self))
        self.EdgeWidget.setCellWidget(row_index, 2,  ImgWidget(  edgeItem.getQPixmap4Reset(), self))
    
    def setEdgeInTable(self, edgeItem):        
        rowCount=self.EdgeWidget.rowCount()
        for row_index in range(rowCount):
            if self.EdgeWidget.item(row_index, 0).text()==edgeItem.boxName: 
                self.EdgeWidget.setCellWidget(row_index, 1, ImgWidget(  edgeItem.getQPixmap4Guard(), self))
                self.EdgeWidget.setCellWidget(row_index, 2,  ImgWidget(  edgeItem.getQPixmap4Reset(), self))
                return
         

        
    def addLocation(self):
        dialog = LocationItemDlg(position=self.position(),
                             scene=self.scene, parent=self)
        dialog.exec_()   
    def listTextName(self):
          buttonReply = QMessageBox.question(self, 'PyQt5 message', str(self.dicText), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
          buttonReply = QMessageBox.question(self, 'PyQt5 message', str(self.dicLine.keys()), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)


    def addVariable(self):
        dialog = VariableItemDlg( parent=self)
        dialog.exec_()
     
    def addPicture(self):
        fig, ax = plt.subplots(figsize=(8, 5))
        X, Y = fig.get_dpi() * fig.get_size_inches()
        h = Y 
        i=2
        if i==2: 
            name='aa'
            formula = r'$x=\frac{3}{100}$'
            ax.text(0.5, 2.5, name+formula, fontsize=(h ),
            horizontalalignment='left',
            verticalalignment='center')

        ax.set_xlim(1, X)
        ax.set_ylim(1, Y)
        ax.set_axis_off()

        #fig.subplots_adjust(left=0, right=1,                    top=1, bottom=0,                    hspace=0, wspace=0)
        plt.show()
    def addEdge(self):
        dialog = EdgeItemDlg(position=self.position(),
                            scene=self.scene, parent=self)
        dialog.exec_()
    
    
    def RePaintLine(self):
        for line in  self.dicLine.values():
            line.resetLine();
        self.scene.update()
    def position(self):
        point = self.mapFromGlobal(QCursor.pos())
        if not self.view.geometry().contains(point):
            coord = random.randint(36, 144)
            point = QPoint(coord, coord)
        else:
            if point == self.prevPoint:
                point += QPoint(self.addOffset, self.addOffset)
                self.addOffset += 5
            else:
                self.addOffset = 5
                self.prevPoint = point
        return self.view.mapToScene(point)
    def open(self):
        self.offerSave()
        self.EdgeWidget.clearContents()
        path = (QFileInfo(self.filename).path()
                if self.filename else ".")
        fname,filetype = QFileDialog.getOpenFileName(self,
                "Page Designer - Open", path,
                "Page Designer Files (*.json)")
        if not fname:
            return
        self.filename = fname
        fh = None
        try:
       
            items = self.scene.items()
            while items:
                item = items.pop()
                self.scene.removeItem(item)
                del item
            #self.addBorders()         dictItemJson={}
            self.dicItem={} 
            with open (self.filename, 'r') as fh:        
                self.dicItem=json.load(fh) 
            for key, item in self.dicItem.items():
                self.readItemFrom( item) 
            self.DrawLineFromRead()
        except IOError as e:
            QMessageBox.warning(self, "Page Designer -- Open Error",
                    "Failed to open {0}: {1}".format(self.filename, e))
        finally:
            if fh is not None:
                fh.close()
        global Dirty
        Dirty = False


    def reject(self):
        self.accept()


    def accept(self):
        self.offerSave()
        QDialog.accept(self)


    def offerSave(self):
        if (Dirty and QMessageBox.question(self,
                            "Page Designer - Unsaved Changes",
                            "Save unsaved changes?",
                            QMessageBox.Yes|QMessageBox.No) == 
           QMessageBox.Yes):
            self.save()

    def SameX(self):
        if self.scene.selectedItems()==None:
            return
        if len(self.scene.selectedItems())==0:
            return
        x=self.scene.selectedItems()[0].x()
        for box in self.scene.selectedItems():
            box.setPos(x, box.y())
            lines=[ line for line in  self.dicLine.values() if ( line.fromBox.boxName== box.boxName or line.toBox.boxName==box.boxName)]
            for line in  lines:
                line.resetLine();
        self.scene.update()
    def SameY(self):
        if self.scene.selectedItems()==None:
            return
        y=self.scene.selectedItems()[0].y()
        for box in self.scene.selectedItems():
            box.setPos(box.x(),y)
        self.scene.update()
    def save(self):
        if not self.filename:
            path = "."
            fname,filetype = QFileDialog.getSaveFileName(self,
                    "Page Designer - Save As", path,
                    "Page Designer Files (*.json)")
            if not fname:
                return
            self.filename = fname
        fh = None
        #try: 
        if 1==1:
            self.scene.clearSelection()
            dictItemJson={}
         
            for item in self.scene.items():
               dictItemJson[item.boxName]=item.toSaveJson()
            with open (self.filename, 'w') as fh:             
                json.dump(dictItemJson, fh)
        #except IOError as e:
        #    QMessageBox.warning(self, "Page Designer -- Save Error",
        #            "Failed to save {0}: {1}".format(self.filename, e))
        #finally:
        #    if fh is not None:
        #       fh.close()
        #    pass
        global Dirty
        Dirty = False

 
    def DrawLineFromRead(self):
            #draw lines between diffenent Loaation
            for key, ln in self.dicItem.items():
                if ln["type"] == "Edge":   
                    str1=ln["strFromLocation"]
                    str2=ln["strToLocation"]
                    if not (str1 == str2):                        
                        n=EdgeItem( ln["boxName"],self.dicText[ln["strFromLocation"]],self.dicText[ln["strToLocation"]], 
                        ln["guard"], ln["reset"], self.scene, self, ln["style"])
                        self.dicLine[ln["boxName"]]=n;
                        n.setRotation(ln["rotation"])
                        self.addEdgeInTable(n)
            #draw lines in a Loaation self
            for key, ln in self.dicItem.items():
                if ln["type"] == "Edge":    
                    str1=ln["strFromLocation"]
                    str2=ln["strToLocation"]
                    if (str1 == str2):
                        n=EdgeItem( ln["boxName"],self.dicText[ln["strFromLocation"]],self.dicText[ln["strToLocation"]], 
                        ln["guard"], ln["reset"], self.scene, self, ln["style"])
                        self.dicLine[ln["boxName"]]=n;
                        n.setRotation(ln["rotation"])
                        self.addEdgeInTable(n)
    def readItemFrom(self, item): 
        if item["type"] == "Text": 
            tx=TextItem(item, '', '',  self.scene, self)
            self.dicText[tx.boxName]=tx;
            tx.setRotation(item["rotation"] )
        elif item["type"]  == "Location":
    #        def __init__(self, boxName, equation, guard, position, isInitial, isNameAbove, scene,parentForm, style=Qt.SolidLine,
    
            tx=LocationItem(item, '', '','', '', '',   self.scene, self)
            self.dicText[tx.boxName]=tx;
            tx.setRotation(item["rotation"] )
            pass
        elif type == "Pixmap":
            pass
        elif type == "Line": 
            pass


    def writeItemToStream(self, item,):
        #if isinstance(item, TextItem):
        data=item.toSaveJson()
        self.dictItemJson[item.boxName]=data
        #elif isinstance(item, LineItem):
        #   data=item.toSaveJson()
        #   self.dictItemJson[item.boxName]=data



app = QApplication(sys.argv)
form = MainForm()
rect = QApplication.desktop().availableGeometry()
form.resize(int(rect.width() * 0.6), int(rect.height() * 0.9))
form.show()
app.exec_()
