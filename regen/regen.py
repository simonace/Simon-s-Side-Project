import xlrd

class Module(object):
    def __init__(self, moduleName, baseAddressInt, sheet):
        self.usedOffsetAddrList = []
        self.regNameDict = {}
        self.regDict = {}
        self.regStartRowList = []
        self.moduleName=moduleName
        self.baseAddressInt = baseAddressInt
        self.sheet = sheet
        self._sheetProcess()

    def _sheetProcess(self):
        if self.sheet.nrows < 5:
            raise Exception("Module " + self.moduleName + " has no register information or wrong format")
        else:
            for i in range(4, self.sheet.nrows):
                if self.sheet.row_values(i)[0].replace(' ',''):
                    self.regStartRowList.append(i)
            self.regStartRowList.append(self.sheet.nrows)
        for j in range(len(self.regStartRowList)-1):
            regName = self.sheet.row_values(self.regStartRowList[j])[0]
            offsetInt = ProcessTools.offsetAddressProcess(self.sheet.row_values(self.regStartRowList[j])[1])
            if offsetInt in self.usedOffsetAddrList:
                raise Exception("Same offset address happens in two regs in module " + self.moduleName)
            else:
                self.usedOffsetAddrList.append(offsetInt)
            self.regNameDict[offsetInt] = regName
            if regName in self.regDict:
                raise Exception("Register with same module name exist in module " + self.moduleName)
            self.regDict[regName] = Register(regName, offsetInt)
            for k in range(self.regStartRowList[j], self.regStartRowList[j+1]):
                if self.sheet.row_values(k)[2].replace(' ', ''):
                    segName = self.sheet.row_values(k)[2].replace(' ', '')
                    segStart, segEnd = ProcessTools.indexProcess(self.sheet.row_values(k)[3])
                    segType = self.sheet.row_values(k)[4]
                    self.regDict[regName].addSegment(Segment(segName, segStart, segEnd, segType))

    def buildModuleRegVerilog(self, projectName, toLowerCase=False, acknowledge=False):
        if toLowerCase:
            fileName = self.moduleName.lower() + "_regfile"
        else:
            fileName = self.moduleName + "_regfile"
        f = open(fileName + ".v", 'w+')
        ProcessTools.writeHeadComments(f, fileName + ".v")

        if acknowledge:
            import random
            acknowledgeList = [ "// This project is solely and wholely for you, Wanying.\n\n",
                                "// I always imagine, Wanying, I could take your hand and see the world together with you.\n\n",
                                "// I am so enchanted by your beautiful innocent eyes, and your lovely wink, Wanying.\n\n",
                                "// I cherish you, Wanying, forever and always.\n\n"
                              ]
            rndAck = random.randint(0,3)

        if acknowledge:
            if rndAck==0:
                f.write(acknowledgeList[rndAck])

        f.write("module " + fileName + "(\n")

        if acknowledge:
            if rndAck==1:
                f.write(acknowledgeList[rndAck])

        if acknowledge:
            if rndAck==2:
                f.write(acknowledgeList[rndAck])

        if acknowledge:
            if rndAck==3:
                f.write(acknowledgeList[rndAck])

        f.write("endmodule\n")
        f.close()

        
        
                    
            


class Register(object):

    def __init__(self, regName, offsetInt):
        self.regName = regName
        self.offsetInt = offsetInt
        self.occupied = [False]*32
        self.segStartIndexList = []
        self.segNameList = []
        self.segDict = {}

    def addSegment(self, segment):
        start = segment.start
        end = segment.end
        segName = segment.segName
        if segName in self.segNameList:
            raise Exception("Segment " + segName + "already exists")
        else:
            self.segNameList.append(segName)
        if True in self.occupied[start:end+1]:
            raise Exception("Register" + self.regName + "Segment Overlapped");
        else:
            for i in range(start,end+1):
                self.occupied[i] = True
            self.segStartIndexList.append(start)
            self.segStartIndexList.sort()
            self.segDict[start] = segment

class Segment(object):

    def __init__(self, segName, start, end, segType):
        self.segName = segName
        self.start = start
        self.end = end
        self.width = self.start - self.end + 1
        self.segType = segType


class Project(object):

    def __init__(self, projectName, excelName):
        self.usedBaseAddrList = []
        self.moduleNameDict = {}
        self.validSheetList = []
        self.moduleDict = {}
        self.book = xlrd.open_workbook(excelName)
        self._listValidSheets()
        self.usedBaseAddrList.sort()
        self.projectName = projectName

    def _listValidSheets(self):
        for sheet in self.book.sheets():
            if not(sheet.nrows == 0 and sheet.ncols == 0):
                if sheet.row_values(0)[0] == "Module Name":
                    moduleName = sheet.row_values(0)[1]
                    if sheet.row_values(1)[0] == "Base Address":
                        addrInt = ProcessTools.baseAddressProcess(sheet.row_values(1)[1])
                        if addrInt in self.usedBaseAddrList:
                            raise Exception("Same base address happens in two module")
                        else:
                            self.usedBaseAddrList.append(addrInt)
                            self.moduleNameDict[addrInt] = moduleName
                            self.validSheetList.append(sheet)
                            if moduleName in self.moduleDict:
                                raise Exception("Modules with same module name exist")
                            else:
                                self.moduleDict[moduleName] = Module(moduleName, addrInt, sheet)

    def buildProjectRegVerilog(self):
        for m in self.moduleDict.values():
            m.buildModuleRegVerilog(projectName=self.projectName, acknowledge=True)
        

class ProcessTools(object):
    def _getAddressInInteger(rawString):
        rawString = rawString.lower().replace(' ', '').replace('_', '')
        if rawString.startswith("0x"):
            return int(rawString[2:], 16)

    def baseAddressProcess(rawString):
        addrInt = ProcessTools._getAddressInInteger(rawString)
        if addrInt%1024>0:
            raise Exception("Base address should align with 0x400")
        else:
            return addrInt

    def offsetAddressProcess(rawString):
        addrInt = ProcessTools._getAddressInInteger(rawString)
        if addrInt > 1020:
            raise Exception("Offset address should not exceed 0x3fc")
        elif addrInt%4>0:
            raise Exception("Offset address should aligh with word")
        else:
            return addrInt

    def indexProcess(rawString):
        import re
        p1 = r'\[(\d+)\]'
        p2 = r'\[(\d+):(\d+)\]'
        rawString = rawString.replace(' ', '')
        if rawString[0] == '[' and rawString[-1]== ']':
            if ':' in rawString:
                m = re.match(p2, rawString)
                try:
                    start = int(m.group(1))
                    end = int(m.group(2))
                except:
                    raise Exception("Index error!")  
            else:
                m = re.match(p1, rawString)
                try:
                    start = int(m.group(1))
                    end = int(m.group(1))
                except:
                    raise Exception("Index error!")
        else:
            raise Exception("Index error! Without []")
        if start>end:
            start, end = end, start
        return start,end

    def writeHeadComments(f, fileName, commentLenghth=66):
        from datetime import datetime
        now = datetime.now()
        f.write("// " + '='*commentLenghth + '\n')
        f.write("// " + "This file is automatically generated.".center(commentLenghth) + "\n")
        f.write("// " + "Scripts by Cheng Cai".center(commentLenghth) + "\n")
        f.write("// " + "File name".ljust(int(commentLenghth/3)) + ":  " + fileName + "\n")
        f.write("// " + "Generation time".ljust(int(commentLenghth/3))  + ":  " + str(now.year) + '-' + str(now.month) + '-' + str(now.day) + " "
                + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second) + "\n")
        f.write("// " + '='*commentLenghth + '\n')
        f.write('\n'*6)

    def writePortLine(f, portName, inOut, width=1, isReg=False, withComma=True, typeStartCol=10, widthStartCol=18, nameStartCol=28, cmtStartCol=48, cmt="", indentation=0):
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
    

if __name__ == "__main__":
    TEST_READ_PROCESS_EXCEL = False
    p = Project("StarRiver", "regen_template.xlsx")
    if TEST_READ_PROCESS_EXCEL:
        for m in p.moduleDict.values():
            print(m.moduleName)
            for r in m.regDict.values():
                print(str(r.offsetInt) + ":" + r.regName)
                print(r.occupied)
                for s in r.segNameList:
                    print(s)
    p.buildProjectRegVerilog()
    
                    
