import json
import functools
import random
import sys
from latex2sympy.process_latex import process_sympy
from BaseControl.CheckPointItem import CheckPointItem
import FormatParseLatex
from sympy import *
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from PyQt5.QtCore import (QByteArray, QDataStream, QFile, QFileInfo,QLineF, QLine, 
                          QIODevice, QPoint, QPointF, QRectF, Qt, QSizeF)
from PyQt5.QtWidgets import (QApplication, QDialog, QFrame, 
                             QDialogButtonBox, QFileDialog, QFontComboBox, 
                             QGraphicsItem, QGraphicsPixmapItem,QGraphicsLineItem,    
                             QGraphicsScene, QGraphicsTextItem, QGraphicsView, QGridLayout,
                             QHBoxLayout, QLabel, QMenu, QMessageBox,QPushButton, QSpinBox,
                             QStyle, QTextEdit, QVBoxLayout, QLineEdit, QCheckBox, QComboBox)
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtGui import QFont,QCursor,QFontMetrics,QTransform,QPainter,QPen,QPixmap,QBrush, QImage
from PyQt5.QtPrintSupport import QPrinter,QPrintDialog

MAC = True
InputBySympy=True
try:
    from PyQt5.QtGui import qt_mac_set_native_menubar
except ImportError:
    MAC = False

 
PointSize = 10



class LocationItemDlg(QDialog):

    def __init__(self, item=None, position=None, scene=None, parent=None):
        super(QDialog, self).__init__(parent)
        self.parentForm=parent;
        self.item = item
        self.position = position
        self.scene = scene

        self.ediEquation = QTextEdit()         
        self.ediEquation.setAcceptRichText(True)
        self.ediEquation.setTabChangesFocus(True)
        lblEquation= QLabel("Equations:")
        lblEquation.setBuddy(self.ediEquation)
         
        self.txtLocationName = QLineEdit()           
        lblLocationName = QLabel("LocationName:")
        lblLocationName.setBuddy(self.txtLocationName)
        
        self.isNameAbove=QCheckBox()
        lblIsNameAbove=QLabel("IsNameAbove")
        lblIsNameAbove.setBuddy(self.isNameAbove)
        
        self.isInitial=QCheckBox()
        lblIsInitial=QLabel("IsInitial")
        lblIsInitial.setBuddy(self.isInitial)
        
        self.isEnd=QCheckBox()
        lblIsEnd=QLabel("IsEnd")
        lblIsEnd.setBuddy(self.isEnd)
        
        self.txtInvariant = QLineEdit()           
        lblInvariant = QLabel("Invariant:")
        lblInvariant.setBuddy(self.txtInvariant)
        
        self.figEquation = Figure(figsize=(3, 1))        
        self.canvEquation  = FigureCanvas(self.figEquation) 
        
        lblCanvEquation = QLabel("Format(Equations):")
        lblCanvEquation.setBuddy(self.canvEquation)
        
        self.ediSymEquation = QTextEdit()         
        self.ediSymEquation.setAcceptRichText(True)
        self.ediSymEquation.setTabChangesFocus(False)
        lblSymEquation= QLabel("Sympy(Equations):")
        lblSymEquation.setBuddy(self.ediSymEquation)
       
       
       
        self.txtCheckPointSeq = QLineEdit()           
        lblCheckPointSeq = QLabel("CheckPoint Seq:")
        lblCheckPointSeq.setBuddy(self.txtCheckPointSeq)
        
        
        self.cmbVariableName=QComboBox()        
        self.dicVariableList=[ key for key in parent.dicVariable.keys() if parent.dicVariable[key].isConstant ==False]
         
        self.cmbVariableName.addItems(self.dicVariableList)
        lblVariableName = QLabel("variableName:")
        lblVariableName.setBuddy(self.cmbVariableName) 
        
        
        self.txtValue = QLineEdit()           
        lblValue = QLabel("Value:")
        lblValue.setBuddy(self.txtValue)
        
        btnAddCheckPoint=QPushButton("&Save CheckPoint")
        btnAddCheckPoint.clicked.connect(self.SaveCheckPoint)
        
        
        btnRemoveCheckPoint=QPushButton("&Remove CheckPoint")
        btnRemoveCheckPoint.clicked.connect(self.RemoveCheckPoint)
        
            #self.EdgeWidget.resizeColumnsToContents() 
        self.VariablesWidget = QTableWidget() 
        # setup table widget
        self.VariablesWidget.itemDoubleClicked.connect(self.VariablesWidgetDoubleClicked)
        self.VariablesWidget.setColumnCount(3)
        self.VariablesWidget.setHorizontalHeaderLabels(['Seq','Variable', 'Value'])
    
        #self.figInvariant = Figure(figsize=(5, 0.4))
        
        #self.canvInvariant  = FigureCanvas(self.figInvariant)
 
    
        #lblCanvInvariant = QLabel("&Format(Invariant):")
        #lblCanvInvariant.setBuddy(self.canvInvariant)
        btnDelete=QPushButton("Delete Location")
        btnDelete.clicked.connect(self.delete)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                          QDialogButtonBox.Cancel)
        #self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.isNameAbove.setChecked(True)
        if self.item is not None:
            self.ediEquation.setPlainText("\n".join(self.item.equation))
            self.txtLocationName.setText(self.item.boxName)
            self.isInitial.setChecked(self.item.isInitial)            
            self.isEnd.setChecked(self.item.isEnd)
            self.isNameAbove.setChecked(self.item.isNameAbove)
            self.txtInvariant.setText(self.item.invariant)
            self.SetVariableWdigetAll(self.item.checkPoints)


        layout = QGridLayout()
        layout.addWidget(lblEquation, 0, 0)
        layout.addWidget(self.ediEquation, 1, 0, 1, 8)
        layout.addWidget(lblLocationName, 2, 0)
        layout.addWidget(self.txtLocationName, 2, 1, 1, 2)
        layout.addWidget(lblIsNameAbove, 2, 3)
        layout.addWidget(self.isNameAbove, 2, 4, 1, 2)        
        layout.addWidget(lblIsInitial, 3, 0) 
        layout.addWidget(self.isInitial, 3, 1 )      
        layout.addWidget(lblIsEnd, 3, 2) 
        layout.addWidget(self.isEnd, 3, 3 )
        layout.addWidget(lblInvariant, 4, 0)
        layout.addWidget(self.txtInvariant,  4, 1, 1, 7)
        
        layout.addWidget(lblCanvEquation, 5, 0)        
        layout.addWidget(self.canvEquation, 6, 0, 3, 8)
        
        layout.addWidget(lblSymEquation, 10, 0)
        layout.addWidget(self.ediSymEquation, 11, 0, 1, 8)
        #layout.addWidget(lblCanvInvariant, 10, 0)                
        #layout.addWidget(self.canvInvariant, 10,1, 1, 5)  
        layout.addWidget(self.buttonBox, 12, 0, 1, 6)    
        layout.addWidget(btnDelete, 12, 7)
        self.setLayout(layout)

        layout.addWidget(lblCheckPointSeq, 13, 0)
        layout.addWidget(self.txtCheckPointSeq, 13, 1)
        layout.addWidget(lblVariableName, 13, 2)
        layout.addWidget(self.cmbVariableName, 13, 3)
        layout.addWidget(lblValue, 13, 4)
        layout.addWidget(self.txtValue, 13, 5)
        
        layout.addWidget(btnAddCheckPoint, 13, 6 )
        layout.addWidget(btnRemoveCheckPoint, 13, 7 )
        
        
        layout.addWidget( self.VariablesWidget, 14, 0, 1, 8)
        
        self.VariablesWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        #self.VariablesWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.VariablesWidget.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.VariablesWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
 
        self.ediEquation.textChanged.connect(self.updateUi)
        self.txtInvariant.textChanged.connect(self.updateUi)
         
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject) 
        self.resize(900, 1000)
        #self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.apply)

        self.setWindowTitle("{0} Location Item".format(
                "Add" if self.item is None else "Edit"))
        self.updateUi()

    def delete(self):  
        self.parentForm.deleteText(self.item)        
        self.parentForm.setDirty()
        QDialog.accept(self)
    
    def updateUi(self):
        self.apply()

    def SetVariableWdigetAll(self, checkPoints):       
        self.VariablesWidget.clearContents()
        self.VariablesWidget.setRowCount(0)     
        for strSeq in sorted(checkPoints.keys()):
        #for key in sorted(mydict.iterkeys()):

            self.AddCheckPoint(checkPoints[strSeq])
    def SaveCheckPoint(self):
        if not self.txtCheckPointSeq.text():
            QMessageBox.question(self,
                            "CheckPoint Seq Is None",
                            "Fail to Save,Please input a CheckPoint Seq!",
                            QMessageBox.Ok )  
            return
        if not self.cmbVariableName.currentText():
            QMessageBox.question(self,
                            "CheckPoint variable Name Is None",
                            "Fail to Save,Please select  a variable name!",
                            QMessageBox.Ok )  
            return
        if not self.txtValue.text():
            QMessageBox.question(self,
                            "CheckPoint Value Is None",
                            "Fail to Save,Please input a CheckPoint Value!",
                            QMessageBox.Ok )  
            return
        checkPoint={
        "boxName":self.txtCheckPointSeq.text(), 
        "VariableName":self.cmbVariableName.currentText(), 
        "Value":self.txtValue.text()}
        self.UpdateCheckPoint(checkPoint)
    def AddCheckPoint(self, checkPoint):
        rowCount=self.VariablesWidget.rowCount()
        
        row_index=self.VariablesWidget.rowCount()
        self.VariablesWidget.insertRow(row_index)
        row_index=row_index
        self.VariablesWidget.setItem(row_index, 0, QTableWidgetItem( checkPoint["boxName"] , 0))        
        self.VariablesWidget.setItem(row_index, 1, QTableWidgetItem( checkPoint["VariableName"] , 0))        
        self.VariablesWidget.setItem(row_index, 2, QTableWidgetItem( checkPoint["Value"] , 0))
        
    def UpdateCheckPoint(self, checkPoint):        
        rowCount=self.VariablesWidget.rowCount()
        for row_index in range(rowCount):
            if self.VariablesWidget.item(row_index, 0).text()== checkPoint["boxName"] :     
                self.VariablesWidget.setItem(row_index, 1, QTableWidgetItem( checkPoint["VariableName"] , 0))        
                self.VariablesWidget.setItem(row_index, 2, QTableWidgetItem( checkPoint["Value"] , 0))
          #ui->tableWidget->resizeRowToContents(curRow)
                return
        self.AddCheckPoint(checkPoint)
    def RemoveCheckPoint(self):
        if not self.txtCheckPointSeq.text():
            QMessageBox.question(self,
                            "CheckPoint Seq Is None",
                            "Fail to Remove,Please input a CheckPoint Seq!",
                            QMessageBox.Ok )  
            return
        rowCount=self.VariablesWidget.rowCount()
        for row_index in range(rowCount):
            if self.VariablesWidget.item(row_index, 0).text()== checkPoint["boxName"] :     
                VariablesWidget.removeRow(row_index)
                return
    def GetCheckPoints(self):
        rowCount=self.VariablesWidget.rowCount()
        checkPoints={}
        for row_index in range(rowCount):
            strCheckPointSeq=self.VariablesWidget.item(row_index, 0).text() 
            if strCheckPointSeq:     
                checkPoints[strCheckPointSeq]={  
        "boxName":strCheckPointSeq, 
        "VariableName":self.VariablesWidget.item(row_index, 1).text() , 
        "Value":self.VariablesWidget.item(row_index, 2).text() }
        return checkPoints
    def VariablesWidgetDoubleClicked(self, item):
        self.txtCheckPointSeq.setText(self.VariablesWidget.item(item.row(), 0).text()) 
        self.cmbVariableName.setCurrentIndex(self.dicVariableList.index(self.VariablesWidget.item(item.row(), 1).text()))       
        self.txtValue.setText(self.VariablesWidget.item(item.row(), 2).text())
        
    

    def accept(self):
        iEditLine=self.ediEquation.document().lineCount(); 
        equation=[self.ediEquation.document().findBlockByLineNumber(i).text() for i in range(iEditLine)]     
        tmpLocationName=self.txtLocationName.text()     
        if (tmpLocationName==""):
            QMessageBox.question(self,
                            "Please Input Location Name",
                            "Fail to Accept,Please Input a Name for the Location!",
                            QMessageBox.Ok )  
            return;        
        if self.item is None: 
            if (tmpLocationName in self.parentForm.dicText.keys()):
                QMessageBox.question(self,
                            "Location Name Exists",
                            "Fail to Accept,Please Change a Name for the Location due to there is already a location named "+tmpLocationName +"!",
                            QMessageBox.Ok )  
                return
            self.item = LocationItem("",equation,self.txtInvariant.text(), self.position, self.isInitial.isChecked(), self.isEnd.isChecked(), self.isNameAbove.isChecked(), {}, self.scene, self.parentForm)
        if (self.item.boxName==""):
            self.item.boxName=self.txtLocationName.text()
        else:
            if (self.item.boxName!=self.txtLocationName.text()):
                if (tmpLocationName in self.parentForm.dicText.keys()):
                    QMessageBox.question(self,
                            "Location Name Exists",
                            "Fail to Accept,Please Change a Name for the Location due to there is already a location named "+tmpLocationName +"!",
                            QMessageBox.Ok )  
                    return
                self.parentForm.dicText.pop(self.item.boxName)                
                self.item.boxName=self.txtLocationName.text()
        self.parentForm.dicText[self.item.boxName]=self.item
        self.item.equation=equation
        self.item.invariant=self.txtInvariant.text()
        self.item.isInitial=self.isInitial.isChecked()
        self.item.isEnd=self.isEnd.isChecked()
        self.item.isNameAbove=self.isNameAbove.isChecked()
        self.item.checkPoints=self.GetCheckPoints()
        self.item.update() 
        self.parentForm.setDirty()
        QDialog.accept(self)
    
    def apply(self):
        
        #formula = #r'$x=\frac{3}{100}$'
        iEditLine=self.ediEquation.document().lineCount();
        iHeight=1;
        if (iEditLine>4):
            iHeight=0.2*(iEditLine-4)+1;
            self.figEquation.set_size_inches(5, iHeight)
        self.figEquation.clf()
        SympyLines=[]
        try:       
            for i in range(iEditLine):
                strData=self.ediEquation.document().findBlockByLineNumber(i).text()     
                try:  
            #if True:
                    if '=' in strData:
                        strLeftEquation, strRightEquation=FormatParseLatex.formatParseLatex4Design(strData)
                        SympyLines.append('='.join([strLeftEquation,  strRightEquation]))
                        self.figEquation.text(0.1,iHeight-0.2*(i+1), strData, fontsize=10)
       
                except Exception as e  : 
            #else:
                    SympyLines.append(strData+"Error:"+str(e))
                    print (str(e))
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                         
            self.ediSymEquation.setPlainText("\n".join(SympyLines))
            self.canvEquation.draw()
        except:
            print("")
        #self.figInvariant.clf()
        #self.figInvariant.text(0.1,0.2, self.txtInvariant.text(),family="Consolas",  fontsize=16)
        #self.canvInvariant.draw()
        
 



class LocationItem(QGraphicsItem): 
    def __init__(self, boxName, equation, invariant, position, isInitial, isEnd, isNameAbove, checkPoints, scene,parentForm,size=None, style=Qt.SolidLine,
                  matrix=QTransform()):  
        super(LocationItem, self).__init__()
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable|
                      QGraphicsItem.ItemIsFocusable)
       
        if isinstance(boxName, dict ):            
            equation=boxName["equation"]
            position= QPointF(boxName["position"][0], boxName["position"][1])
            invariant=boxName["invariant"]
            isInitial=boxName["isInitial"]    
            if "isEnd" in boxName.keys():
                isEnd=boxName["isEnd"]
            else:
                isEnd=False
            if "checkPoints" in boxName.keys():
                checkPoints=boxName['checkPoints']
            else:
                checkPoints={}
            isNameAbove=boxName["isNameAbove"]
            size=QSizeF(boxName["size"][0], boxName["size"][1]) 
            boxName=boxName["boxName"]
        rect = QRectF(-10 * PointSize, -PointSize, 20 * PointSize,
                          2 * PointSize)
        rect.setBottom(100)
        rect.setRight(100)
        if size is not None:
            rect = QRectF(QPointF(-10 * PointSize, -PointSize),size)
        self.parentForm=parentForm
        self.equation=equation
        self.invariant=invariant
        self.isInitial=isInitial
        self.isEnd=isEnd
        self.isNameAbove=isNameAbove
        self.boxName=boxName
        self.checkPoints=checkPoints  
        self.rect = rect
        self.style = style
        self.setPos(position)
        self.setTransform(matrix)
        self.imageEquation=self.getQImage4Equation()
        self.imageInvariant=self.getQImage4Invariant()    
        scene.clearSelection()
        scene.addItem(self)
        self.setSelected(True)
        self.setFocus()
        self._edges={}
        global Dirty
        Dirty = True 
        self.mouseMove=False
        self.mousePress=False
    def rePaint (self): 
        self.imageEquation=self.getQImage4Equation()      
        
    def getQImage4Equation(self ):
        iEditLine=len(self.equation);
        iHeight=1.0;
        iWidth=2.5 
        #if (iEditLine>4):
        #    iHeight=0.2*(iEditLine-4)+1; 
        if hasattr(self,'rect'):
            # if self.rect.height()>100:
            #    iHeight=self.rect.height()/100.0
            if self.rect.width() >200:
                iWidth=2.5*self.rect.width()/200
            
        InvariantFig = Figure(figsize=(iWidth, iHeight))        
        canvas  = FigureCanvas(InvariantFig)  
        SympyLines=[]
        for i in range(iEditLine):
            strData=self.equation[i]   
            try:
                if '=' in strData:
                    str1=strData.split('=')
                    leftEquation=str1[0].replace('$', '')
                    rightEquation=str1[1].replace('$', '')
                    strLeftEquation=str( process_sympy(leftEquation))
                    strRightEquation=str( process_sympy(rightEquation)   )                     
                    SympyLines.append('='.join([strLeftEquation,  strRightEquation]))
                    InvariantFig.text(0.1,iHeight-0.2*(i+1), strData, fontsize=10)
            except Exception as e:
                SympyLines.append(strData+"Error:"+str(e))
            #    print (str(e))     
            #try:  
            #    InvariantFig.text(0.1,iHeight-0.2*(i+1), strData,family="Consolas",  fontsize=10)       
            #except:
            #    pass
        canvas.draw()
        size = canvas.size()
        width, height = size.width(), size.height()
        im = QImage(canvas.buffer_rgba(), width, height, QImage.Format_ARGB32)
        return im
        
    def getQImage4Invariant(self):
        InvariantFig = Figure(figsize=(2.5, 0.4))        
        canvas  = FigureCanvas(InvariantFig)   
        strData=self.invariant      
        try:
            InvariantFig.text(0.1,0.3,  strData,family="Consolas",  fontsize=10)       
        except:
            pass
        canvas.draw()
        size = canvas.size()
        width, height = size.width(), size.height()
        im = QImage(canvas.buffer_rgba(), width, height, QImage.Format_ARGB32)
        return im
         
    def toSaveJson(self):
        data={"type":"Location", "boxName":self.boxName, "equation":self.equation,"invariant":self.invariant, 
        "position":(self.x(), self.y()) ,   "isInitial":self.isInitial,  "isEnd":self.isEnd, "isNameAbove":self.isNameAbove, 
        "checkPoints":self.checkPoints, 
        "size":(self.rect.width(), self.rect.height()) ,  "rotation":self.rotation()}
        return data
        #Json.dumps(data)
    def mouseDoubleClickEvent(self, event):
        dialog = LocationItemDlg(self, self.parentWidget(),self.scene, self.parentForm )
        dialog.exec_()
    
    def mousePressEvent(self, event):
        self.mousePress=True
        super(LocationItem, self).mousePressEvent(event)
    def mouseMoveEvent(self, event):        
        super(LocationItem, self).mouseMoveEvent(event)
        if self.mousePress:
            self.mouseMove=True
    def mouseReleaseEvent(self, event):
        
        super(LocationItem, self).mouseReleaseEvent(event)
        if self.mousePress:            
            self.parentForm.RePaintLine()
        self.mouseMove=False
        self.mousePress=False
    @property
    def edgeToSelf(self):
        return self._edgeToSelf

    @edgeToSelf.setter
    def edgeToSelf(self, value):
        if not isinstance(value, str  ):
            raise ValueError('edgeToSelf must be a string!')        
        self._edgeToSelf = value  
  
    @property
    def edges(self):
        return self._edges

    @edges.setter
    def edges(self, value):
        if not isinstance(value, dict ):
            raise ValueError('edges must be a dictionary!')        
        self._edges = value  
    
    @property
    def boxName(self):
        return self._boxName

    @boxName.setter
    def boxName(self, value):
        if not isinstance(value, str ):
            raise ValueError('boxName must be a string!')        
        self._boxName = value
      
    @property
    def isInitial(self):
        return self._isInitial

    @isInitial.setter
    def isInitial(self, value):
        if not isinstance(value, bool ):
            raise ValueError('IsInitial must be a boolean!')        
        self._isInitial = value
    @property
    def isEnd(self):
        return self._isEnd

    @isEnd.setter
    def isEnd(self, value):
        if not isinstance(value, bool ):
            raise ValueError('IsEnd must be a boolean!')        
        self._isEnd = value
    
     
    @property
    def isNameAbove(self):
        return self._isNameAbove

    @isNameAbove.setter
    def isNameAbove(self, value):
        if not isinstance(value, bool ):
            raise ValueError('IsNameAbove must be a boolean!')        
        self._isNameAbove = value
    
    
    @property
    def equation(self):
        return self._equation

    @equation.setter
    def equation(self, value):
        if not isinstance(value, list ):
            raise ValueError('Invariant must be a list!')        
        self._equation = value        
        self.imageEquation=self.getQImage4Equation()
        
    @property
    def checkPoints(self):
        return self._checkPoints

    @checkPoints.setter
    def checkPoints(self, value):
        if not isinstance(value, dict ):
            raise ValueError('checkPoints must be a dict!')        
        self._checkPoints = value         
        
    @property
    def invariant(self):
        return self._invariant

    @invariant.setter
    def invariant(self, value):
        if not isinstance(value, str ):
            raise ValueError('Invariant must be an string!')        
        self._invariant = value        
        self.imageInvariant=self.getQImage4Invariant()
    def parentWidget(self):
        return self.scene().views()[0]


    def boundingRect(self):
        return self.rect.adjusted(-1, -1,  1, 1)
  
  
    def boundingRect2(self):
        return self.rect.adjusted(0, 0,  0, 0)


    def paint(self, painter, option, widget): 
        pen = QPen(self.style)
        pen.setColor(Qt.black)
        pen.setWidth(1)
        if option.state & QStyle.State_Selected:
            pen.setColor(Qt.blue)
        painter.setPen(pen)
      #  painter.drawRect(self.boundingRect())
        painter.drawRect(self.boundingRect2())
        painter.drawImage(self.rect, self.imageEquation)
        pointText=QPointF(self.rect.x(), self.rect.y()-40)
        rectInvariant=QRectF(self.rect.x(), self.rect.y()-35, self.rect.width(), 30)
        pointInvariant=QPointF(self.rect.x(), self.rect.y()-25 )
        if not self.isNameAbove:            
            pointText=QPointF(self.rect.x(), self.rect.y()+self.rect.height()+50)
            rectInvariant=QRectF(self.rect.x(), self.rect.y() +self.rect.height()+5, self.rect.width(), 30)
            pointInvariant=QPointF(self.rect.x(), self.rect.y()+self.rect.height()+15)
        painter.drawText(pointText,  self.boxName)
        painter.drawText(pointInvariant,  self.invariant)
        #painter.drawText(self.rect.x(), self.rect.y()-30, "1-" +self.boxName)
        #painter.drawText(self.rect.x(), self.rect.y()-10, "2-" + self.boxName)
        #painter.drawText(self.rect.x(), self.rect.y()+10, "3-" + self.boxName)
        #painter.drawText(self.rect.x(), self.rect.y()+self.rect.height()+30, "4-" +  self.boxName)
       
       #painter.drawImage(rectInvariant, self.imageInvariant)
        

    def itemChange(self, change, variant):
        if change != QGraphicsItem.ItemSelectedChange:
            global Dirty
            Dirty = True
        
        return QGraphicsItem.itemChange(self, change, variant)


    def contextMenuEvent(self, event):
        wrapped = []
        menu = QMenu(self.parentWidget())
        for text, param in (
                ("&Solid", Qt.SolidLine),
                ("&Dashed", Qt.DashLine),
                ("D&otted", Qt.DotLine),
                ("D&ashDotted", Qt.DashDotLine),
                ("DashDo&tDotted", Qt.DashDotDotLine)):
            wrapper = functools.partial(self.setStyle, param)
            wrapped.append(wrapper)
            menu.addAction(text, wrapper)
        menu.exec_(event.screenPos())


    def setStyle(self, style):
        self.style = style
        self.update()
        global Dirty
        Dirty = True


    def keyPressEvent(self, event):
        factor = PointSize / 4
        changed = False
        if event.modifiers() & Qt.ShiftModifier:
            if event.key() == Qt.Key_Left:
                self.rect.setRight(self.rect.right() - factor)
                changed = True
            elif event.key() == Qt.Key_Right:
                self.rect.setRight(self.rect.right() + factor)
                changed = True
            elif event.key() == Qt.Key_Up:
                self.rect.setBottom(self.rect.bottom() - factor)
                changed = True
            elif event.key() == Qt.Key_Down:
                self.rect.setBottom(self.rect.bottom() + factor)
                changed = True
        if changed:
            #self.rePaint()
            self.update()
            global Dirty
            Dirty = True
        else:
            QGraphicsItem.keyPressEvent(self, event)





class LocationItemPixmap(QGraphicsPixmapItem):
    def __init__(self, boxName, equation, position, scene,parentForm,  matrix=QTransform()):
        if isinstance(boxName, dict ):            
            text=boxName["text"]
            position= QPointF(boxName["position"][0], boxName["position"][1]) 
            boxName=boxName["boxName"]
        pixmap=self.GetPixmap(text)
        super(LocationItem, self).__init__(pixmap)
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable|
                      QGraphicsItem.ItemIsFocusable)
        #self.setTextInteractionFlags(Qt.TextEditorInteraction)
        #self.setFont(font)
        self.setPos(position)
        self.boxName=boxName
        self.setTransform(matrix)
        self.parentForm=parentForm
        scene.clearSelection()
        scene.addItem(self)
        self.setSelected(True)
        global Dirty
        Dirty = True 
        
    def GetPixmap(self, text):
        iEditLine=len(text);
        iHeight=1;
        if (iEditLine>4):
            iHeight=0.2*(iEditLine-4)+1;
        
        InvariantFig = Figure(figsize=(5, iHeight))        
        canvas  = FigureCanvas(InvariantFig)  
        
        for i in range(iEditLine):
            strData=text[i]            
            InvariantFig.text(0.1,iHeight-0.2*(i+1), strData, fontsize=10)       
        canvas.draw()
        size = canvas.size()
        width, height = size.width(), size.height()
        im = QImage(canvas.buffer_rgba(), width, height, QImage.Format_ARGB32)
        return QPixmap(im)
    def toSaveJson(self):
        data={"type":"Text", "boxName":self.boxName, "text":self.toPlainText(),
        "position":(self.x(), self.y()) ,   "font":( self.font().family(), self.font().pointSize()), 
        "rotation":self.rotation()}
        return data
        #Json.dumps(data)
        
    
    @property
    def boxName(self):
        return self._boxName

    @boxName.setter
    def boxName(self, value):
        if not isinstance(value, str ):
            raise ValueError('boxName must be an string!')        
        self._boxName = value
      
    @property
    def isInitial(self):
        return self._isInitial

    @isInitial.setter
    def isInitial(self, value):
        if not isinstance(value, bool ):
            raise ValueError('IsInitial must be an boolean!')        
        self._isInitial = value
    
    
    @property
    def Invariant(self):
        return self._invariant

    @Invariant.setter
    def Invariant(self, value):
        if not isinstance(value, str ):
            raise ValueError('Invariant must be an string!')        
        self._invariant = value
        
    def boundingRect(self) :  
        height=super().boundingRect().height()
        width=super().boundingRect().width()
        if height<100:
            height=100
        if width<100:
            width=100
        return  QRectF(0,0,width, height )  
        
    def parentWidget(self):
        return self.scene().views()[0]

 
 
    def mouseDoubleClickEvent(self, event):
        dialog = LocationItemDlg(self, self.parentWidget(),self.scene, self.parentForm )
        dialog.exec_()
    
    def paint(self, painter, option, widget): 
        super().paint( painter, option, widget)        
        painter.drawRect(self.boundingRect())
    
    def keyPressEvent(self, event):
        factor = PointSize / 4
        changed = False
        if event.modifiers() & Qt.ShiftModifier:
            if event.key() == Qt.Key_Left:
                self.boundingRect().setRight(self.boundingRect().right() - factor)
                changed = True
            elif event.key() == Qt.Key_Right:
                self.boundingRect().setRight(self.boundingRect().right() + factor)
                changed = True
            elif event.key() == Qt.Key_Up:
                self.boundingRect().setBottom(self.boundingRect().bottom() - factor)
                changed = True
            elif event.key() == Qt.Key_Down:
                self.boundingRect().setBottom(self.boundingRect().bottom() + factor)
                changed = True
        if changed:
            self.update()
            global Dirty
            Dirty = True
        else:
            QGraphicsItem.keyPressEvent(self, event)
class LocationItemText(QGraphicsTextItem):    
    def __init__(self, boxName, text, position, scene,parentForm, 
                 font=QFont("Times", PointSize), matrix=QTransform()):
        if isinstance(boxName, dict ):            
            text=boxName["text"]
            position= QPointF(boxName["position"][0], boxName["position"][1])
            font= QFont(boxName["font"][0], boxName["font"][1])
            boxName=boxName["boxName"]
        super(LocationItem, self).__init__(text)
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable)
        #self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFont(font)
        self.setPos(position)
        self.boxName=boxName
        self.setTransform(matrix)
        self.parentForm=parentForm
        scene.clearSelection()
        scene.addItem(self)
        self.setSelected(True)
        global Dirty
        Dirty = True 
        
    def toSaveJson(self):
        data={"type":"Text", "boxName":self.boxName, "text":self.toPlainText(),
        "position":(self.x(), self.y()) ,   "font":( self.font().family(), self.font().pointSize()), 
        "rotation":self.rotation()}
        return data
        #Json.dumps(data)
        
    
    @property
    def boxName(self):
        return self._boxName

    @boxName.setter
    def boxName(self, value):
        if not isinstance(value, str ):
            raise ValueError('boxName must be an string!')        
        self._boxName = value
      
    @property
    def isInitial(self):
        return self._isInitial

    @isInitial.setter
    def isInitial(self, value):
        if not isinstance(value, bool ):
            raise ValueError('IsInitial must be an boolean!')        
        self._isInitial = value
    
    
    @property
    def Invariant(self):
        return self._invariant

    @Invariant.setter
    def Invariant(self, value):
        if not isinstance(value, str ):
            raise ValueError('Invariant must be an string!')        
        self._invariant = value
        
    def boundingRect(self) :  
        height=super().boundingRect().height()
        width=super().boundingRect().width()
        if height<100:
            height=100
        if width<100:
            width=100
        return  QRectF(0,0,width, height )  
        
    def parentWidget(self):
        return self.scene().views()[0]


    def itemChange(self, change, variant):
        if change != QGraphicsItem.ItemSelectedChange:
            global Dirty
            Dirty = True
        '''
        if change== QGraphicsItem.ItemPositionChange:
            if (parentFormvars().has_key('dicLine') ):
                if parentForm.dicLine!=None:
                    lines=[ line for line in  self.dicLine.values() if ( line.fromBox.boxName== self.boxName or line.toBox.boxName==self.boxName)]
                    for line in  lines:
                        line.resetLine();                    
                parentForm.scene.update()
        '''
        return QGraphicsLocationItem.itemChange(self, change, variant)

 
    def mouseDoubleClickEvent(self, event):
        dialog = LocationItemDlg(self, self.parentWidget(),self.scene, self.parentForm )
        dialog.exec_()
    
    def paint(self, painter, option, widget): 
        super().paint( painter, option, widget)        
        painter.drawRect(self.boundingRect())
        
