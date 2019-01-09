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
        self.length = self.start - self.end + 1
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
    

if __name__ == "__main__":

    p = Project("StarRiver", "regen_template.xlsx")
    for m in p.moduleDict.values():
        print(m.moduleName)
        for r in m.regDict.values():
            print(str(r.offsetInt) + ":" + r.regName)
            print(r.occupied)
            for s in r.segNameList:
                print(s)
                    
