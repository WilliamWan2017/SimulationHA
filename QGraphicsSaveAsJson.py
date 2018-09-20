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
                             QStyle, QTextEdit, QVBoxLayout, QLineEdit, QComboBox, QShortcut,)
from PyQt5.QtGui import QFont,QCursor,QFontMetrics,QTransform,QPainter,QPen,QPixmap,QBrush, QKeySequence
from PyQt5.QtPrintSupport import QPrinter,QPrintDialog
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QTableWidgetItem, QWidget, QHBoxLayout, \
    QApplication

MAC = True
try:
    from PyQt5.QtGui import qt_mac_set_native_menubar
except ImportError:
    MAC = False

#PageSize = (595, 842) # A4 in points
PageSize = (800, 700) # US Letter in points
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

        self.view = GraphicsView(self)
 
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
               # ("List &TextName", self.listTextName), 
                ("&Open...", self.open),
                ("&Save", self.save),
                ("&RePaintLine", self.RePaintLine),
                ("&Quit", self.accept), 
                #("&SameX", self.SameX), 
                ("&New Black HA", self.newHA),              
                ("QLineEdit", "Current HA Name")  ,   
                ("QComboBox", "HA Name List"),                 
                ("QLineEdit", "Current Model Name")  , 
                ("S&witch HA", self.switchHA)  ,        
                ("&Delete HA", self.deleteHA), 
                ("&Copy And New HA", self.copyHA) 
                ):
            if text  in ['QLineEdit', 'QComboBox']:
                lbl=QLabel(slot) 
                buttonLayout.addWidget(lbl)
                if slot=='Current HA Name':
                    self.txtHAName=QLineEdit()       
                    self.txtHAName.setText("NoName")
                    buttonLayout.addWidget( self.txtHAName)  
                    #self.txtHAName.textChanged.connect(self.txtChanged)
                if slot=='Current Model Name':
                    self.txtModelName=QLineEdit()               
                    self.txtModelName.setText("NoName")     
                    buttonLayout.addWidget( self.txtModelName)
                    self.txtModelName.hide()                    
                    #self.txtModelName.textChanged.connect(self.txtChanged)
                    lbl.hide()
                if slot=='HA Name List':
                    self.cmbHANameList=QComboBox()                    
                    buttonLayout.addWidget( self.cmbHANameList)
                
            else:   
                button = QPushButton(text)
                if not MAC:
                    button.setFocusPolicy(Qt.NoFocus)
                if slot is not None:
                    button.clicked.connect(slot)
                #if shortcutKey:
                #    shortcut = QShortcut(QKeySequence(shortcutKey), self) 
                #   shortcut.activated.connect(slot) 
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
        
        layoutTable = QVBoxLayout()#BoxLayout()
 
        
        self.EdgeWidget = QTableWidget()
        layoutTable.addWidget(self.EdgeWidget) 
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
        
        #self.EdgeWidget.resizeColumnsToContents() 
        self.VariablesWidget = QTableWidget()
        layoutTable.addWidget(self.VariablesWidget) 
        # setup table widget
        self.VariablesWidget.itemDoubleClicked.connect(self.VariablesWidgetDoubleClicked)
        self.VariablesWidget.setColumnCount(5)
        self.VariablesWidget.setHorizontalHeaderLabels(['Name','Initial Value', 'Input', 'Output', "IsConstant"])
         
        #self.VariablesWidget.hideColumn(0)
        self.VariablesWidget.setColumnWidth(0, 100)        
        self.VariablesWidget.setColumnWidth(1, 200)
        self.VariablesWidget.setColumnWidth(2, 100)
        self.VariablesWidget.setColumnWidth(3,100)
        self.VariablesWidget.setColumnWidth(4,100)
        self.VariablesWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        #self.VariablesWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.VariablesWidget.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.VariablesWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #self.VariablesWidget.resizeColumnsToContents() 
        layoutMain=QVBoxLayout()
        layoutMain.addLayout(layout)   
        layoutMain.addLayout(layoutTable)  
        layoutMain.setStretchFactor(layout, 8)
        layoutMain.setStretchFactor(layoutTable, 2)
        self.setLayout(layoutMain)

        fm = QFontMetrics(self.font())
        self.resize(self.scene.width() + fm.width(" Delete... ") + 50,
                    self.scene.height() + 50)
        self.setWindowTitle("Simulation of HA Designer")
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint|Qt.WindowMaximizeButtonHint|Qt.WindowCloseButtonHint) 
        self.dicText= {}
        self.dicLine={}
        self.dicVariable={}
        self.dicHA={}
        self.dicModel={}
        #self.dicModel["HAs"]={}         
        self.currentProject={}
        #self.currentProject["Models"]={}
        
        #self.currentProject["Models"]["NoName"]=self.dicModel
        self.currentHA=None

    def txtChanged(self):
        self.setDirty()
        
    def setDirty(self, newDirty=None):
        if newDirty is None:
            newDirty=True
        global Dirty
        Dirty=newDirty 
    
    def newHA(self):
        if self.txtHAName.text()=="NoName":
            if (Dirty):
                QMessageBox.question(self,
                            "Please Input HA Name",
                            "Fail to New HA,Please Change the HA Name from 'NoName' to a new name you want!",
                            QMessageBox.Ok )  
                return
        self.offerSave()       
        if (Dirty):
            QMessageBox.question(self,
                            "Please Save or Discard Current Editing",
                            "Fail to new HA,Please Save or Discard current editing first!",
                            QMessageBox.Ok )  
            return 
        self.clearCurrent()
        self.txtHAName.setText("NoName")
        self.currentHA=None 
    def copyHA(self):
        global Dirty
        if self.txtHAName.text()=="NoName":
            if (Dirty):
                QMessageBox.question(self,
                            "Please Input HA Name",
                            "Fail to copy HA,Please Change the HA Name from 'NoName' to a new name you want!",
                            QMessageBox.Ok )  
                return        
        self.offerSave()
        if (Dirty):
            QMessageBox.question(self,
                            "Please Save or Discard Current Editing",
                            "Fail to copy HA,Please Save or Discard current editing first!",
                            QMessageBox.Ok )  
            return
        '''if (self.cmbHANameList.currentText()==""):
            QMessageBox.question(self,
                            "Please Select HA Name",
                            "Fail to copy HA,Please select a HA Name in HA Name List!",
                            QMessageBox.Ok )  
            return
        '''
        self.currentHA= self.currentProject["Models"][self.txtModelName.text()]["HAs"][self.txtHAName.text()]        
        self.clearCurrent()
        self.DrawHA(self.currentHA)
        self.txtHAName.setText("NoName")
        self.currentHA=None
        self.setDirty()
       
        
    def switchHA(self):
        if self.txtHAName.text()=="NoName":
            if (Dirty):
                QMessageBox.question(self,
                            "Please Input HA Name",
                            "Fail to switch HA,Please Change the HA Name from 'NoName' to a new name you want!",
                            QMessageBox.Ok )  
                return    
        NewHAName=self.cmbHANameList.currentText()
        self.offerSave()
        if (Dirty):
            QMessageBox.question(self,
                            "Please Save or Discard Current Editing",
                            "Fail to switch HA,Please Save or Discard current editing first!",
                            QMessageBox.Ok )  
            return
        if (self.cmbHANameList.currentText()==""):
            QMessageBox.question(self,
                            "Please Select HA Name",
                            "Fail to switch HA,Please select a HA Name in HA Name List!",
                            QMessageBox.Ok )  
            return
        self.clearCurrent()
        self.cmbHANameList.setEditText(NewHAName )
        self.txtHAName.setText(self.cmbHANameList.currentText())
        self.DrawHA()
    def deleteHA(self):
        strHAName=self.txtHAName.text() 
        if (strHAName in self.currentProject["Models"][self.txtModelName.text()]["HAs"].keys()):
            self.currentProject["Models"][self.txtModelName.text()]["HAs"].pop(strHAName)
        self.clearCurrent()  
        if not self.filename:            
            pass
        else:
            with open (self.filename, 'w') as fh:             
                json.dump(self.currentProject, fh)
        self.setDirty(False)
        self.DrawDefaultHA() 
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
        self.VariablesWidget.setItem(row_index, 1, QTableWidgetItem(  variableItem.initialValue, 0))
        self.VariablesWidget.setItem(row_index, 2, QTableWidgetItem( str(variableItem.isInput), 0))
        self.VariablesWidget.setItem(row_index, 3, QTableWidgetItem( str(variableItem.isOutput), 0))
        self.VariablesWidget.setItem(row_index, 4, QTableWidgetItem( str(variableItem.isConstant), 0))
        self.VariablesWidget.resizeRowToContents(row_index)
        self.VariablesWidget.resizeRowsToContents()
        self.VariablesWidget.resizeColumnsToContents()
        
        #self.VariablesWidget.setCellWidget(row_index, 2,  CheckWidget(  variableItem.isInput, self)) 
        #self.VariablesWidget.setCellWidget(row_index, 3,  CheckWidget(  variableItem.isOutput, self))
    
    def setVariableInTable(self, variableItem):        
        rowCount=self.VariablesWidget.rowCount()
        for row_index in range(rowCount):
            if self.VariablesWidget.item(row_index, 0).text()==variableItem.boxName:                  
                #self.VariablesWidget.setCellWidget(row_index, 1, ImgWidget(  variableItem.getQPixmap4Variable(), self))
                #self.VariablesWidget.setCellWidget(row_index, 2,  CheckWidget(  variableItem.isInput, self)) 
                #self.VariablesWidget.setCellWidget(row_index, 3,  CheckWidget(  variableItem.isOutput, self))
         
                self.VariablesWidget.setItem(row_index, 1, QTableWidgetItem(  variableItem.initialValue, 0))
                self.VariablesWidget.setItem(row_index, 2, QTableWidgetItem( str(variableItem.isInput), 0))
                self.VariablesWidget.setItem(row_index, 3, QTableWidgetItem( str(variableItem.isOutput), 0))
                self.VariablesWidget.setItem(row_index, 4, QTableWidgetItem( str(variableItem.isConstant), 0))
                self.VariablesWidget.resizeRowToContents(row_index)
                self.VariablesWidget.resizeColumnsToContents()
          #ui->tableWidget->resizeRowToContents(curRow)
                return
    def addEdgeInTable(self, edgeItem):
        row_index=self.EdgeWidget.rowCount()
        self.EdgeWidget.insertRow(row_index)
        row_index=row_index
        self.EdgeWidget.setItem(row_index, 0, QTableWidgetItem( edgeItem.boxName, 0))        
        self.EdgeWidget.setItem(row_index, 1, QTableWidgetItem( edgeItem.guard, 0))        
        self.EdgeWidget.setItem(row_index, 2, QTableWidgetItem( edgeItem.reset, 0))
        #self.EdgeWidget.setCellWidget(row_index, 1, ImgWidget(  edgeItem.getQPixmap4Guard(), self))
        #self.EdgeWidget.setCellWidget(row_index, 2,  ImgWidget(  edgeItem.getQPixmap4Reset(), self))
        self.EdgeWidget.resizeRowToContents(row_index)        
        self.EdgeWidget.resizeRowsToContents()
        self.EdgeWidget.resizeColumnsToContents()
    def setEdgeInTable(self, edgeItem):        
        rowCount=self.EdgeWidget.rowCount()
        for row_index in range(rowCount):
            if self.EdgeWidget.item(row_index, 0).text()==edgeItem.boxName:  
                self.EdgeWidget.setItem(row_index, 1, QTableWidgetItem( edgeItem.guard, 0))       
                self.EdgeWidget.setItem(row_index, 2, QTableWidgetItem( edgeItem.reset, 0))
                #self.EdgeWidget.setCellWidget(row_index, 1, ImgWidget(  edgeItem.getQPixmap4Guard(), self))
                #self.EdgeWidget.setCellWidget(row_index, 2,  ImgWidget(  edgeItem.getQPixmap4Reset(), self))
                self.EdgeWidget.resizeRowToContents(row_index)
                self.EdgeWidget.resizeColumnsToContents()
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
       # self.scene.update()
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
    def clearCurrent(self):
        
        self.EdgeWidget.clearContents()
        self.EdgeWidget.setRowCount(0)        
        self.VariablesWidget.clearContents()
        self.VariablesWidget.setRowCount(0)   
      
        items = self.scene.items()
        while items:
            item = items.pop()
            self.scene.removeItem(item)
            del item
            #self.addBorders()         dictItemJson={}
        self.dicItem={}   
        self.dicLine={}
        self.dicText={}
        self.dicVariable={}
    def DrawHA(self, currentHA=None):
        if (currentHA is None):
            if not self.txtModelName.text() in self.currentProject["Models"].keys():
                return
            if not self.txtHAName.text() in  self.currentProject["Models"][self.txtModelName.text()]["HAs"].keys():
                return
            self.currentHA= self.currentProject["Models"][self.txtModelName.text()]["HAs"][self.txtHAName.text()]     
        else:
            self.currentHA=currentHA
        for key,  item in self.currentHA["boxes"].items():
            self.readItemFrom( item) 
        self.DrawLine(self.currentHA["lines"])
        self.DrawVariable(self.currentHA["variables"])
    def DrawDefaultHA(self):
        if ("NoName" in self.currentProject["Models"].keys()) or  len( self.currentProject["Models"])==0:
            self.txtModelName.setText("NoName")
        else:                           
            self.txtModelName.setText(next(iter(self.currentProject["Models"].keys())))
        if ("NoName" in self.currentProject["Models"][self.txtModelName.text()]["HAs"].keys())  or  len( self.currentProject["Models"][self.txtModelName.text()]["HAs"])==0:
            self.txtHAName.setText("NoName")
        else:            
            self.txtHAName.setText(next(iter(self.currentProject["Models"][self.txtModelName.text()]["HAs"].keys()))) 
        self.cmbHANameList.clear()
        self.cmbHANameList.addItems([key for key in self.currentProject["Models"][self.txtModelName.text()]["HAs"].keys()])   
        self.DrawHA( )
    def open(self):
        self.offerSave()
        path = (QFileInfo(self.filename).path()
                if self.filename else ".")
        fname,filetype = QFileDialog.getOpenFileName(self,
                "Page Designer - Open", path,
                "Page Designer Files (*.json)")
        if not fname:
            return
        self.filename = fname
        self.clearCurrent()
        fh = None
        #try:
        if 1==1:
       
            with open (self.filename, 'r') as fh:        
                self.currentProject=json.load(fh) 
            self.DrawDefaultHA()
       
        '''except IOError as e:
            QMessageBox.warning(self, "Page Designer -- Open Error",
                    "Failed to open {0}: {1}".format(self.filename, e))
        finally:
            if fh is not None:
                fh.close()
        '''
        global Dirty
        Dirty = False


    def reject(self):
        self.accept()


    def accept(self):
        self.offerSave()
        QDialog.accept(self)


    def offerSave(self):
        if self.currentHA is not None:
            if not self.currentHA["name"]==self.txtHAName.text():
                self.setDirty()
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
            dicBoxSave={} 
            dicLineSave={}
            dicVariableSave={}
            for item in self.dicText.values():
               dicBoxSave[item.boxName]=item.toSaveJson()
            for item in self.dicLine.values():
               dicLineSave[item.boxName]=item.toSaveJson()
            for item in self.dicVariable.values():                
               dicVariableSave[item.boxName]=item.toSaveJson()
            if self.currentHA is not None:
                if not self.currentHA["name"]== self.txtHAName.text():
                    self.currentProject["Models"][self.txtModelName.text()]["HAs"].pop(self.currentHA["name"])
            HASave={}
            HASave["boxes"]=dicBoxSave
            HASave["lines"]=dicLineSave
            HASave["variables"]=dicVariableSave
            HASave["type"]="HA"
            HASave["name"]=self.txtHAName.text()
            #self.dicHA[self.txtHAName.text()]=HASave
            if (len(dicBoxSave)>0):
                if not "Models" in self.currentProject.keys():
                    self.currentProject["Models"]={}
                if not self.txtModelName.text() in self.currentProject["Models"].keys():
                    self.currentProject["Models"][self.txtModelName.text()]={}                    
                if not "HAs" in self.currentProject["Models"][self.txtModelName.text()].keys():
                    self.currentProject["Models"][self.txtModelName.text()]["HAs"]={}
                self.currentProject["Models"][self.txtModelName.text()]["HAs"][self.txtHAName.text()]=HASave            
            CurrentModel={}
            CurrentModel["HAs"]=self.dicHA
            CurrentModel["type"]="Model"
            CurrentModel["name"]=self.txtModelName.text()
            #self.dicModel[self.txtModelName.text()]=CurrentModel
            self.currentHA=HASave
            #self.currentProject["Models"]=self.dicModel
            self.cmbHANameList.clear()
            self.cmbHANameList.addItems([key for key in self.currentProject["Models"][self.txtModelName.text()]["HAs"].keys()])
   
            with open (self.filename, 'w') as fh:             
                json.dump(self.currentProject, fh)
            
        #except IOError as e:
        #    QMessageBox.warning(self, "Page Designer -- Save Error",
        #            "Failed to save {0}: {1}".format(self.filename, e))
        #finally:
        #    if fh is not None:
        #       fh.close()
        #    pass
        global Dirty
        Dirty = False 

    def DrawVariable(self, Variables):
            #draw lines between diffenent Loaation
            for key, ln in Variables.items():
                if ln["type"] == "Variable":    
                    if not "isConstant" in ln.keys():
                        ln["isConstant"]=False
                    if not "initialValue" in ln.keys():
                        ln["initialValue"]="0"      
                    v=VariableItem( ln["boxName"],ln["isInput"], ln["isOutput"], ln["isConstant"], ln["initialValue"], self)    
                    self.dicVariable[v.boxName]=v                
                    self.addVariableInTable(v)
    def DrawLine(self, Lines):
            #draw lines between diffenent Loaation
            for key, ln in Lines.items():
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
            for key, ln in Lines.items():
                if ln["type"] == "Edge":    
                    str1=ln["strFromLocation"]
                    str2=ln["strToLocation"]
                    if (str1 == str2):
                        n=EdgeItem( ln["boxName"],self.dicText[ln["strFromLocation"]],self.dicText[ln["strToLocation"]], 
                        ln["guard"], ln["reset"], self.scene, self, ln["style"])
                        self.dicLine[ln["boxName"]]=n;
                        n.setRotation(ln["rotation"])
                        self.addEdgeInTable(n)
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
    
            tx=LocationItem(item, '', '','', '','',  '', '',   self.scene, self)
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
form.resize(int(rect.width() * 0.9), int(rect.height() * 0.9))
form.show()
app.exec_()
