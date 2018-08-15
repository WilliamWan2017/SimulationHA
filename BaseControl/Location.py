import json
import functools
import random
import sys
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
                             QStyle, QTextEdit, QVBoxLayout, QLineEdit, QCheckBox)
from PyQt5.QtGui import QFont,QCursor,QFontMetrics,QTransform,QPainter,QPen,QPixmap,QBrush, QImage
from PyQt5.QtPrintSupport import QPrinter,QPrintDialog

MAC = True
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
        lblEquation= QLabel("&Equations:")
        lblEquation.setBuddy(self.ediEquation)
         
        self.txtLocationName = QLineEdit()           
        lblLocationName = QLabel("&LocationName:")
        lblLocationName.setBuddy(self.txtLocationName)
        
        self.isNameAbove=QCheckBox()
        lblIsNameAbove=QLabel("&IsNameAbove")
        lblIsNameAbove.setBuddy(self.isNameAbove)
        
        self.isInitial=QCheckBox()
        lblIsInitial=QLabel("&IsInitail")
        lblIsInitial.setBuddy(self.isInitial)
        
        self.txtGuard = QLineEdit()           
        lblGuard = QLabel("&Guard:")
        lblGuard.setBuddy(self.txtGuard)
        
        self.figEquation = Figure(figsize=(3, 1))        
        self.canvEquation  = FigureCanvas(self.figEquation) 
        
        lblCanvEquation = QLabel("&Format(Equations):")
        lblCanvEquation.setBuddy(self.canvEquation)
        
        self.figGuard = Figure(figsize=(5, 0.4))
        
        self.canvGuard  = FigureCanvas(self.figGuard)
    
        lblCanvGuard = QLabel("&Format(Guard):")
        lblCanvGuard.setBuddy(self.canvGuard)
        btnDelete=QPushButton("Delete Location")
        btnDelete.clicked.connect(self.delete)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                          QDialogButtonBox.Cancel)
        #self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        if self.item is not None:
            self.ediEquation.setPlainText("\n".join(self.item.equation))
            self.txtLocationName.setText(self.item.boxName)
            self.isInitial.setChecked(self.item.isInitial)
            self.isNameAbove.setChecked(self.item.isNameAbove)
            self.txtGuard.setText(self.item.guard)

        layout = QGridLayout()
        layout.addWidget(lblEquation, 0, 0)
        layout.addWidget(self.ediEquation, 1, 0, 1, 6)
        layout.addWidget(lblLocationName, 2, 0)
        layout.addWidget(self.txtLocationName, 2, 1, 1, 2)
        layout.addWidget(lblIsNameAbove, 2, 3)
        layout.addWidget(self.isNameAbove, 2, 4, 1, 2)        
        layout.addWidget(lblIsInitial, 3, 0) 
        layout.addWidget(self.isInitial, 3, 1 )
        layout.addWidget(lblGuard, 4, 0)
        layout.addWidget(self.txtGuard,  4, 1, 1, 5)
        
        layout.addWidget(lblCanvEquation, 5, 0)        
        layout.addWidget(self.canvEquation, 6, 0, 3, 6)
        layout.addWidget(lblCanvGuard, 10, 0)        
        layout.addWidget(self.canvGuard, 10,1, 1, 5)  
        layout.addWidget(self.buttonBox, 11, 0, 1, 5)    
        layout.addWidget(btnDelete, 11, 5)
        self.setLayout(layout)

 
        self.ediEquation.textChanged.connect(self.updateUi)
        self.txtGuard.textChanged.connect(self.updateUi)
         
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject) 
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

 
        

    def accept(self):
        iEditLine=self.ediEquation.document().lineCount(); 
        equation=[self.ediEquation.document().findBlockByLineNumber(i).text() for i in range(iEditLine)]          
        if self.item is None:
             self.item = LocationItem("",equation,self.txtGuard.text(), self.position, self.isInitial.isChecked(), self.isNameAbove.isChecked(), self.scene, self.parentForm)
        if (self.item.boxName==""):
            self.item.boxName=self.txtLocationName.text()
        else:
            if (self.item.boxName!=self.txtLocationName.text()):
                self.parentForm.dicText.pop(self.item.boxName)
        self.parentForm.dicText[self.item.boxName]=self.item
        self.item.equation=equation
        self.item.guard=self.txtGuard.text()
        self.item.isInitial=self.isInitial.isChecked()
        self.item.isNameAbove=self.isNameAbove.isChecked()
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
        for i in range(iEditLine):
            strData=self.ediEquation.document().findBlockByLineNumber(i).text();            
            self.figEquation.text(0.1,iHeight-0.2*(i+1), strData, fontsize=10)
        self.canvEquation.draw()
        self.figGuard.clf()
        self.figGuard.text(0.1,0.2, self.txtGuard.text(), fontsize=16)
        self.canvGuard.draw()
        
 



class LocationItem(QGraphicsItem): 
    def __init__(self, boxName, equation, guard, position, isInitial, isNameAbove, scene,parentForm,size=None, style=Qt.SolidLine,
                  matrix=QTransform()):
        super(LocationItem, self).__init__()
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable|
                      QGraphicsItem.ItemIsFocusable)

        if isinstance(boxName, dict ):            
            equation=boxName["equation"]
            position= QPointF(boxName["position"][0], boxName["position"][1])
            guard=boxName["guard"]
            isInitial=boxName["isInitial"]
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
        self.guard=guard
        self.isInitial=isInitial
        self.isNameAbove=isNameAbove
        self.boxName=boxName
        self.imageEquation=self.getQImage4Equation()
        self.imageGuard=self.getQImage4Guard()   
        self.rect = rect
        self.style = style
        self.setPos(position)
        self.setTransform(matrix)
        scene.clearSelection()
        scene.addItem(self)
        self.setSelected(True)
        self.setFocus()
        self._edges={}
        global Dirty
        Dirty = True


    def getQImage4Equation(self ):
        iEditLine=len(self.equation);
        iHeight=1;
        if (iEditLine>4):
            iHeight=0.2*(iEditLine-4)+1;
        
        guardFig = Figure(figsize=(2.5, iHeight))        
        canvas  = FigureCanvas(guardFig)  
        
        for i in range(iEditLine):
            strData=self.equation[i]         
            try:  
                guardFig.text(0.1,iHeight-0.2*(i+1), strData, fontsize=10)       
            except:
                pass
        canvas.draw()
        size = canvas.size()
        width, height = size.width(), size.height()
        im = QImage(canvas.buffer_rgba(), width, height, QImage.Format_ARGB32)
        return im
        
    def getQImage4Guard(self):
        guardFig = Figure(figsize=(2.5, 0.4))        
        canvas  = FigureCanvas(guardFig)   
        strData=self.guard      
        try:
            guardFig.text(0.1,0.3,  strData, fontsize=10)       
        except:
            pass
        canvas.draw()
        size = canvas.size()
        width, height = size.width(), size.height()
        im = QImage(canvas.buffer_rgba(), width, height, QImage.Format_ARGB32)
        return im
         
    def toSaveJson(self):
        data={"type":"Location", "boxName":self.boxName, "equation":self.equation,"guard":self.guard, 
        "position":(self.x(), self.y()) ,   "isInitial":self.isInitial, "isNameAbove":self.isNameAbove, 
        "size":(self.rect.width(), self.rect.height()) ,  "rotation":self.rotation()}
        return data
        #Json.dumps(data)
    def mouseDoubleClickEvent(self, event):
        dialog = LocationItemDlg(self, self.parentWidget(),self.scene, self.parentForm )
        dialog.exec_()
    
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
    def isNameAbove(self):
        return self._isNameAbove

    @isNameAbove.setter
    def isNameAbove(self, value):
        if not isinstance(value, bool ):
            raise ValueError('IsInitial must be a boolean!')        
        self._isNameAbove = value
    
    
    @property
    def equation(self):
        return self._equation

    @equation.setter
    def equation(self, value):
        if not isinstance(value, list ):
            raise ValueError('Guard must be a list!')        
        self._equation = value        
        self.imageEquation=self.getQImage4Equation()
        
    @property
    def guard(self):
        return self._guard

    @guard.setter
    def guard(self, value):
        if not isinstance(value, str ):
            raise ValueError('Guard must be an string!')        
        self._guard = value        
        self.imageGuard=self.getQImage4Guard()
    def parentWidget(self):
        return self.scene().views()[0]


    def boundingRect(self):
        return self.rect.adjusted(-1, -1,  1, 1)


    def paint(self, painter, option, widget): 
        pen = QPen(self.style)
        pen.setColor(Qt.black)
        pen.setWidth(1)
        if option.state & QStyle.State_Selected:
            pen.setColor(Qt.blue)
        painter.setPen(pen)
        painter.drawRect(self.boundingRect())
        painter.drawImage(self.rect, self.imageEquation)
        pointText=QPointF(self.rect.x(), self.rect.y()-40)
        rectGuard=QRectF(self.rect.x(), self.rect.y()-35, self.rect.width(), 30)
        if self.isNameAbove:            
            pointText=QPointF(self.rect.x(), self.rect.y()+self.rect.height()+50)
            rectGuard=QRectF(self.rect.x(), self.rect.y() +self.rect.height()+5, self.rect.width(), 30)
        painter.drawText(pointText,  self.boxName)
        #painter.drawText(self.rect.x(), self.rect.y()-30, "1-" +self.boxName)
        #painter.drawText(self.rect.x(), self.rect.y()-10, "2-" + self.boxName)
        #painter.drawText(self.rect.x(), self.rect.y()+10, "3-" + self.boxName)
        #painter.drawText(self.rect.x(), self.rect.y()+self.rect.height()+30, "4-" +  self.boxName)
        painter.drawImage(rectGuard, self.imageGuard)
        

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
        
        guardFig = Figure(figsize=(5, iHeight))        
        canvas  = FigureCanvas(guardFig)  
        
        for i in range(iEditLine):
            strData=text[i]            
            guardFig.text(0.1,iHeight-0.2*(i+1), strData, fontsize=10)       
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
    def guard(self):
        return self._guard

    @guard.setter
    def guard(self, value):
        if not isinstance(value, str ):
            raise ValueError('Guard must be an string!')        
        self._guard = value
        
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
    def guard(self):
        return self._guard

    @guard.setter
    def guard(self, value):
        if not isinstance(value, str ):
            raise ValueError('Guard must be an string!')        
        self._guard = value
        
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
        
