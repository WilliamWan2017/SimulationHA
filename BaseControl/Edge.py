
import functools
import random
import sys

from BaseControl.Location import LocationItem, LocationItemDlg
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from PyQt5.QtCore import (QByteArray, QDataStream, QFile, QFileInfo,QLineF, QLine, 
                          QIODevice, QPoint, QPointF, QRectF, Qt)
from PyQt5.QtWidgets import (QApplication, QDialog, QFrame, 
                             QDialogButtonBox, QFileDialog, QFontComboBox, 
                             QGraphicsItem, QGraphicsPixmapItem,QGraphicsLineItem,    
                             QGraphicsScene, QGraphicsTextItem, QGraphicsView, QGridLayout,QComboBox, 
                             QHBoxLayout, QLabel, QMenu, QMessageBox,QPushButton, QSpinBox,
                             QStyle, QTextEdit, QVBoxLayout, QLineEdit)
from PyQt5.QtGui import QFont,QCursor,QFontMetrics,QTransform,QPainter,QPen,QPixmap,QBrush, QImage
from PyQt5.QtPrintSupport import QPrinter,QPrintDialog
adjustY=10
adjustX=15
MAC = True
try:
    from PyQt5.QtGui import qt_mac_set_native_menubar
except ImportError:
    MAC = False

   

class ImgWidget(QLabel):
    def __init__(self, pic, parent=None):
        super(ImgWidget, self).__init__(parent)       
        self.setPixmap(pic)
class EdgeItemDlg(QDialog):
    def __init__(self, item=None,  position=None,  scene=None, parent=None):
        super(QDialog, self).__init__(parent)
        self.parentForm=parent;
        self.item = item
        self.position = position
        self.scene = scene
        
        self.fromLocation=QComboBox()        
        self.dicTextKeyList=[key for key in parent.dicText.keys()]
        self.fromLocation.addItems(self.dicTextKeyList)
        fromLocationLabel = QLabel("&fromLocation:")
        fromLocationLabel.setBuddy(self.fromLocation) 
        
        
        
        self.toLocation =QComboBox()        
        self.toLocation.addItems(self.dicTextKeyList)
        ToLocationLabel = QLabel("&ToLocation:")
        ToLocationLabel.setBuddy(self.toLocation ) 
        
        self.LocationName = QLineEdit()     
        LocationNameLabel = QLabel("&EdgeName:")
        LocationNameLabel.setBuddy(self.LocationName)
        
        
        self.txtGuard = QLineEdit()     
        GuardLabel = QLabel("&Guard:")
        GuardLabel.setBuddy(self.txtGuard)
        
        
        self.txtReset = QLineEdit()     
        ResetLabel = QLabel("&Reset:")
        ResetLabel.setBuddy(self.txtReset)  
        
        self.figGuard = Figure(figsize=(2.5, 0.4))
        
        self.canvGuard  = FigureCanvas(self.figGuard)
    
        lblCanvGuard = QLabel("&Format(Guard):")
        lblCanvGuard.setBuddy(self.canvGuard)
        
             
        self.figReset = Figure(figsize=(2.5, 0.4))        
        self.canvReset  = FigureCanvas(self.figReset) 
        
        lblCanvReset = QLabel("&Format(Reset):")
        lblCanvReset.setBuddy(self.canvReset)
        
        self.buttonLocation = QDialogButtonBox(QDialogButtonBox.Ok|
                                          QDialogButtonBox.Cancel)
        self.buttonLocation.button(QDialogButtonBox.Ok).setEnabled(False)
        btnDelete=QPushButton("Delete Edge")
        btnDelete.clicked.connect(self.delete)
      
      

        layout = QGridLayout()
        layout.addWidget(fromLocationLabel, 0, 0)
        layout.addWidget(self.fromLocation, 0, 1, 1, 1)
        layout.addWidget(ToLocationLabel, 1, 0)
        layout.addWidget(self.toLocation , 1, 1, 1, 1) 
        layout.addWidget(self.LocationName, 2, 1, 1, 2)
        layout.addWidget(LocationNameLabel, 2, 0)
        layout.addWidget(self.txtGuard, 3, 1, 1, 5)
        layout.addWidget(GuardLabel, 3, 0)
        layout.addWidget(self.txtReset, 4, 1, 1, 5)
        layout.addWidget(ResetLabel, 4, 0)
        
        
        #layout.addWidget(self.canvGuard, 5, 1, 1, 5)
        #layout.addWidget(lblCanvGuard, 5, 0)
        #layout.addWidget(self.canvReset,6, 1, 1, 5)
        #layout.addWidget(lblCanvReset, 6, 0)     
        
        
        layout.addWidget(self.buttonLocation, 7, 0, 1, 5)    
        layout.addWidget(btnDelete, 7, 5)    
        
        
        self.setLayout(layout)  
        if self.item is not None:
            #self.fromLocation.setEditText (self.item.fromLocation.boxName) 
            #self.toLocation.setEditText (self.item.toLocation.boxName) 
            self.fromLocation.setCurrentIndex(self.dicTextKeyList.index(self.item.fromLocation.boxName))
            self.toLocation.setCurrentIndex(self.dicTextKeyList.index(self.item.toLocation.boxName))
            self.LocationName.setText(self.item.boxName)
            self.txtGuard.setText(self.item.guard)
            self.txtReset.setText(self.item.reset)
        self.toLocation .editTextChanged.connect(self.updateUi)
        self.fromLocation.editTextChanged.connect(self.updateUi)
        self.toLocation .currentIndexChanged.connect(self.updateUi)
        self.fromLocation.currentIndexChanged.connect(self.updateUi)
        self.LocationName.textChanged.connect(self.updateUi)
        self.txtGuard.textChanged.connect(self.updateUi)
        self.txtReset.textChanged.connect(self.updateUi)
        self.buttonLocation.accepted.connect(self.accept)
        self.buttonLocation.rejected.connect(self.reject)


        self.buttonLocation.accepted.connect(self.accept)
        self.buttonLocation.rejected.connect(self.reject)

        self.setWindowTitle("Page Designer - {0} Linkline Item".format(
                "Add" if self.item is None else "Line"))
        self.updateUi()


    
    def delete(self):       
        self.parentForm.deleteLine(self.item)                
        self.parentForm.setDirty()        
        QDialog.accept(self)
    def updateUi(self):
        self.buttonLocation.button(QDialogButtonBox.Ok).setEnabled(
                bool(self.LocationName.text()))
        self.apply()


    def apply(self):       
        return
        self.figGuard.clf()
        try:
            self.figGuard.text(0.1,0.2, self.txtGuard.text(), family="Consolas",  fontsize=16)
        except:
            pass
        self.canvGuard.draw()
        self.figReset.clf()
        try:
            self.figReset.text(0.1,0.2, self.txtReset.text(), family="Consolas", fontsize=16)
        except:
            pass
        self.canvReset.draw()
    def accept(self):
        if (self.fromLocation.currentText()==""):
            QMessageBox.question(self,
                            "Please Select FromLocation Name",
                            "Fail to Accept,Please Select FromLocation Name!",
                            QMessageBox.Ok )  
            return;    
        if (self.toLocation.currentText()==""):
            QMessageBox.question(self,
                            "Please Select ToLocation Name",
                            "Fail to Accept,Please Select ToLocation Name!",
                            QMessageBox.Ok )  
            return;     
        tmpLocationName=self.LocationName.text()     
        if (tmpLocationName==""):
            QMessageBox.question(self,
                            "Please Input Edge Name",
                            "Fail to Accept,Please Input a Name for the Edge!",
                            QMessageBox.Ok )  
            return;     
        if self.item is None:
            if (tmpLocationName in self.parentForm.dicLine.keys()):
                QMessageBox.question(self,
                            "Edge Name Exists",
                            "Fail to Accept,Please Change a Name for this Edge due to there is already an edge named "+tmpLocationName +"!",
                            QMessageBox.Ok )  
                return
            self.item = EdgeItem(self.LocationName.text(), None,None, "","",  self.scene, self.parentForm)  
            self.parentForm.addEdgeInTable(self.item)
        else:
            if (self.item.boxName!=tmpLocationName):
                if (tmpLocationName in self.parentForm.dicLine.keys()):
                    QMessageBox.question(self,
                            "Edge Name Exists",
                            "Fail to Accept,Please Change a Name for this Edge due to there is already an edge named "+tmpLocationName +"!",
                         QMessageBox.Ok )  
                    return
                self.parentForm.dicLine.pop(self.item.boxName)
        self.item.fromLocation=self.parentForm.dicText[self.fromLocation.currentText()]
        self.item.toLocation=self.parentForm.dicText[self.toLocation .currentText()]
        self.item.boxName=self.LocationName.text()
        self.item.guard=self.txtGuard.text()
        self.item.reset=self.txtReset.text()
        self.item.update()
        self.parentForm.dicLine[self.item.boxName]=self.item
        self.parentForm.setEdgeInTable(self.item)        
        self.parentForm.setDirty()
        QDialog.accept(self)

class EdgeItem(QGraphicsLineItem):
    def __init__(self, boxName,   fromLocation,toLocation, guard, reset, scene,parentForm,   style=Qt.SolidLine,
                 rect=None, matrix=QTransform()):
        super(EdgeItem, self).__init__() 
        
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable|
                      QGraphicsItem.ItemIsFocusable)
        self.style = style
        self.boxName=boxName
        self.guard=guard
        self.reset=reset
        self._fromLocation=None
        self._toLocation=None
        if fromLocation==None:
            x1=10
            y1=10        
        else:
            x1=fromLocation.rect.right()
            y1=fromLocation.rect.top()+fromLocation.rect.height()*0.3
        if toLocation==None:
            x2=100
            y2=100        
        else:
            x2=toLocation.rect.left()
            y2=toLocation.rect.top()+fromLocation.rect.height()*0.3
        self.parentForm=parentForm
        self.source = QPointF(x1, y1)
        self.dest = QPointF(x2, y2) 
        self.fromLocation=fromLocation
        self.toLocation=toLocation
        self.direction="a"
        self.myColor = Qt.black
        self.setPen(QPen(self.myColor, 2, Qt.SolidLine,
                Qt.RoundCap, Qt.RoundJoin))
        self.line = QLineF(self.source, self.dest)
        self.line.setLength(self.line.length() - 5)      
        self.resetLine()
        self.scene=scene
        scene.clearSelection()
        scene.addItem(self)
        self.setSelected(True)
        self.setFocus()             
        global Dirty
        Dirty = True 
    def drawLine2Self(self):
        haveEdges=[strDirection   for strDirection in self.fromLocation.edges.values()]
        self.arcx1=self.fromLocation.x()-self.fromLocation.rect.width()/2-40#-30
        self.arcy1=self.fromLocation.y()# -50#+self.fromLocation.rect.height*0.3 
        self.minAngle=90 
        x1=self.arcx1+33
        y1=self.arcy1+80
        x2=self.arcx1+40
        y2=self.arcy1+80            
        self.arcTextx=self.arcx1
        self.arcTexty=self.arcy1+40
        self.spanAngle=180 
        if "top" not in haveEdges and self.fromLocation.isNameAbove:
            self.arcx1=self.fromLocation.x()-40
            self.arcy1=self.fromLocation.y() -40-adjustY
            x1=self.arcx1+80
            y1=self.arcy1+40-7
            x2=self.arcx1+80
            y2=self.arcy1+40
            self.minAngle=0 
            self.arcTextx=self.arcx1+40
            self.arcTexty=self.arcy1 
        elif "left" not in haveEdges:
            self.arcx1=self.fromLocation.x()-self.fromLocation.rect.width()/2-40#-30
            self.arcy1=self.fromLocation.y()# -50#+self.fromLocation.rect.height*0.3 
            self.minAngle=90 
            x1=self.arcx1+33
            y1=self.arcy1+80
            x2=self.arcx1+40
            y2=self.arcy1+80            
            self.arcTextx=self.arcx1
            self.arcTexty=self.arcy1+40
        elif "bottom" not in haveEdges  and self.fromLocation.isNameAbove==False:
            self.arcx1=self.fromLocation.x()-40
            self.arcy1=self.fromLocation.y()+self.fromLocation.rect.height()-adjustY-40
            self.minAngle=180         
            x1=self.arcx1+80
            y1=self.arcy1+7+40
            x2=self.arcx1+80
            y2=self.arcy1+40            
            self.arcTextx=self.arcx1+40
            self.arcTexty=self.arcy1 +80
        elif "right" not in haveEdges:
            self.arcx1=self.fromLocation.x()+self.fromLocation.rect.width()/2-25-adjustX #-30
            self.arcy1=self.fromLocation.y()# -50#+self.fromLocation.rect.height*0.3 
            self.minAngle=270 
            x1=self.arcx1+7+25+adjustX
            y1=self.arcy1+80
            x2=self.arcx1+25+adjustX
            y2=self.arcy1+80            
            self.arcTextx=self.arcx1+80
            self.arcTexty=self.arcy1+40
        self.source = QPointF(x1, y1)
        self.dest = QPointF(x2, y2)         
        self.line = QLineF(self.source, self.dest)
        self.line.setLength(self.line.length() - 5)      
#if 'time' not in listOfStrings :
  #  print("Yes, 'time' NOT found in List : " , listOfStrings)
    
    def getQPixmap4Guard(self):
        guardFig = Figure(figsize=(5, 0.4))        
        canvas  = FigureCanvas(guardFig)   
        strData=self.guard         
        try:
            guardFig.text(0.1,0.3,  strData,family="Consolas",  fontsize=10)       
        except:
            pass
        canvas.draw()
        size = canvas.size()
        width, height = size.width(), size.height()
        im = QImage(canvas.buffer_rgba(), width, height, QImage.Format_ARGB32)
        return QPixmap(im)
        
    def getQPixmap4Reset(self):
        guardFig = Figure(figsize=(5, 0.4))        
        canvas  = FigureCanvas(guardFig)   
        strData=self.reset            
        try:
            guardFig.text(0.1,0.3,  strData, family="Consolas", fontsize=10)       
        except:
            pass
        canvas.draw()
        size = canvas.size()
        width, height = size.width(), size.height()
        im = QImage(canvas.buffer_rgba(), width, height, QImage.Format_ARGB32)
        return QPixmap(im)
        
    
    def resetLine(self):
        if self.fromLocation==None and  self.toLocation==None:
            return 
        
        if  self.fromLocation==None:            
            #self.toLocation.edges[self.boxName]="left"
            x2= self.toLocation.x()
            y2= self.toLocation.y()+self.toLocation.rect.height()*0.3
            x1=x2-30
            y1=y2
        elif self.toLocation==None:
            #self.fromLocation.edges[self.boxName]="right"
            x1= self.fromLocation.x()+self.fromLocation.rect.width()
            y1= self.fromLocation.y()+self.fromLocation.rect.height()*0.3
            x2=x1+30
            y2=y1 
        else:
            if self.fromLocation.boxName==self.toLocation.boxName:
                self.drawLine2Self()
                self.fromLocation.edgeToSelf=self.boxName;
                return
            x_diff=self.toLocation.x()-self.fromLocation.x()
            y_diff=self.toLocation.y()-self.fromLocation.y()
            x_diff_standand=(self.fromLocation.rect.width()+self.toLocation.rect.width())/2
            y_diff_standand=(self.fromLocation.rect.height()+self.toLocation.rect.height())/2
            if ((abs(y_diff)<y_diff_standand)):
                if x_diff>0:         
                 
                    self.direction="x>"   
                    
                    self.fromLocation.edges[self.boxName]="right"            
                    self.toLocation.edges[self.boxName]="left"
                    x1= self.fromLocation.x()+self.fromLocation.rect.width()/2
                    y1= self.fromLocation.y()+self.fromLocation.rect.height()*0.33 -adjustY    
                    x2= self.toLocation.x()-self.toLocation.rect.width()/2
                    y2= self.toLocation.y()+self.toLocation.rect.height()*0.33-adjustY
                else:        
                    self.direction="x<"                       
                    self.fromLocation.edges[self.boxName]="left"            
                    self.toLocation.edges[self.boxName]="right"
                    x1= self.fromLocation.x()-self.fromLocation.rect.width()/2
                    y1= self.fromLocation.y()+self.fromLocation.rect.height()*0.67 -adjustY       
                    x2= self.toLocation.x()+self.toLocation.rect.width()/2
                    y2= self.toLocation.y()+self.toLocation.rect.height()*0.67-adjustY
            elif ((abs(x_diff)<x_diff_standand)):
                if (y_diff>0):
                    self.direction="y>"   
                    
                    self.fromLocation.edges[self.boxName]="bottom"            
                    self.toLocation.edges[self.boxName]="top"
                    x1= self.fromLocation.x()-self.fromLocation.rect.width()*0.25          
                    y1= self.fromLocation.y()+self.fromLocation.rect.height()-adjustY
                    x2= self.toLocation.x()-self.toLocation.rect.width()*0.25          
                    y2= self.toLocation.y()-adjustY
                else:
                    self.direction="y<"      
       
                    self.fromLocation.edges[self.boxName]="top"            
                    self.toLocation.edges[self.boxName]="bottom"             
                    x1= self.fromLocation.x()+self.fromLocation.rect.width()*0.25
                    y1= self.fromLocation.y()-adjustY
                    x2= self.toLocation.x()+self.toLocation.rect.width()*0.25       
                    y2= self.toLocation.y() +self.toLocation.rect.height()-adjustY
            else:
                if (x_diff>0) and (y_diff>0):
                    self.direction="xy>"         
                    self.fromLocation.edges[self.boxName]="right"            
                    self.toLocation.edges[self.boxName]="top"         
                    x1=self.fromLocation.x()+self.fromLocation.rect.width()/2
                    y1=self.fromLocation.y()+self.fromLocation.rect.height()*0.87-adjustY
                    x2=self.toLocation.x()-self.toLocation.rect.width()*0.37
                    y2=self.toLocation.y()-adjustY
                elif ((x_diff<0) and (y_diff<0)):                
                    self.direction="xy<"            
             
                    self.fromLocation.edges[self.boxName]="left"            
                    self.toLocation.edges[self.boxName]="bottom"                
                    x1=self.fromLocation.x()-self.fromLocation.rect.width()/2
                    y1=self.fromLocation.y()+self.fromLocation.rect.height()*0.13-adjustY
                    x2=self.toLocation.x()+self.toLocation.rect.width()*0.37
                    y2=self.toLocation.y()+self.toLocation.rect.height()-adjustY 
                elif (x_diff>0) and (y_diff<0):
                    self.direction="x>y<"                   
                    
                    self.fromLocation.edges[self.boxName]="top"            
                    self.toLocation.edges[self.boxName]="left"          
                    x1=self.fromLocation.x()+self.fromLocation.rect.width()*0.37
                    y1=self.fromLocation.y()-adjustY
                    x2=self.toLocation.x()-self.fromLocation.rect.width()*0.5
                    y2=self.toLocation.y()+self.toLocation.rect.height()*0.87-adjustY
                else:
                    self.direction="x<y>"            
                    self.fromLocation.edges[self.boxName]="bottom"            
                    self.toLocation.edges[self.boxName]="right"             
                    x1=self.fromLocation.x() -self.fromLocation.rect.width()*0.37
                    y1=self.fromLocation.y()+self.fromLocation.rect.height()-adjustY
                    x2=self.toLocation.x()+self.toLocation.rect.width()/2
                    y2=self.toLocation.y()+self.toLocation.rect.height()*0.13    -adjustY            
        self.source = QPointF(x1, y1)
        self.dest = QPointF(x2, y2)         
        self.line = QLineF(self.source, self.dest)
        self.line.setLength(self.line.length() - 5)      
    @property
    def boxName(self):
        return self._boxName

    @boxName.setter
    def boxName(self, value):
        if not isinstance(value, str ):
            raise ValueError('EdgeName must be an string!')        
        self._boxName = value
    
    
    @property        
    def guard(self):
        return self._guard

    @guard.setter
    def guard(self, value):
        if not isinstance(value, str ):
            raise ValueError('EdgeName must be an string!')        
        self._guard = value
        
    @property
    def reset(self):
        return self._reset

    @reset.setter
    def reset(self, value):
        if not isinstance(value, str ):
            raise ValueError('EdgeName must be an string!')        
        self._reset = value
    
    def toSaveJson(self):
        data={"type":"Edge", "boxName":self.boxName, "strFromLocation":self.fromLocation.boxName,
        "strToLocation":self.toLocation.boxName ,"guard":self.guard, "reset":self.reset,    "style":self.style , "rotation":self.rotation()}
        
        return data 
     
    @property
    def fromLocation(self):
        return self._fromLocation 

    @fromLocation.setter
    def fromLocation(self, value):
        if value!=None:
            if not isinstance(value, LocationItem ):
                raise ValueError('LocationName must be a  LocationItem!')        
            self._fromLocation = value        
            self.resetLine()
    @property
    def toLocation(self):
        return self._toLocation 

    @toLocation.setter
    def toLocation(self, value):
        if value!=None:
            if not isinstance(value, LocationItem ):
                raise ValueError('LocationName must be a LocationItem!')        
            self._toLocation = value        
            self.resetLine()
     
        
    def parentWidget(self):
        return self.scene.views()[0]


    def itemChange(self, change, variant):
        if change != QGraphicsItem.ItemSelectedChange:
            global Dirty
            Dirty = True
        return QGraphicsLineItem.itemChange(self, change, variant)


    def mouseDoubleClickEvent(self, event):
        dialog = edgeItemDlg(self, self.parentWidget(), self.parentWidget(),self.scene, self.parentForm )
        dialog.exec_()
     
    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
        # setPen
        pen = QPen()
        pen.setWidth(1)
        pen.setJoinStyle(Qt.MiterJoin) #让箭头变尖
        QPainter.setPen(pen)

        # draw line
        QPainter.drawLine(self.line)
        ptextx=(self.line.x1()+self.line.x2())/2
        ptexty=(self.line.y1()+self.line.y2())/2
        ptexty-=5
        ptextx-=len(self.boxName)*3
        
        #Painter.drawText(QPointF(ptextx, ptexty+20), self.direction)
        # setBrush
        brush = QBrush()
        brush.setColor(Qt.black)
        brush.setStyle(Qt.SolidPattern)
        QPainter.setBrush(brush)

        v = self.line.unitVector()
        v.setLength(5)
        v.translate(QPointF(self.line.dx(), self.line.dy()))

        n = v.normalVector()
        n.setLength(n.length() * 0.5)
        n2 = n.normalVector().normalVector()

        p1 = v.p2()
        p2 = n.p2()
        p3 = n2.p2()

        # 方法1
        QPainter.drawLine(self.line)
        QPainter.drawPolygon(p1, p2, p3)
        
        
 
        if self.fromLocation is not None and self.toLocation is not  None:
            if self.fromLocation.boxName==self.toLocation.boxName:
                QPainter.drawArc(self.arcx1, self.arcy1, 80, 80, self.minAngle*16, self.spanAngle*16)                     
                ptextx=self.arcTextx
                ptexty=self.arcTexty
                #QPainter.drawArc(self.arcx1, self.arcy1+100, 50, 50, 270*16, 89*16)      
 
                #QPainter.drawArc(self.arcx1, self.arcy1+200, 50, 50, 0*16, 89*16)   
 
                #QPainter.drawArc(self.arcx1, self.arcy1+300, 50, 50, 270*16, 180*16)   
 
                #QPainter.drawArc(self.arcx1, self.arcy1+400, 50, 50, 270*16, 270*16)   
                #QPainter.drawArc(self.arcx1, self.arcy1+500, 50, 50, 180*16, 89*16)                  
               
        QPainter.drawText(QPointF(ptextx, ptexty),   self.boxName)
       
        #QPainter.drawRect(self.arcx1, self.arcy1, 50, 50)
        self.scene.update()

        # 方法2
        # arrow = QPolygonF([p1, p2, p3, p1])
        # path = QPainterPath()
        # path.moveTo(self.source)
        # path.lineTo(self.dest)
        # path.addPolygon(arrow)
        # QPainter.drawPath(path)
        
