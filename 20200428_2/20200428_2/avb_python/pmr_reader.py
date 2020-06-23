from lib.PMR import PMRReader
import os
import sys


def path2url(path):
    path = os.path.abspath(path)
    return 'file://' + path


p = PMRReader(sys.argv[1])
print(p.outprintable())
