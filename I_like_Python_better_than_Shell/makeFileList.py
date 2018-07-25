import os
import fnmatch
import getopt
import sys

def _filePathGenerator(fromPath, filePattern='*.[Vv]', verbose=False):
    for root, dirs, files in os.walk(fromPath):
        for name in files:
            if fnmatch.fnmatch(name, filePattern):
                if root.startswith('.'+os.sep):
                    cwd = root.replace('.'+os.sep, os.getcwd()+os.sep, 1)
                else:
                    cwd = root
                if verbose:
                    print("Find file: " + os.sep.join([cwd,name]))
                yield os.sep.join([cwd,name])

def makeFileList(fromPath, filePattern, fileListName, appending=False, verbose=False):
    if appending:
        mode = 'a'
    else:
        mode = 'w+'
    f = open(fileListName, mode)
    
    for path in _filePathGenerator(fromPath, filePattern, verbose):
        f.write(path+'\n')
    f.close()

def printManual():
    import textwrap
    basicInfo = "This script finds all the matching files recursively to the given \
                path and write them into the file-list file. This script is originally \
                aiming to be a rather easy way to create the file-list for VCS or NCVerilog \
                to compile and simulate a pack of verilog files. Thus a silent command without \
                any additional options will search all .v files to the current directory."

    print(" makeFileList ".center(66,'='))
    print('')
    print(textwrap.fill(basicInfo, 66))
    print('')
    print('Usage: python makeFileList.py [OPTIONS] [path...] [EXPR]')
    print('\n')
    print((' '*4 + '-a, --appending').ljust(30) + "Appending matching files to the list instead of renewing it")
    print((' '*4 + '-h, --help').ljust(30) + "Display the this help and exit")
    print((' '*4 + '-l, --list-name LIST_FILE_NAME').ljust(30) + "Specify the file list file name")
    print((' '*4 + '-v, --verbose').ljust(30) + "Verbose")
    print('')
    print('-'*66)
    print("This operation can be also realised by shell:")
    print('   find . -iname ".v" > file.f')
    print('-'*66)
    print('')
    print('='*66)
    print("Simon Cai's side project".center(66,'-'))
    print('='*66)
    
if __name__ == '__main__':
    verbose = False
    fromPath = os.getcwd()
    fileListName = "file.f"
    filePattern = '*.[Vv]'
    appending = False
    args = sys.argv
    optlist, args = getopt.getopt(args[1:], 'avhl:', ['appending', 'verbose', 'help', 'list-name='])
    for t in optlist:
        if t[0] in ['-v', '--verbose']:
            verbose = True
        elif t[0] in ['-h', '--help']:
            printManual()
            sys.exit()
        elif t[0] in ['-l', '--list-name']:
            if len(t[1])>0:
                fileListName = t[1]
        elif t[0] in ['-a', '--appending']:
            appending = True
        else:
            print("Unrecognized Option:" + t[0] + ", script terminates.")
            sys.exit()
    if len(args)==1:
        print("Must give both PATH to find files and the matching EXPR")
        sys.exit()
    elif len(args)>=2:
        fromPath = args[0]
        filePattern = args[1]
        

    makeFileList(fromPath, filePattern, fileListName, appending, verbose)
