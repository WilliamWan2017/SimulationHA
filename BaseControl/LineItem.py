
import functools
import random
import sys

from PyQt5.QtCore import (QByteArray, QDataStream, QFile, QFileInfo,QLineF, QLine, 
                          QIODevice, QPoint, QPointF, QRectF, Qt)
from PyQt5.QtWidgets import (QApplication, QDialog, QFrame, 
                             QDialogButtonBox, QFileDialog, QFontComboBox, 
                             QGraphicsItem, QGraphicsPixmapItem,QGraphicsLineItem,    
                             QGraphicsScene, QGraphicsTextItem, QGraphicsView, QGridLayout,QComboBox, 
                             QHBoxLayout, QLabel, QMenu, QMessageBox,QPushButton, QSpinBox,
                             QStyle, QTextEdit, QVBoxLayout, QLineEdit)
from PyQt5.QtGui import QFont,QCursor,QFontMetrics,QTransform,QPainter,QPen,QPixmap,QBrush
from PyQt5.QtPrintSupport import QPrinter,QPrintDialog

MAC = True
try:
    from PyQt5.QtGui import qt_mac_set_native_menubar
except ImportError:
    MAC = False

 
class QBoxList(QComboBox):
    def __init__(self, parent=None):
        super(QComboBox, self).__init__(parent)
        self.addItems([key for key in parent.dicText.keys()])
        #self.item=parent.dicText.keys();


class LineItemDlg(QDialog):
    def __init__(self, item=None,  position=None,  scene=None, parent=None):
        super(QDialog, self).__init__(parent)
        self.parentForm=parent;
        self.item = item
        self.position = position
        self.scene = scene
        
        self.FromBox=QBoxList(self.parentForm)  
        FromBoxLabel = QLabel("&FromBox:")
        FromBoxLabel.setBuddy(self.FromBox) 
        
        
        
        self.ToBox=QBoxList(self.parentForm)  
        ToBoxLabel = QLabel("&ToBox:")
        ToBoxLabel.setBuddy(self.ToBox) 
        
        self.boxName = QLineEdit()     
        BoxNameLabel = QLabel("&LineName:")
        BoxNameLabel.setBuddy(self.boxName)
        
        
        self.txtGuard = QLineEdit()     
        GuardLabel = QLabel("&Guard:")
        GuardLabel.setBuddy(self.txtGuard)
        
        
        self.txtReset = QLineEdit()     
        ResetLabel = QLabel("&Reset:")
        ResetLabel.setBuddy(self.txtReset)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                          QDialogButtonBox.Cancel)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        if self.item is not None:
            self.fromBox.currentText(self.item.fromBox.boxName) 
            self.toBox.currentText(self.item.toBox.boxName) 
            self.boxName.setText(self.item.boxName)

        layout = QGridLayout()
        layout.addWidget(FromBoxLabel, 0, 0)
        layout.addWidget(  self.FromBox, 0, 1, 1, 1)
        layout.addWidget(ToBoxLabel, 1, 0)
        layout.addWidget(self.ToBox, 1, 1, 1, 1) 
        layout.addWidget(self.buttonBox, 5, 0, 1, 6)    
        layout.addWidget(self.boxName, 2, 1, 1, 2)
        layout.addWidget(BoxNameLabel, 2, 0)
        layout.addWidget(self.txtGuard, 3, 1, 1, 2)
        layout.addWidget(GuardLabel, 3, 0)
        layout.addWidget(self.txtReset, 4, 1, 1, 2)
        layout.addWidget(ResetLabel, 4, 0)
        
        self.setLayout(layout)  
        self.ToBox.editTextChanged.connect(self.updateUi)
        self.FromBox.editTextChanged.connect(self.updateUi)
        self.ToBox.currentIndexChanged.connect(self.updateUi)
        self.FromBox.currentIndexChanged.connect(self.updateUi)
        self.boxName.textChanged.connect(self.updateUi)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)


        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Page Designer - {0} Linkline Item".format(
                "Add" if self.item is None else "Line"))
        self.updateUi()


    def updateUi(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
                bool(self.boxName.text()))


    def accept(self):
        if self.item is None:
            self.item = LineItem(self.boxName.text(), None,None, self.position, self.scene, self.parentForm) 
        self.item.fromBox=self.parentForm.dicText[self.FromBox.currentText()]
        self.item.toBox=self.parentForm.dicText[self.ToBox.currentText()]
        self.item.boxName=self.boxName.text()
        self.item.update()
        self.parentForm.dicLine[self.item.boxName]=self.item
        global Dirty
        Dirty = True
        QDialog.accept(self)


class LineItem(QGraphicsLineItem):
    def __init__(self, boxName,   fromBox,toBox,position, scene,parentForm,   style=Qt.SolidLine,
                 rect=None, matrix=QTransform()):
        super(LineItem, self).__init__() 
        
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable|
                      QGraphicsItem.ItemIsFocusable)
        self.style = style
        self.boxName=boxName
        self._fromBox=None
        self._toBox=None
        if fromBox==None:
            x1=10
            y1=10        
        else:
            x1=fromBox.boundingRect().right()
            y1=fromBox.boundingRect().top()+fromBox.boundingRect().height()*0.3
        if toBox==None:
            x2=100
            y2=100        
        else:
            x2=toBox.boundingRect().left()
            y2=toBox.boundingRect().top()+fromBox.boundingRect().height()*0.3
        self.parentForm=parentForm
        self.source = QPointF(x1, y1)
        self.dest = QPointF(x2, y2) 
        self.fromBox=fromBox
        self.toBox=toBox
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
    
    def resetLine(self):
        if self.fromBox==None and  self.toBox==None:
            return 
        if  self.fromBox==None:            
            x2= self.toBox.x()
            y2= self.toBox.y()+self.toBox.boundingRect().height()*0.3
            x1=x2-30
            y1=y2
        elif self.toBox==None:
            x1= self.fromBox.x()+self.fromBox.boundingRect().width()
            y1= self.fromBox.y()+self.fromBox.boundingRect().height()*0.3
            x2=x1+30
            y2=y1 
        else:
            x_diff=self.toBox.x()-self.fromBox.x()
            y_diff=self.toBox.y()-self.fromBox.y()
            x_diff_standand=(self.fromBox.boundingRect().width()+self.toBox.boundingRect().width())/2
            y_diff_standand=(self.fromBox.boundingRect().height()+self.toBox.boundingRect().height())/2
            if ((abs(y_diff)<y_diff_standand)):
                if x_diff>0:         
                 
                    self.direction="x>"   
                    x1= self.fromBox.x()+self.fromBox.boundingRect().width()
                    y1= self.fromBox.y()+self.fromBox.boundingRect().height()*0.3          
                    x2= self.toBox.x()
                    y2= self.toBox.y()+self.toBox.boundingRect().height()*0.3
                else:        
                    self.direction="x<"   
                    x1= self.fromBox.x()
                    y1= self.fromBox.y()+self.fromBox.boundingRect().height()*0.67          
                    x2= self.toBox.x()+self.toBox.boundingRect().width()
                    y2= self.toBox.y()+self.toBox.boundingRect().height()*0.67
            elif ((abs(x_diff)<x_diff_standand)):
                if (y_diff>0):
                    self.direction="y>"   
                    x1= self.fromBox.x()+self.fromBox.boundingRect().width()*0.3          
                    y1= self.fromBox.y()+self.fromBox.boundingRect().height()
                    x2= self.toBox.x()+self.toBox.boundingRect().width()*0.3          
                    y2= self.toBox.y()
                else:
                    self.direction="y<"                   
                    x1= self.fromBox.x()+self.fromBox.boundingRect().width()*0.67
                    y1= self.fromBox.y()
                    x2= self.toBox.x()+self.toBox.boundingRect().width()*0.67         
                    y2= self.toBox.y() +self.toBox.boundingRect().height()
            else:
                if (x_diff>0) and (y_diff>0):
                    self.direction="xy>"                   
                    x1=self.fromBox.x()+self.fromBox.boundingRect().width()
                    y1=self.fromBox.y()+self.fromBox.boundingRect().height()*0.87
                    x2=self.toBox.x()+self.toBox.boundingRect().width()*0.13
                    y2=self.toBox.y()
                elif ((x_diff<0) and (y_diff<0)):                
                    self.direction="xy<"                   
                    x1=self.fromBox.x()
                    y1=self.fromBox.y()+self.fromBox.boundingRect().height()*0.13
                    x2=self.toBox.x()+self.toBox.boundingRect().width()*0.87
                    y2=self.toBox.y()+self.toBox.boundingRect().height() 
                elif (x_diff>0) and (y_diff<0):
                    self.direction="x>y<"                   
                    x1=self.fromBox.x()+self.fromBox.boundingRect().width()*0.87
                    y1=self.fromBox.y()
                    x2=self.toBox.x()
                    y2=self.toBox.y()+self.toBox.boundingRect().height()*0.87
                else:
                    self.direction="x<y>"                   
                    x1=self.fromBox.x() +self.fromBox.boundingRect().width()*0.13
                    y1=self.fromBox.y()+self.fromBox.boundingRect().height()
                    x2=self.toBox.x()+self.toBox.boundingRect().width()
                    y2=self.toBox.y()+self.toBox.boundingRect().height()*0.13                
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
            raise ValueError('boxName must be an string!')        
        self._boxName = value
    
    
    def toSaveJson(self):
        data={"type":"Line", "boxName":self.boxName, "strFromBox":self.fromBox.boxName,
        "strToBox":self.toBox.boxName ,   "style":self.style , "rotation":self.rotation()}
        return data 
     
    @property
    def fromBox(self):
        return self._fromBox 

    @fromBox.setter
    def fromBox(self, value):
        if value!=None:
            if not isinstance(value, QGraphicsTextItem ):
                raise ValueError('boxName must be an string!')        
            self._fromBox = value        
            self.resetLine()
    @property
    def toBox(self):
        return self._toBox 

    @toBox.setter
    def toBox(self, value):
        if value!=None:
            if not isinstance(value, QGraphicsTextItem ):
                raise ValueError('boxName must be an string!')        
            self._toBox = value        
            self.resetLine()
     
        
    def parentWidget(self):
        return self.scene().views()[0]


    def itemChange(self, change, variant):
        if change != QGraphicsItem.ItemSelectedChange:
            global Dirty
            Dirty = True
        return QGraphicsLineItem.itemChange(self, change, variant)


    def mouseDoubleClickEvent(self, event):
        dialog = LineItemDlg(self, self.parentWidget(), self.parentWidget(),self.scene, self.parentForm )
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
        QPainter.drawText(QPointF(ptextx, ptexty),  self.boxName)
        
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
        
        
        QPainter.drawArc(10, 10, 50, 50, 0, 180*16)
        
        v = self.line.unitVector()
        v.setLength(5)
        v.translate(QPointF(10, 60))

        n = v.normalVector()
        n.setLength(n.length() * 0.5)
        n2 = n.normalVector().normalVector()

        p1 = v.p2()
        p2 = n.p2()
        p3 = n2.p2()

        # 方法1
        #QPainter.drawLine(self.line)
        QPainter.drawPolygon(p1, p2, p3)
        self.scene.update()

        # 方法2
        # arrow = QPolygonF([p1, p2, p3, p1])
        # path = QPainterPath()
        # path.moveTo(self.source)
        # path.lineTo(self.dest)
        # path.addPolygon(arrow)
        # QPainter.drawPath(path)
        
