import xlrd

class Crossbar(object):

    def __init__(self, excelFileName, sheetName):
        self.portDictByIndex = {}
        self.funcDictByRow = {}
        self.crossCoList = []
        self._processExcelFile(excelFileName, sheetName)


    def _processExcelFile(self, excelFileName, sheetName):
        self.book = xlrd.open_workbook(excelFileName)
        self.sheet = self.book.sheet_by_name(sheetName)

        if self.sheet.row_values(0)[0] == "Port":
            port_num = len(self.sheet.row_values(0)) - 1
            i = 1
            for portName in self.sheet.row_values(0)[1:]:
                if portName:
                    self.portDictByIndex[i] = Port(portName, i)
                i = i + 1
        if self.sheet.row_values(1)[0] == "Function" and self.sheet.row_values(1)[1] == "Type":
            for i in range(2, self.sheet.nrows):
                if self.sheet.row_values(i)[0]:
                    self.funcDictByRow[i] = Func(self.sheet.row_values(i)[0], self.sheet.row_values(i)[1], i)

        for i in range(2, self.sheet.nrows):
            for j in range(2, self.sheet.ncols):
                if self.sheet.row_values(i)[j]:
                    self.crossCoList.append((i,j))

    def _writePortLine(self, f, portName, inOut, width=1, isReg=False, withComma=True, typeStartCol=10, widthStartCol=18, nameStartCol=28, cmtStartCol=48, cmt="", indentation=0):
        l = ""
        if portName:
            if inOut.lower() in ["i", "in", "input"]:
                l = l + "input "
                isReg = False
            else:
                l = l + "output "
        l = l + ' ' * (typeStartCol-len(l))
        if isReg:
            l = l + "reg "
        else:
            l = l + "wire "
        if width>1:
            l = l + ' ' * (widthStartCol-len(l)) + '[' + str(width-1) + ":0] "
        l = l + ' ' * (nameStartCol-len(l)) + portName
        if withComma:
            l = l + ','
        if cmt:
            l = l + ' ' * (cmtStartCol-len(l)) + "//" + cmt
        l = l + '\n'
        if indentation>0:
            l = ' '*indentation + l
        if width>0:
            f.write(l)

    def _writeRegWireLine(self, f, name, regWire, width=1, withSemiComma=True, widthStartCol=10, nameStartCol=20, cmtStartCol=48, cmt="", indentation=0):
        l = ""
        if regWire.lower() in ['r', 'reg']:
            l = l + "reg"
        elif regWire.lower() in ['w', 'wire']:
            l = l + "wire"
        l = l + ' '*(widthStartCol-len(l))
        if width>1:
            l = l + '[' + str(width-1) + ":0]"
        l = l + ' '*(nameStartCol-len(l))
        l = l + name
        if withSemiComma:
            l = l + ";"
        if cmt:
            l = l + ' '*(cmtStartCol-len(l)) + "//" + cmt
        if indentation>0:
            l = ' '*indentation + l
        l = l + '\n'
        if width>0:
            f.write(l)

    def _writeFuncOnPinAssignment(self, f, co, orLogicList):
        f.write(("assign " + self.funcDictByRow[co[0]].funcName + "_on_" + self.portDictByIndex[co[1]].portName).ljust(25))
        f.write("=".ljust(8))
        if len(orLogicList) > 0:
            f.write("~(")
            l = len(orLogicList)
            upTo = 4
            while upTo<l:
                if upTo>4:
                    f.write(' '*33)
                for i in range(upTo-4, upTo):
                    f.write(orLogicList[i] + " | ")
                f.write('\n')
                upTo = upTo + 4
            if upTo>4:
                f.write(' '*33)
            for i in range(upTo-4, l-1):
                f.write(orLogicList[i] + " | ")
            f.write(orLogicList[l-1] + ") &\n")
            f.write(' '*33)
        f.write(self.funcDictByRow[co[0]].funcName + "_ON & " + self.portDictByIndex[co[1]].portName + "_not_SKIP;\n\n")

    def _writePinHasFunc(self, f, pinName, funcList):
        f.write(("assign " + pinName + "_has_func").ljust(25))
        f.write("=".ljust(8))
        if len(funcList) == 0:
            f.write("1'b0;\n")
        else:
            l = len(funcList)
            upTo = 4
            while upTo<l:
                if upTo>4:
                    f.write(' '*33)
                for i in range(upTo-4, upTo):
                    f.write(funcList[i] + " | ")
                f.write('\n')
                upTo = upTo + 4
            if upTo>4:
                f.write(' '*33)
            for i in range(upTo-4, l-1):
                f.write(funcList[i] + " | ")
            f.write(funcList[l-1] + ";\n\n")

    def _writePinDout(self, f, pinName, funcList):
        f.write(("assign " + pinName + "_out").ljust(25))
        f.write("=".ljust(8))
        l = len(funcList)
        upTo = 2
        while upTo<l:
            if upTo>2:
                f.write(' '*33)
            for i in range(upTo-2, upTo):
                f.write(funcList[i] + " | ")
            f.write('\n')
            upTo = upTo + 2
        if upTo>2:
            f.write(' '*33)
        for i in range(upTo-2, l-1):
            f.write(funcList[i] + " | ")
        f.write(funcList[l-1] + ";\n\n")

    def _writeFuncIn(self, f, funcIn, pinList):
        f.write(("assign " + funcIn).ljust(25))
        f.write("=".ljust(8))
        l = len(pinList)
        upTo = 2
        while upTo<1:
            if upTo>2:
                f.write(' '*33)
            for i in range(upTo-2, upTo):
                f.write(pinList[i] + " | ")
            f.write('\n')
            upTo = upTo + 2
        if upTo>2:
            f.write(' '*33)
        for i in range(upTo-2, l-1):
            f.write(pinList[i] + " | ")
        f.write(pinList[l-1] + ";\n\n")
        
                    

    def writeVerilog(self, fileName, headCommentLength=66):
        f = open(fileName + ".v", 'w+')
        from datetime import datetime
        now = datetime.now()
        f.write("// " + '='*headCommentLength + '\n')
        f.write("// " + "This file is automatically generated.".center(headCommentLength) + "\n")
        f.write("// " + "Scripts by Cheng Cai".center(headCommentLength) + "\n")
        f.write("// " + "File name".ljust(int(headCommentLength/2)) + ":  " + fileName + "\n")
        f.write("// " + "Generation time".ljust(int(headCommentLength/2))  + ":  " + str(now.year) + '-' + str(now.month) + '-' + str(now.day) + " "
                + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second) + "\n")
        f.write("// " + '='*headCommentLength + '\n')
        f.write("// Number of ports (with digital functions): " + str(len(self.portDictByIndex)) + "\n")
        f.write("// Number of digital functions: " + str(len(self.funcDictByRow)) + "\n"*2)

        f.write("module " + fileName + "(\n")
        #port list
        f.write("// Ports' data input and output\n")
        for p in self.portDictByIndex.values():
            portName = p.portName
            self._writePortLine(f=f, portName=portName+"_out", inOut="out", isReg=False)
            self._writePortLine(f=f, portName=portName+"_in", inOut="in", isReg=False)
        f.write("// GPIO input and output\n")
        for p in self.portDictByIndex.values():
            portName = p.portName
            self._writePortLine(f=f, portName=portName+"_gpio_din", inOut="out", isReg=False)
            self._writePortLine(f=f, portName=portName+"_gpio_dout", inOut="in", isReg=False)
        f.write("// Functions' input and/or output\n")
        for func in self.funcDictByRow.values():
            funcName = func.funcName
            if func.funcDir.lower() == "di":
                self._writePortLine(f=f, portName=funcName, inOut="out", isReg=False, cmt=funcName + " DI")
            elif func.funcDir.lower() == "do":
                self._writePortLine(f=f, portName=funcName, inOut="in", isReg=False, cmt=funcName + " DO")
            elif func.funcDir.lower() == "dio":
                self._writePortLine(f=f, portName=funcName + "_in", inOut="out", isReg=False, cmt=funcName+ " DIO")
                self._writePortLine(f=f, portName=funcName + "_out", inOut="in", isReg=False)
                self._writePortLine(f=f, portName=funcName + "_oe", inOut="in", isReg=False)
        f.write("// Ports' SKIP\n")
        for p in self.portDictByIndex.values():
            portSkip = p.portName + "_SKIP"
            self._writePortLine(f=f, portName=portSkip, inOut="in", isReg=False)
        f.write("// Functions' ON\n")
        funcOnList = []
        for func in self.funcDictByRow.values():
            funcOnList.append(func.funcName + "_ON")
        for funcOn in funcOnList[:-1]:
            self._writePortLine(f=f, portName=funcOn, inOut="in", isReg=False)
        self._writePortLine(f=f, portName=funcOnList[-1], inOut="in", isReg=False, withComma=False)
        f.write(");\n\n")

        #reg/wire var
        f.write("// func on pin\n")
        for co in self.crossCoList:
            row = co[0]
            col = co[1]
            funcOnPinName = self.funcDictByRow[row].funcName + "_on_" + self.portDictByIndex[col].portName
            self._writeRegWireLine(f=f, name=funcOnPinName, regWire="wire")
        f.write("// not skip\n")
        for p in self.portDictByIndex.values():
            portNotSkip = p.portName + "_not_SKIP"
            self._writeRegWireLine(f=f, name=portNotSkip, regWire="wire")
        for p in self.portDictByIndex.values():
            portHasFunc = p.portName + "_has_func"
            self._writeRegWireLine(f=f, name=portHasFunc, regWire="wire")

        f.write("\n"*2)
        #logic assignment
        f.write("// not skip logic\n")
        for p in self.portDictByIndex.values(): 
            f.write("assign " + p.portName + "_not_SKIP = ~" + p.portName + "_SKIP;\n")

        f.write('\n'*2)
        f.write("// pin has func logic\n")
        for p in self.portDictByIndex.values():
            funcOnPinList = []
            for co in self.crossCoList:
                if co[1] == p.index:
                    funcOnPinList.append(self.funcDictByRow[co[0]].funcName + "_on_" + self.portDictByIndex[co[1]].portName)
            self._writePinHasFunc(f=f, pinName=p.portName, funcList=funcOnPinList)

        f.write("\n"*2)
        f.write("// func on pin logic\n")
        for co in self.crossCoList:
            upLeft = []
            for i in range(2,co[0]+1):
                for j in range(2,co[1]+1):
                    if (i,j) in self.crossCoList:
                        if (i,j) != co:
                            upLeft.append(self.funcDictByRow[i].funcName + "_on_" + self.portDictByIndex[j].portName)
            self._writeFuncOnPinAssignment(f=f, co=co, orLogicList=upLeft)

        f.write('\n'*2)
        f.write("// dout logic\n")
        for p in self.portDictByIndex.values():
            funcDoutList = []
            for co in self.crossCoList:
                if co[1] == p.index:
                    if self.funcDictByRow[co[0]].funcDir.lower() == "dio":
                        funcDoutList.append("(" + self.funcDictByRow[co[0]].funcName + "_out & " + self.funcDictByRow[co[0]].funcName + "_on_" + self.portDictByIndex[co[1]].portName + ")")
                    elif self.funcDictByRow[co[0]].funcDir.lower() == "do":
                        funcDoutList.append("(" + self.funcDictByRow[co[0]].funcName + " & " + self.funcDictByRow[co[0]].funcName + "_on_" + self.portDictByIndex[co[1]].portName + ")")
            funcDoutList.append("(" + p.portName + "_gpio_dout & ~" + p.portName + "_has_func)")
            self._writePinDout(f=f, pinName=p.portName, funcList=funcDoutList)

        f.write('\n'*2)
        f.write("// func in logic\n")
        for func in self.funcDictByRow.values():
            if func.funcDir.lower() == "di" or func.funcDir.lower() == "dio":
                pinList = []
                for co in self.crossCoList:
                    if co[0] == func.row:
                        pinList.append("(" + self.portDictByIndex[co[1]].portName + "_in & " + self.funcDictByRow[co[0]].funcName + "_on_" + self.portDictByIndex[co[1]].portName + ")")
                if func.funcDir.lower() == "di":
                    funcIn = func.funcName
                else:
                    funcIn = func.funcName + "_in"
                self._writeFuncIn(f=f, funcIn=funcIn, pinList=pinList)

        f.write('\n'*2)
        f.write("// gpio in\n")
        for p in self.portDictByIndex.values():
            f.write(("assign " + p.portName + "_gpio_din").ljust(25) + "=".ljust(8) + p.portName + "_in;\n\n")

        f.write("endmodule")
            
                    
                    
        

        f.write('\n'*3)
            
                        
        
        f.close()
            




class Port(object):
    def __init__(self, portName, index):
        self.portName = portName
        self.index = index

class Func(object):
    def __init__(self, funcName, funcDir,row):
        self.funcName = funcName
        self.funcDir = funcDir
        self.row = row

if __name__ == "__main__":
    c = Crossbar("crossbar.xlsx", "crossbar")
    c.writeVerilog("crossbar")
