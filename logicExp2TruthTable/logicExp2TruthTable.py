i = "~~a | (b &~(c)) & ~c"

boolExpDict = {}
subExpIndex = {}


class Token(object):
    def __init__(self, rawString, depth, idx):
        self.rawString = rawString.lower()
        self.depth = depth
        self.idx = idx

class BoolExp(object):
    def __init__(self, boolType, start, end, i1=None, i2=None):
        self.start = start
        self.end = end
        self.boolType = boolType
        self.i1 = i1
        self.i2 = i2

    def cal(self, a, b, c):
        if self.boolType in ['1', '0']:
            return self.boolType
        if self.boolType == 'a':
            return str(a)
        if self.boolType == 'b':
            return str(b)
        if self.boolType == 'c':
            return str(c)
        if self.boolType == '&':
            ii1 = self.i1.cal(a, b, c)
            ii2 = self.i2.cal(a, b, c)
            if ii1=='1' and ii2=='1':
                return '1'
            else:
                return '0'
        if self.boolType == '|':
            ii1 = self.i1.cal(a, b, c)
            ii2 = self.i2.cal(a, b, c)
            if ii1=='0' and ii2=='0':
                return '0'
            else:
                return '1'
        if self.boolType == '(':
            return self.i1.cal(a, b, c)
        if self.boolType == '~':
            if self.i1.cal(a, b, c) == '0':
                return '1'
            else:
                return '0'



class ToolkitTB(object):
    def __init__(self):
        return None

    def tokenize(logicExpression):
        ruleDict = {'a': ['&', '|', ')'],
                    'b': ['&', '|', ')'],
                    'c': ['&', '|', ')'],
                    '1': ['&', '|', ')'],
                    '0': ['&', '|', ')'],
                    '~': ['a', 'b', 'c', '(', '~', '1', '0'],
                    '&': ['a', 'b', 'c', '(', '~', '1', '0'],
                    '|': ['a', 'b', 'c', '(', '~', '1', '0'],
                    '(': ['a', 'b', 'c', '(', '~', '1', '0'],
                    ')': ['&', '|', ')']}
        logicExpSr = logicExpression.replace(' ', '')
        depth = 0
        tokenChain = []
        lastS = '('
        idx = 0
        for s in logicExpSr:
            if s.lower() not in ['a', 'b', 'c', '1', '0', '~', '&', '|', '(', ')']:
                raise Exception("Unexpected input:" + s)
            if depth < 0:
                raise Exception("Unexpected right parenthese!")
            if s.lower() not in ruleDict[lastS.lower()]:
                errorExp = lastS + " can only be followed by any of "
                for ss in ruleDict[lastS.lower()]:
                    errorExp= errorExp + ss
                errorExp = errorExp + " , not by " + s
                raise Exception(errorExp)
            if s == ')':
                depth = depth - 1
            tokenChain.append(Token(s, depth, idx))
            if s == '(':
                depth = depth + 1
            lastS = s
            idx = idx + 1
        if depth != 0:
            raise Exception("Expect more right parenthese!")
        return tokenChain

    def parse(tokenChain):
        initDepth = tokenChain[0].depth
        leftP = []
        rightP = []
        inv = []
        abc10 = []
        i = 0
        andOr = []
        for t in tokenChain:
            if t.rawString == 'a' or t.rawString == 'b' or t.rawString == 'c' or t.rawString == '1' or t.rawString == '0':
                if t.depth == initDepth:
                    abc10.append(i)
            if t.rawString == '(':
                if t.depth == initDepth:
                    leftP.append(i)
            if t.rawString == ')':
                if t.depth == initDepth:
                    rightP.append(i)
            if t.rawString == '~':
                if t.depth == initDepth:
                    inv.append(i)
            if t.rawString == '&' or t.rawString == '|':
                if t.depth == initDepth:
                    andOr.append(i)
            i = i + 1
        for ao in andOr:
            yield(tokenChain[ao].rawString, tokenChain[ao].idx, tokenChain[ao].idx, initDepth)
        for x in abc10:
            yield(tokenChain[x].rawString, tokenChain[x].idx, tokenChain[x].idx, initDepth)
        for l,r in zip(leftP, rightP):
            yield ('(', tokenChain[l].idx, tokenChain[r].idx, initDepth)
        for ii in inv:
            yield ('~', tokenChain[ii].idx, tokenChain[ii].idx, initDepth)
        for l,r in zip(leftP, rightP):
            for tt in ToolkitTB.parse(tokenChain[l+1:r]):
                yield tt

    def boolExpGen(parseResultList):
        d = max(parseResultList, key=lambda k:k[3])[3]
        while d>=0:
            listOnDepth = []
            for ttt in parseResultList:
                if ttt[3] == d:
                    listOnDepth.append(ttt)
            listOnDepth = sorted(listOnDepth, key=lambda k: k[2])
            for t in listOnDepth:
                if t[0] in ['1', '0', 'a', 'b', 'c']:
                    boolExpDict[(t[1], t[2])] = BoolExp(t[0], t[1], t[2])
                    subExpIndex[t[1]] = (t[1], t[2])
                if t[0] == '(':
                    #print(t[1])
                    #print(subExpIndex[t[1]+1])
                    boolExpDict[(t[1], t[2])] = BoolExp(t[0], t[1], t[2], i1=boolExpDict[subExpIndex[t[1]+1]])
                    for i in range(t[1], t[2]+1):
                        subExpIndex[i] = (t[1], t[2])
            listOnDepth.reverse()
            for t in listOnDepth:
                if t[0] == '~':
                    boolExpDict[(t[1], subExpIndex[t[2]+1][1])] = BoolExp(t[0], t[1], subExpIndex[t[2]+1][1], i1=boolExpDict[subExpIndex[t[2]+1]])
                    for i in range(t[1], subExpIndex[t[2]+1][1]+1):
                        subExpIndex[i] = (t[1], subExpIndex[t[2]+1][1])
            #print(subExpIndex)
            #print(boolExpDict)
            listOnDepth.reverse()
            for t in listOnDepth:
                if t[0] in ['&', '|']:
                    #print(str(t[0]) + ' ' + str(t[1]) + ' '+ str(t[2]))
                    boolExpDict[(subExpIndex[t[1]-1][0], subExpIndex[t[2]+1][1])] = BoolExp(t[0], subExpIndex[t[1]-1][0], subExpIndex[t[2]+1][1], i1=boolExpDict[subExpIndex[t[1]-1]], i2=boolExpDict[subExpIndex[t[2]+1]])
                    for i in range(subExpIndex[t[1]-1][0], subExpIndex[t[2]+1][1]+1):
                        subExpIndex[i] = (subExpIndex[t[1]-1][0], subExpIndex[t[2]+1][1])
            d=d-1
                

    
            
        
                


if __name__ == "__main__":
    c = ToolkitTB.tokenize(i)
    ttt = []
    for xxx in ToolkitTB.parse(c):
        ttt.append(xxx)
    deepest = max(ttt, key=lambda k: k[3])[3]
    length = max(ttt, key=lambda k:k[2])[2] + 1
    for iiii in range(length):
        subExpIndex[iiii] = None
    #print(subExpIndex)
    ToolkitTB.boolExpGen(ttt)
    #print(subExpIndex)
    #print(boolExpDict)
    print("o = " + i + '\n')
    print("a b c | o |\n")
    print("------|---|\n")
    print("0 0 0 | " + boolExpDict[(0,length-1)].cal('0','0','0') + ' |\n')
    print("0 0 1 | " + boolExpDict[(0,length-1)].cal('0','0','1') + ' |\n')
    print("0 1 0 | " + boolExpDict[(0,length-1)].cal('0','1','0') + ' |\n')
    print("0 1 1 | " + boolExpDict[(0,length-1)].cal('0','1','1') + ' |\n')
    print("1 0 0 | " + boolExpDict[(0,length-1)].cal('1','0','0') + ' |\n')
    print("1 0 1 | " + boolExpDict[(0,length-1)].cal('1','0','1') + ' |\n')
    print("1 1 0 | " + boolExpDict[(0,length-1)].cal('1','1','0') + ' |\n')
    print("1 1 1 | " + boolExpDict[(0,length-1)].cal('1','1','1') + ' |\n')

    
    
    
