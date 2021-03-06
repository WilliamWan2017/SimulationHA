import json
import functools
import random
import sys
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from PyQt5.QtCore import (QByteArray, QDataStream, QFile, QFileInfo,QLineF, QLine, 
                          QIODevice, QPoint, QPointF, QRectF, Qt, QSizeF)
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QTableWidgetItem, QWidget, QHBoxLayout, \
    QApplication

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

class CheckWidget(QWidget):
    def __init__(self, isChecked, parent=None):
        super(CheckWidget, self).__init__(parent)       
        pCheckBox=QCheckBox()
        pCheckBox.setTristate(False)
        pCheckBox.setCheckState(isChecked)
        layout=QHBoxLayout(self)
        layout.addWidget(pCheckBox) 
        self.setLayout(layout) 
class VariableItemDlg(QDialog):

    def __init__(self, item=None,  parent=None):
        super(QDialog, self).__init__(parent)
        self.parentForm=parent;
        self.item = item  
         
        self.txtVariableName = QLineEdit()           
        lblVariableName = QLabel("VariableName:")
        lblVariableName.setBuddy(self.txtVariableName)
        
        self.isOutput=QCheckBox()
        lblIsOutput=QLabel("IsOutput")
        lblIsOutput.setBuddy(self.isOutput)
 
        self.isInput=QCheckBox()
        lblIsInput=QLabel("IsInput")
        lblIsInput.setBuddy(self.isInput)
        
        self.isConstant=QCheckBox()
        lblIsConstant=QLabel("IsConstant")
        lblIsConstant.setBuddy(self.isConstant)
               
        
        self.txtInitialValue = QLineEdit()           
        lblInitialValue = QLabel("Initial Value:")
        lblInitialValue.setBuddy(self.txtInitialValue)
        
        #self.figVariable = Figure(figsize=(5, 0.4))        
        #self.canvVariable  = FigureCanvas(self.figVariable) 
        
        #lblCanvVariable = QLabel("&Format(Variable):")
        #lblCanvVariable.setBuddy(self.canvVariable)
        
        btnDelete=QPushButton("&Delete Variable")
        btnDelete.clicked.connect(self.delete)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                          QDialogButtonBox.Cancel)
        #self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        if self.item is not None: 
            self.txtVariableName.setText(self.item.boxName)
            self.isOutput.setChecked(self.item.isOutput)
            self.isInput.setChecked(self.item.isInput) 
            self.isConstant.setChecked(self.item.isConstant)
            self.txtInitialValue.setText(self.item.initialValue)

        layout = QGridLayout()
        layout.addWidget(lblVariableName, 0, 0)
        layout.addWidget(self.txtVariableName, 0, 1, 1,5) 
        layout.addWidget(lblIsInput, 1, 0)
        layout.addWidget(self.isInput, 1,1)        
        layout.addWidget(lblIsOutput, 1, 2) 
        layout.addWidget(self.isOutput, 1 , 3 ) 
       
        layout.addWidget(lblIsConstant, 2, 0) 
        layout.addWidget(self.isConstant, 2 , 1 ) 
         
        layout.addWidget(lblInitialValue,3, 0)        
        layout.addWidget(self.txtInitialValue, 3,1,1, 6) 
       # layout.addWidget(lblCanvVariable,3, 0)        
        #layout.addWidget(self.canvVariable, 3,1,1, 6) 
        layout.addWidget(self.buttonBox, 4 , 0, 1, 5)    
        layout.addWidget(btnDelete, 4 , 5)
        self.setLayout(layout) 
        self.txtVariableName.textChanged.connect(self.updateUi)
         
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject) 
        #self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.apply)

        self.setWindowTitle("{0}  Variable".format(
                "Add" if self.item is None else "Edit"))
        self.updateUi()

    def delete(self):  
        self.parentForm.deleteVariable(self.item)          
        self.parentForm.setDirty()        
        QDialog.accept(self)
    
    def updateUi(self):
        self.apply()

 
        

    def accept(self):   
        tmpLocationName=self.txtVariableName.text()     
        if (tmpLocationName==""):
            QMessageBox.question(self,
                            "Please Input Variable Name",
                            "Fail to Accept,Please Input a Name for the Edge!",
                            QMessageBox.Ok )  
            return;     
        if self.item is None:
            if (tmpLocationName in self.parentForm.dicVariable.keys()):
                QMessageBox.question(self,
                            "Variable Name Exists",
                            "Fail to Accept,Please Change a Name for this Variable due to there is already a Variable named "+tmpLocationName +"!",
                            QMessageBox.Ok )  
                return
            self.item =VariableItem(  self.txtVariableName.text(),  self.isInput.isChecked(), self.isOutput.isChecked(), self.isConstant.isChecked(), self.txtInitialValue.text(),   self.parentForm)
            self.parentForm.addVariableInTable(self.item)
        else:
            if (self.item.boxName!=tmpLocationName):
                if (tmpLocationName in self.parentForm.dicLine.keys()):
                    QMessageBox.question(self,
                            "Variable Name Exists",
                            "Fail to Accept,Please Change a Name for this Variable due to there is already a Variable named "+tmpLocationName +"!",
                         QMessageBox.Ok )  
                    return
                self.parentForm.dicVariable.pop(self.item.boxName)
                self.parentForm.renameVariable(self.item.boxName, tmpLocationName)
                self.item.boxName=tmpLocationName
                #self.parentForm.addVariableInTable(self.item)
            
        self.parentForm.dicVariable[self.item.boxName]=self.item
        self.item.isInput=self.isInput.isChecked() 
        self.item.isOutput=self.isOutput.isChecked()      
        self.item.isConstant=self.isConstant.isChecked()       
        self.item.initialValue=self.txtInitialValue.text()
        self.parentForm.dicVariable[self.item.boxName]=self.item
        self.parentForm.setVariableInTable(self.item)
        global Dirty
        Dirty = True
        QDialog.accept(self)
    
    def apply(self):        
        #self.figVariable.clf()
        #self.figVariable.text(0.1,0.2, self.txtVariableName.text(), fontsize=16)
        #self.canvVariable.draw()
        pass
 



class VariableItem(object): 
    def __init__(self, boxName,isInput,isOutput, isConstant, initialValue ,parentForm): 
        if isinstance(boxName, dict ):            
            isInput=boxName["isInput"] 
            isOutput=boxName["isOutput"] 
            isConstant=boxName["isConstant"]
            initialValue=boxName["initialValue"]
            boxName=boxName["boxName"] 
        self.parentForm=parentForm
        self.isOutput=isOutput 
        self.boxName=boxName  
        self.isConstant=isConstant
        self.initialValue=initialValue
        self._isInput =False
        self._isOutput=False
        global Dirty
        Dirty = True

 
        
    def getQPixmap4Variable(self):
        guardFig = Figure(figsize=(2.5, 0.4))        
        canvas  = FigureCanvas(guardFig)   
        strData=self.boxName            
        try:
            guardFig.text(0.1,0.3,  strData, fontsize=10)       
        except:
            pass
        canvas.draw()
        size = canvas.size()
        width, height = size.width(), size.height()
        im = QImage(canvas.buffer_rgba(), width, height, QImage.Format_ARGB32)
        return QPixmap(im)
         
    def toSaveJson(self):
        data={"type":"Variable", "boxName":self.boxName,   "isInput":self.isInput, "isOutput":self.isOutput , 
        "isConstant":self.isConstant, "initialValue":self.initialValue}
        return data  
    
    @property
    def boxName(self):
        return self._boxName

    @boxName.setter
    def boxName(self, value):
        if not isinstance(value, str ):
            raise ValueError('boxName must be a string!')        
        self._boxName = value
      
    @property
    def isInput(self):
        return self._isInput

    @isInput.setter
    def isInput(self, value):
        if not isinstance(value, bool ):
            raise ValueError('isInput must be a boolean!')        
        self._isInput = value
    
    @property
    def isOutput(self):
        return self._isOutput

    @isOutput.setter
    def isOutput(self, value):
        if not isinstance(value, bool ):
            raise ValueError('IsInitial must be a boolean!')        
        self._isOutput = value
    
          
     
    @property
    def isConstant(self):
        return self._isConstant

    @isConstant.setter
    def isConstant(self, value):
        if not isinstance(value, bool ):
            raise ValueError('isConstant must be a boolean!')        
        self._isConstant = value
    
    @property
    def initialValue(self):
        return self._initialValue

    @initialValue.setter
    def initialValue(self, value):
        if not isinstance(value, str ):
            raise ValueError('initialValue must be a string!')        
        self._initialValue = value
        


 
        
