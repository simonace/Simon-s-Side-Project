import xlrd

class Module(object):
    def __init__(self, moduleName, baseAddressInt, busType, sheet):
        self.usedOffsetAddrList = []
        self.regNameDict = {}
        self.regDict = {}
        self.regStartRowList = []
        self.moduleName=moduleName
        self.busType = busType
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
                self.usedOffsetAddrList.sort()
            self.regNameDict[offsetInt] = regName
            if regName in self.regDict:
                raise Exception("Register with same module name exist in module " + self.moduleName)
            self.regDict[regName] = Register(regName, offsetInt)
            for k in range(self.regStartRowList[j], self.regStartRowList[j+1]):
                if self.sheet.row_values(k)[2].replace(' ', ''):
                    segName = self.sheet.row_values(k)[2].replace(' ', '')
                    segStart, segEnd = ProcessTools.indexProcess(self.sheet.row_values(k)[3])
                    segType = self.sheet.row_values(k)[4]
                    segPortIn = self.sheet.row_values(k)[5].replace(' ','')
                    segPortOut = self.sheet.row_values(k)[6].replace(' ','')
                    segDefaultValue = self.sheet.row_values(k)[7].replace(' ','')
                    self.regDict[regName].addSegment(Segment(segName, regName, segStart, segEnd, segType, segPortIn, segPortOut, segDefaultValue))

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
        if self.busType == "apb":
            ProcessTools.writePortLine(f=f, portName="PCLK", inOut="input", width=1, isReg=False)
            ProcessTools.writePortLine(f=f, portName="PCLKG", inOut="input", width=1, isReg=False)
            ProcessTools.writePortLine(f=f, portName="PRESETn", inOut="input", width=1, isReg=False)
            ProcessTools.writePortLine(f=f, portName="PSEL", inOut="input", width=1, isReg=False)
            ProcessTools.writePortLine(f=f, portName="PENABLE", inOut="input", width=1, isReg=False)
            ProcessTools.writePortLine(f=f, portName="PWRITE", inOut="input", width=1, isReg=False)
            ProcessTools.writePortLine(f=f, portName="PADDR", inOut="input", width=10, isReg=False)
            ProcessTools.writePortLine(f=f, portName="PWDATA", inOut="input", width=32, isReg=False)
            ProcessTools.writePortLine(f=f, portName="PRDATA", inOut="output", width=32, isReg=True)
            if acknowledge:
                if rndAck==1:
                    f.write(acknowledgeList[rndAck])
            port_t_list = []
            for offset in self.usedOffsetAddrList:
                reg = self.regDict[self.regNameDict[offset]]
                #f.write("// " + reg.regName + "\n")
                for segStartIndex in reg.segStartIndexList:
                    #f.write("// " + ' '*4 + reg.segDict[segStartIndex].segName + "\n")
                    for t in reg.segDict[segStartIndex].portOfSeg():
                        port_t_list.append(t)
            for tt in port_t_list[0:-1]:
                ProcessTools.writePortLine(f=f, portName=tt[0], inOut=tt[1], width=tt[2], isReg=tt[3], withComma=True)
            t = port_t_list[-1]
            ProcessTools.writePortLine(f=f, portName=t[0], inOut=t[1], width=t[2], isReg=t[3], withComma=False)
            f.write(");\n\n")
            

        if acknowledge:
            if rndAck==2:
                f.write(acknowledgeList[rndAck])
        if self.busType == "apb":
            ProcessTools.writeRegWireLine(f=f, name="w_en", regWire="wire", width=1)
            ProcessTools.writeRegWireLine(f=f, name="r_en", regWire="wire", width=1)
            ProcessTools.writeRegWireLine(f=f, name="PWDATA_in", regWire="wire", width=32)
            ProcessTools.writeRegWireLine(f=f, name="PADDR_gated", regWire="wire", width=10)
            for offset in self.usedOffsetAddrList:
                reg = self.regDict[self.regNameDict[offset]]
                if reg.hasWr:
                    ProcessTools.writeRegWireLine(f=f, name=reg.regName+"_w", regWire="wire", width=10)
            f.write("\n\n")

        if acknowledge:
            if rndAck==3:
                f.write(acknowledgeList[rndAck])

        if self.busType == "apb":
            f.write("assign PWDATA_in = ((PSEL==1'b1) & (PWRITE==1'b1)) ? PWDATA : 32'd0;\n")
            f.write("assign PADDR_gated = (PSEL==1'b1) ? PADDR : 10'h000;\n")
            f.write("assign w_en = PWRITE & PSEL;\n")
            f.write("assign r_en = PSEL & (~PWRITE) & PENABLE;\n\n")
            for offset in self.usedOffsetAddrList:
                reg = self.regDict[self.regNameDict[offset]]
                if reg.hasWr:
                    f.write("assign " + reg.regName + "_w = ((w_en == 1'b1) & (PADDR_gated == " + reg.getHexOffsetVerilog() + ")) ? 1'b1 : 1'b0;\n")
            f.write('\n\n')
            f.write("// PRDATA Read\n")
            f.write("always @(*) begin\n")
            f.write(' '*4 + "case({r_en,PADDR_gated})\n")
            for offset in self.usedOffsetAddrList:
                reg = self.regDict[self.regNameDict[offset]]
                if reg.hasRd:
                    f.write(' '*8 + ("{1'b1, "+reg.getHexOffsetVerilog()+'}').ljust(18) + ":   " + "begin\n")
                    f.write(' '*30 + "PRDATA = " + reg.getReadConcatRegister() + ";\n")
                    f.write(' '*30 + "end\n")
            f.write(' '*8 + "default".ljust(18) + ":   begin\n")
            f.write(' '*30 + "PRDATA = 32'b0;\n")
            f.write(' '*30 + "end\n")
            f.write(' '*4 + "endcase\n")
            f.write("end\n\n")

        if self.busType == "apb":
            for offset in self.usedOffsetAddrList:
                reg = self.regDict[self.regNameDict[offset]]
                for segStartIndex in reg.segStartIndexList:
                    seg = reg.segDict[segStartIndex]
                    f.write("// " + seg.regName + " - " + seg.segName + "\n")
                    if seg.segType == "cw0" or seg.segType == "ro" or seg.segType == "wr" or seg.segType == "wo":
                        if seg.segPortIn == 'y':
                            f.write("always @(posedge PCLK or negedge PRESETn) begin\n")
                        else:
                            f.write("always @(posedge PCLKG or negedge PRESETn) begin\n")
                        f.write(' '*4 + "if (!PRESETn) begin\n")
                        f.write(' '*8 + seg.regName + "_" + seg.segName + " <= " + seg.segDefaultValue + ";\n")
                        f.write(' '*4 + "end\n")
                        f.write(' '*4 + "else if (" + seg.regName + '_' + seg.segName + "_w) begin\n")
                        if seg.segType == "cw0":
                            if seg.width>1:
                                f.write(' '*8 + seg.regName + '_' + seg.segName + " <= " + seg.regName + '_' + seg.segName + " & PWDATA_gated[" + str(seg.end) + ":" + str(seg.start) + "];\n")
                            else:
                                f.write(' '*8 + seg.regName + '_' + seg.segName + " <= " + seg.regName + '_' + seg.segName + " & PWDATA_gated[" + str(seg.end) + "];\n")
                        else:
                            if seg.width>1:
                                f.write(' '*8 + seg.regName + '_' + seg.segName + " <= PWDATA_gated[" + str(seg.end) + ":" + str(seg.start) + "];\n")
                            else:
                                f.write(' '*8 + seg.regName + '_' + seg.segName + " <= PWDATA_gated[" + str(seg.end) + "];\n")
                        f.write(' '*4 + "end\n")
                        if seg.segPortIn == "y":
                            f.write(' '*4 + "else if (" + seg.regName + '_' + seg.segName + "_set) begin\n")
                            f.write(' '*8 + seg.regName + '_' + seg.segName + " <= " + seg.regName + '_' + seg.segName + "_set_value;\n")
                            f.write(' '*4 + "end\n")
                        f.write("end\n\n")
                    elif seg.segType == "const":
                        f.write("// const reg\n\n")
                    

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
        self.hasWr = False
        self.hasRd = False

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
        if segment.segType == "wr" or segment.segType == "wo":
            self.hasWr = True
        if segment.segType != "wo":
            self.hasRd = True

    def getHexOffsetVerilog(self):
        return "10'h" + hex(self.offsetInt)[2:]

    def getReadConcatRegister(self):
        concatRegString = "}"
        if len(self.segStartIndexList)>1:
            for i in range(len(self.segStartIndexList)-1):
                if i ==0:
                    if self.segDict[self.segStartIndexList[i]].start >0:
                        concatRegString = self.segDict[self.segStartIndexList[i]].getReadValueVerilog() + ', ' + str(self.segDict[self.segStartIndexList[i]].start) + "'b0" + concatRegString
                    else:
                        concatRegString = self.segDict[self.segStartIndexList[i]].getReadValueVerilog() +  concatRegString
                else:
                    concatRegString = self.segDict[self.segStartIndexList[i]].getReadValueVerilog() + ', ' + concatRegString
                if self.segDict[self.segStartIndexList[i+1]].start > self.segDict[self.segStartIndexList[i]].end + 2:
                    concatRegString = str(self.segDict[self.segStartIndexList[i+1]].start - self.segDict[self.segStartIndexList[i]].end -1) + "'b0, " + concatRegString
            concatRegString = self.segDict[self.segStartIndexList[-1]].getReadValueVerilog() + ', ' + concatRegString
            if self.segDict[self.segStartIndexList[-1]].end <31:
                concatRegString = str(31-self.segDict[self.segStartIndexList[-1]].end) + "'b0, " + concatRegString
        else:
            if self.segDict[self.segStartIndexList[0]].start >0:
                concatRegString = self.segDict[self.segStartIndexList[0]].getReadValueVerilog() + ', ' + str(self.segDict[self.segStartIndexList[0]].start) + "'b0" + concatRegString
            else:
                concatRegString = self.segDict[self.segStartIndexList[0]].getReadValueVerilog() +  concatRegString
            if self.segDict[self.segStartIndexList[0]].end <31:
                concatRegString = str(31-self.segDict[self.segStartIndexList[0]].end) + "'b0, " + concatRegString
        return '{' + concatRegString
        
        
class Segment(object):

    def __init__(self, segName, regName, start, end, segType, segPortIn, segPortOut, segDefaultValue):
        self.segName = segName
        self.regName = regName
        self.start = start
        self.end = end
        self.width = self.end - self.start + 1
        self.segType = segType
        self.segPortIn = segPortIn
        self.segPortOut = segPortOut
        self._fixedSegInout()
        self._processDefaultValue(segDefaultValue)

    def _processDefaultValue(self, rawHex):
        if rawHex[:2].lower() == "0x":
            self.segDefaultValue = str(self.width) + "'h" + rawHex[2:]
        else:
            raise Exception("Default Value Format Error!")

    def _fixedSegInout(self):
        if self.segType == "cw0" or self.segType == "ro":
            self.segPortIn = 'y'
        if self.segType == "const":
            self.segPortIn = 'n'
            self.segPortOut = 'n'
        if self.segType == "wo":
            self.segPortOut = 'y'
        if self.segPortOut == "y" or self.segPortOut == "yes":
            self.segPortOut = 'y'
        if self.segPortIn == "y" or self.segPortIn == "yes":
            self.segPortIn = 'y'
        if self.segPortOut == "n" or self.segPortOut == "no":
            self.segPortOut = 'n'
        if self.segPortIn == "n" or self.segPortIn == "no":
            self.segPortIn = 'n'

    def portOfSeg(self):
        #port in
        if self.segType == "const":
            yield (self.regName + "_" + self.segName + "_const_value", "input", self.width, False)
        elif self.segPortIn == "y" or self.segPortIn == "yes":
            yield (self.regName + "_" + self.segName + "_set", "input", 1, False)
            yield (self.regName + "_" + self.segName + "_set_value", "input", self.width, False)
        else:
            if self.segType == "cw0" or self.segType == "ro":
                yield (self.regName + "_" + self.segName + "_set", "input", 1, False)
                yield (self.regName + "_" + self.segName + "_set_value", "input", self.width, False)

        if self.segType != "ro" and self.segType != "const":
            if self.segPortOut == "y" or self.segPortOut == "yes":
                yield (self.regName + "_" + self.segName, "output", self.width, True)

    def getReadValueVerilog(self):
        if self.segType == "const":
            return self.regName + "_" + self.segName + "_const_value"
        elif self.segType == "wo":
            return str(self.width) + "'b0"
        else:
            return self.regName + "_" + self.segName
        


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
                    if sheet.row_values(2)[0] == "Bus Type":
                        busType = ProcessTools.busTypeProcess(sheet.row_values(2)[1])
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
                                self.moduleDict[moduleName] = Module(moduleName, addrInt, busType, sheet)

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

    def busTypeProcess(rawString):
        busType = rawString.replace(' ','').lower()
        if busType == "apb" or busType == "ahb":
            return busType
        else:
            raise Exception("Bus Type must be either APB or AHB")

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
        f.write("// " + "File name".ljust(int(commentLenghth/2)) + ":  " + fileName + "\n")
        f.write("// " + "Generation time".ljust(int(commentLenghth/2))  + ":  " + str(now.year) + '-' + str(now.month) + '-' + str(now.day) + " "
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

    def writeRegWireLine(f, name, regWire, width=1, withSemiComma=True, widthStartCol=10, nameStartCol=20, cmtStartCol=48, cmt="", indentation=0):
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
    
                    
