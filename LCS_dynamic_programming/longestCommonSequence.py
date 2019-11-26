str1 = "nvahofnqkknvqonkcbaoqncnqqfkjanvanldlkjjgnlq"
str2 = "fjaslvlnoqflnvljqllvknlandfvalknvonqonvla"
lcsLengthDict = {}
maxLen = 0
lcsDict = {}


for i in range(len(str1)):
    for j in range(len(str2)):
        if str1[i] == str2[j]:
            if i != 0 and j !=0:
                lcsLen = lcsLengthDict[(i-1, j-1)] +1
            else:
                lcsLen = 1
            if lcsLen==maxLen:
                lcsDict[lcsLen].append((i,j))
            elif lcsLen>maxLen:
                lcsDict[lcsLen] = []
                lcsDict[lcsLen].append((i, j))
                maxLen = lcsLen
        else:
            lcsLen = 0
        lcsLengthDict[(i, j)] = lcsLen

print("Longest common sequence length is " + str(maxLen))
for t in lcsDict[maxLen]:
    print("Index: " + str(t))
    print("LCS: " + str1[t[0]+1-maxLen:t[0]+1])
