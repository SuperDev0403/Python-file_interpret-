from glob import glob

from lib import AvbParser


def test_parser():
    for filename in glob('files/*.avb'):
        print(filename)
        a = AvbParser(filename)
        a.parse()
        a.transform()
