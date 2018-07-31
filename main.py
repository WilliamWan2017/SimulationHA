import sys
import imp
import qtutils
import _pickle
import customfunction
from TableWidgetDragRows   import TableWidgetDragRows
from DestTableWidgetDragCells import  DestTableWidgetDragCells
from PyQt5.QtCore import *
from PyQt5.QtGui import QDropEvent
from PyQt5.QtWidgets import QMessageBox, QGridLayout , QPushButton,  QTableWidget, QAbstractItemView, QTableWidgetItem, QWidget, QHBoxLayout, \
    QApplication

from pathlib import Path
  

class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        layout = QGridLayout()
        self.setLayout(layout)
        layout=
        self.btnGenerate=QPushButton()
        self.btnGenerate.setText('Generate code')
        self.btnGenerate.clicked.connect(self.On_btnGenerate_clicked)
        
        
        self.btnRunCode=QPushButton()
        self.btnRunCode.setText('Run code by exec')
        self.btnRunCode.clicked.connect(self.On_btnRunCode_clicked)        
        
        
        self.btnRunCodeReload=QPushButton()
        self.btnRunCodeReload.setText('Run code by reload')
        self.btnRunCodeReload.clicked.connect(self.On_btnRunCodeReload_clicked)        
        
        self.btnSave=QPushButton()
        self.btnSave.setText('Save Designed')
        self.btnSave.clicked.connect(self.On_btnSave_clicked)        
        
        layout.addWidget(self.btnGenerate, 0, 0 )         
        layout.addWidget(self.btnRunCode, 0, 1 ) 
        
        layout.addWidget(self.btnRunCodeReload, 1, 0 ) 
        layout.addWidget(self.btnSave, 1, 1 ) 
        self.table_widget = TableWidgetDragRows()
        layout.addWidget(self.table_widget, 2, 0) 

        # setup table widget
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(['variable', 'operation', 'digit'])
        
        
        self.DestTableWidgetDragCell = DestTableWidgetDragCells()
        layout.addWidget(self.DestTableWidgetDragCell, 2, 1) 

        # setup table widget
        self.DestTableWidgetDragCell.setColumnCount(2)
        self.DestTableWidgetDragCell.setHorizontalHeaderLabels(['seq', 'equation'])

        items = [('x', '=', '0'), ('y', '+', '1'), ('z', '-', '2'),  ('a', '*', '3'), ('b', '/', '4'), ('c', '>', '5'),  ('d', '<', '6'), ('e', 'remove', '7'), ('f', 'insert', '8'),  ('g', 'blank_lines', '9') , ('', 'return ', '10')]
        self.table_widget.setRowCount(len(items))
        for i, (virables, operation, digits) in enumerate(items):
            self.table_widget.setItem(i, 0, QTableWidgetItem(virables))
            self.table_widget.setItem(i, 1, QTableWidgetItem(operation))
            self.table_widget.setItem(i, 2, QTableWidgetItem(digits))

        self.resize(800, 800)

        my_file = Path("save.p")
        if my_file.is_file():
            item_xml = _pickle.load( open( "save.p", "rb" ) )
            print ("init")
            print (item_xml)
            iRow=0
            for data in enumerate(item_xml):
                self.DestTableWidgetDragCell.insertRow(iRow)                 
                for item in data[1]:
                    self.DestTableWidgetDragCell.setItem(iRow, item[1], QTableWidgetItem(item[2]))
                iRow=iRow+1
                    
                
           
        self.show()
    def showmessage(selfs):
        
        buttonReply = QMessageBox.question(self, 'PyQt5 message', "Do you like PyQt5?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            print('Yes clicked.')
        else:
            print('No clicked.')

    def On_btnGenerate_clicked(self):
        with open('customfunction.py', 'w') as f:
            f.write("import sys\n")
            f.write("def customfunction():\n")
            for iRow in range(self.DestTableWidgetDragCell.rowCount()):
                f.write("    "+self.DestTableWidgetDragCell.item(iRow, 1).text()+"\n")
   
       

    def On_btnRunCodeReload_clicked(self):
        imp.reload(customfunction)
        QMessageBox.question(self, 'PyQt5 message', "result="+str(customfunction.customfunction()), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
     
    def On_btnRunCode_clicked(self):
        with open("customfunction3.py") as f:
            execcode = compile(f.read(), "customfunction3.py", 'exec')
        exec(execcode)
        
    def On_btnSave_clicked(self):
        self.DestTableWidgetDragCell.selectAll()
        item_xml=[[(row, col, self.DestTableWidgetDragCell.item(row, col).text())for col in range(self.DestTableWidgetDragCell.columnCount())]
        for row in range(self.DestTableWidgetDragCell.rowCount())]
        _pickle.dump( item_xml, open( "save.p", "wb" ) )
        print (item_xml)
#      QMessageBox.question(self, 'result', 'result='+str(globals['x']), QMessageBox.Ok)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
