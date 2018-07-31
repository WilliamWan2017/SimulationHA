# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\0.3deeplearning\eric_wk\HA2\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.widget = QtWidgets.QWidget(self.centralWidget)
        self.widget.setGeometry(QtCore.QRect(50, 20, 471, 81))
        self.widget.setObjectName("widget")
        self.btnAddnewEdit = QtWidgets.QPushButton(self.widget)
        self.btnAddnewEdit.setGeometry(QtCore.QRect(10, 10, 111, 23))
        self.btnAddnewEdit.setObjectName("btnAddnewEdit")
        self.btnAddnewEdit.clicked.connect(self.on_btnAddnewEdit_click)
        self.btnAddnewLabel = QtWidgets.QPushButton(self.widget)
        self.btnAddnewLabel.setGeometry(QtCore.QRect(160, 10, 75, 23))
        self.btnAddnewLabel.setObjectName("btnAddnewLabel")
        
        self.btnAddnewLabel.clicked.connect(self.on_btnAddnewLabel_click)
        self.widget_2 = QtWidgets.QWidget(self.centralWidget)
        self.widget_2.setGeometry(QtCore.QRect(50, 130, 471, 281))
        self.widget_2.setObjectName("widget_2")
        self.textEdit = QtWidgets.QTextEdit(self.widget_2)
        self.textEdit.setGeometry(QtCore.QRect(20, 20, 104, 71))
        self.textEdit.setObjectName("textEdit")
        self.label = QtWidgets.QLabel(self.widget_2)
        self.label.setGeometry(QtCore.QRect(130, 40, 171, 16))
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralWidget)
        self.EditList=[]
        self.LableList=[]
        self.EditCount=0
        self.LableCount=0
        self.dicEdit={}
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    def on_btnAddnewEdit_click(self):
        self.dicEdit[self.EditCount] = QtWidgets.QTextEdit(self.widget_2)
        self.dicEdit[self.EditCount].setGeometry(QtCore.QRect(50, 50 , 104, 71))
        self.dicEdit[self.EditCount].setObjectName("textEdit"+str(self.EditCount))
        self.dicEdit[self.EditCount].move(60, 60)
        self.widget_2.repaint()
        self.EditCount+=1     
    def on_btnAddnewLabel_click(self):
        self.textEdit.move(60, 60)
       
       

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btnAddnewEdit.setText(_translate("MainWindow", "AddnewEdit"))
        self.btnAddnewLabel.setText(_translate("MainWindow", "AddnewLabel"))
        self.label.setText(_translate("MainWindow", "--------------------------->"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

