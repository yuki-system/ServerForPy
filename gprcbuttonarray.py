import json
from enum import Enum, auto
import sys

class GprcButtonArray:
    """UIのボタン表記を管理するクラス
    """
    def __init__(self):
        self.bArray = {}
        self.funcArray = {}
        self.strText = ""
        self.initArray()
    
    def initArray(self):
        self.bArray.clear()
        self.bArray["R"] = ["", "red", "red"]
        self.bArray["G"] = ["", "green", "green"]
        self.bArray["B"] = ["", "blue", "blue"]
        self.bArray["Y"] = ["", "yellow", "yellow"]
        self.bArray["bs"] = ["BS", "backspace", ""]
        self.bArray["divide"] = ["/", "divide", ""]
        self.bArray["multi"] = ["*", "multiply", ""]
        self.bArray["minus"] = ["-", "minus", ""]
        self.bArray["plus"] = ["+", "plus", ""]
        self.bArray["equal"] = ["=", "equal", ""]
        self.bArray["point"] = [".", "point", ""]
        for i in range(0, 10):
            self.bArray[str(i)] = [str(i), str(i), ""]
        
        self.funcArray.clear()
        self.funcArray["R"] = None
        self.funcArray["G"] = None
        self.funcArray["B"] = None
        self.funcArray["Y"] = None
        self.funcArray["bs"] = None
        self.funcArray["divide"] = None
        self.funcArray["multi"] = None
        self.funcArray["minus"] = None
        self.funcArray["plus"] = None
        self.funcArray["equal"] = None
        self.funcArray["point"] = None
        for i in range(0, 10):
            self.funcArray[str(i)] = None
    
    def getJson(self):
        jdict = {}
        jdict["Gprc"] = "s2c"
        jdict["Type"] = "set"
        jdict["Set"] = self.bArray
        jdict["Text"] = self.strText
        return json.dumps(jdict)
    
    def callFunc(self, title):
        """ボタンtitleが押されたときの関数を実行する
        """
        try:
            if self.funcArray[title] == None:
                return
            func = self.funcArray[title]
            func()
        except Exception as e:
            print("{0}:{1}".format(__class__.__name__ +"."+ sys._getframe().f_code.co_name, e))
    
    def setFunc(self, title, argFunc = None):
        """ボタンtitleが押されたときの関数を設定する
        """
        try:
            self.funcArray[title] = argFunc
            return
        except Exception as e:
            print("{0}:{1}".format(__class__.__name__ +"."+ sys._getframe().f_code.co_name, e))
        

class ButtonRole:
    title = ""
    label = ""
    tooltip = ""
    color = ""
    func = None
    
    def __init__(self, argTitle = "", argLabel = "", argToooltip = "", argColor = "", argFunc = None):
        self.title = argTitle
        self.label = argLabel
        self.tooltip = argToooltip
        self.color = argColor
        self.func = argFunc
    
