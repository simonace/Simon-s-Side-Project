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
    #print(c.portDictByIndex)
    print(len(c.portDictByIndex))
    for i,p in c.portDictByIndex.items():
        print(str(i) + ":" + p.portName)
    print("\n")
    for r,f in c.funcDictByRow.items():
        print(str(r) + ":" + f.funcName + " " + f.funcDir)
    print(c.crossCoList)
    print((2,6) in c.crossCoList)
    print((3,6) in c.crossCoList)
