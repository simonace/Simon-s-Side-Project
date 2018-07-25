import os
import os.path
import fnmatch
from shutil import copyfile
import getopt
import sys

def findAndCopy(fromPath, filePattern, toPath, verbose=False):
    fileNames = []
    for root, dirs, files in os.walk(fromPath):
        for name in files:
            if fnmatch.fnmatch(name, filePattern):
                if verbose:
                    print("Find file: " + os.sep.join([root,name]))
                if name not in fileNames:
                    fileNames.append(name)
                    oriPath = os.path.join(root, name)
                    _copyToPath(originalPath=oriPath ,toPath=toPath ,asName=name)
                else: 
                    nameMod = _modifyName(name)
                    if verbose:
                       print("WARNING: There exists file with same name for " + name + ", the copy will be renamed as " + nameMod)
                    fileNames.append(nameMod)
                    oriPath = os.path.join(root, name)
                    _copyToPath(originalPath=oriPath ,toPath=toPath ,asName=nameMod)

def _copyToPath(originalPath, toPath, asName):
    targetPath = os.path.join(toPath, asName)
    copyfile(originalPath, targetPath)

def _modifyName(rawName):
    l = rawName.split('.')
    l[-2] = l[-2]+"x"
    return '.'.join(l)

def printManual():
    import textwrap
    basicInfo = "This script finds all the matching files recursively to \
                the given path and copies them to a given destination. If \
                a replicated file name appears, the copy of the file will \
                be renamed. The whole original file system is not changed \
                at all."
    print(" findAndCopy Manual ".center(66,'='))
    print('')
    print(textwrap.fill(basicInfo,66))
    print('')
    print("Usage: python findAndCopy.py [OPTIONS] PATH_FIND EXPR PATH_COPY")
    print('\n')
    print((' '*4 + '-h, --help').ljust(30) + "Display the this help and exit")
    print((' '*4 + '-v, --verbose').ljust(30) + "Verbose")
    print('='*66)
    print("Simon Cai's side project".center(66,'-'))
    print('='*66)

if __name__ == '__main__':
    verbose = False
    args = sys.argv
    optlist, args = getopt.getopt(args[1:], 'vh', ['verbose','help'])
    for t in optlist:
        if t[0] in ['-v', '--verbose']:
            verbose = True
        elif t[0] in ['-h','--help']:
            printManual()
            sys.exit()
        else:
            print("Unrecognized Option:" + t[0] + ", script terminates.")
            sys.exit()
    
    findAndCopy(args[0],args[1], args[2], verbose)
