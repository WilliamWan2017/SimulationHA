import json
import functools
import random
import sys 

class CheckPointItem(object): 
    def __init__(self, boxName,variableName, checkValue ): 
        if isinstance(boxName, dict ):            
            variableName=boxName["variableName"] 
            checkValue=boxName["checkValue"]  
            boxName=boxName["boxName"]  
        self.boxName=boxName 
        self.variableName=variableName  
        self.checkValue=checkValue  

  
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
        data={"type":"CheckPointItem", "boxName":self.boxName,   "variableName":self.variableName, "checkValue":self.checkValue }
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
    def variableName(self):
        return self._variableName

    @variableName.setter
    def variableName(self, value):
        if not isinstance(value, str ):
            raise ValueError('variableName must be a string!')        
        self._variableName = value
    
    @property
    def checkValue(self):
        return self._checkValue

    @checkValue.setter
    def isOutput(self, value):
        if not isinstance(value, str ):
            raise ValueError('checkValue must be a string!')        
        self._checkValue= value
     
        


 
        
