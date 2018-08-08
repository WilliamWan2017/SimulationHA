import json
import functools
import random
import sys
from PyQt5.QtCore import (QByteArray, QDataStream, QFile, QFileInfo,QLineF, QLine, 
                          QIODevice, QPoint, QPointF, QRectF, Qt)
from PyQt5.QtWidgets import (QApplication, QDialog, QFrame, 
                             QDialogButtonBox, QFileDialog, QFontComboBox, 
                             QGraphicsItem, QGraphicsPixmapItem,QGraphicsLineItem,    
                             QGraphicsScene, QGraphicsTextItem, QGraphicsView, QGridLayout,
                             QHBoxLayout, QLabel, QMenu, QMessageBox,QPushButton, QSpinBox,
                             QStyle, QTextEdit, QVBoxLayout, QLineEdit, QCheckBox)
from PyQt5.QtGui import QFont,QCursor,QFontMetrics,QTransform,QPainter,QPen,QPixmap,QBrush
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

        self.editor = QTextEdit()         
        self.editor.setAcceptRichText(True)
        self.editor.setTabChangesFocus(True)
        editorLabel = QLabel("&Text:")
        editorLabel.setBuddy(self.editor)
        self.fontComboBox = QFontComboBox()
        self.fontComboBox.setCurrentFont(QFont("Times", PointSize))
        fontLabel = QLabel("&Font:")
        fontLabel.setBuddy(self.fontComboBox)
        self.fontSpinBox = QSpinBox()
        self.fontSpinBox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.fontSpinBox.setRange(6, 280)
        self.fontSpinBox.setValue(PointSize)
        fontSizeLabel = QLabel("&Size:")
        fontSizeLabel.setBuddy(self.fontSpinBox)
        
        
        self.textBoxName = QLineEdit()           
        BoxNameLabel = QLabel("&LocationName:")
        BoxNameLabel.setBuddy(self.textBoxName)
        
        self.isInitial=QCheckBox()
        isInitialLabel=QLabel("&IsInitail")
        isInitialLabel.setBuddy(self.isInitial)
        
        self.guardEditor = QTextEdit()         
        self.guardEditor.setAcceptRichText(True)
        self.guardEditor.setTabChangesFocus(True)
        guardEditorLabel = QLabel("&Text:")
        guardEditorLabel.setBuddy(self.guardEditor)
        
        self.ShowEquationLabel=QLabel("")        
        self.ShowEquationLabel.setTextFormat(Qt.RichText)
        self.ShowEquationLabel.setFrameShape(QFrame.StyledPanel)
        ShowEquationLabelLabel = QLabel("&Format(Text):")
        ShowEquationLabelLabel.setBuddy(self.ShowEquationLabel)
        
        
        
        self.ShowGuardLabel=QLabel("")        
        self.ShowGuardLabel.setTextFormat(Qt.RichText)
        self.ShowGuardLabel.setFrameShape(QFrame.StyledPanel)
        ShowGuardLabelLabel = QLabel("&Format(Guard):")
        ShowGuardLabelLabel.setBuddy(self.ShowGuardLabel)
        
      
        
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Reset|
                                          QDialogButtonBox.Cancel)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        if self.item is not None:
            self.editor.setPlainText(self.item.toPlainText())
            self.fontComboBox.setCurrentFont(self.item.font())
            self.fontSpinBox.setValue(self.item.font().pointSize())
            self.textBoxName.setText(self.item.boxName)

        layout = QGridLayout()
        layout.addWidget(editorLabel, 0, 0)
        layout.addWidget(self.editor, 1, 0, 1, 6)
        layout.addWidget(fontLabel, 2, 0)
        layout.addWidget(self.fontComboBox, 2, 1, 1, 2)
        layout.addWidget(fontSizeLabel, 2, 3)
        layout.addWidget(self.fontSpinBox, 2, 4, 1, 2)
        layout.addWidget(self.textBoxName, 3, 1, )
        layout.addWidget(BoxNameLabel, 3, 0)
        
        layout.addWidget(ShowEquationLabelLabel, 4, 0)
        
        layout.addWidget(self.ShowEquationLabel, 5, 0, 3, 6)
        layout.addWidget(ShowGuardLabelLabel, 10, 0)
        
        layout.addWidget(self.ShowGuardLabel, 10, 1, 1, 2)
        
        layout.addWidget(self.buttonBox, 11, 0  )    
        fontSizeLabel.hide()
        self.fontComboBox.hide()
        fontLabel.hide()
        self.fontSpinBox.hide()
        self.setLayout(layout)


        self.fontComboBox.currentFontChanged.connect(self.updateUi)
        self.fontSpinBox.valueChanged.connect(self.updateUi)
        self.editor.textChanged.connect(self.updateUi)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject) 
        self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.apply)

        self.setWindowTitle("Page Designer - {0} CodeBox Item".format(
                "Add" if self.item is None else "Edit"))
        self.updateUi()


    def updateUi(self):
        font = self.fontComboBox.currentFont()
        font.setPointSize(self.fontSpinBox.value())
        self.editor.document().setDefaultFont(font)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
                bool(self.editor.toPlainText()))

    def apply(self):
        self.ShowGuardLabel.setText( self.guardEditor.toPlainText())
        self.ShowEquationLabel.setText(self.Editor.toPlainText())
        

    def accept(self):
        if self.item is None:
            self.item = LocationItem("","", self.position, self.scene, self.parentForm)
        font = self.fontComboBox.currentFont()
        font.setPointSize(self.fontSpinBox.value())
        self.item.setFont(font)
        self.item.setPlainText(self.editor.toPlainText())   
        self.item.boxName=self.textBoxName.text()
        self.item.update()
        self.parentForm.dicText[self.item.boxName]=self.item
        global Dirty
        Dirty = True
        QDialog.accept(self)


class LocationItem(QGraphicsTextItem):    
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
        
