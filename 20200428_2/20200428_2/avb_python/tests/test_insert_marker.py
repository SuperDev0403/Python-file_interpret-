from glob import glob
import tempfile

from lib import Markers


def test_insert_markers():
    for filename in glob('files/*.avb'):
        print(filename)
        data = Markers(filename)

        for _, component in data.enumerate_components().items():
            marker = data.create_marker(0, 'xxx', 'red', 'me')
            data.add_marker(component, marker)

        filename = tempfile.mkstemp(suffix='.avb')[1]

        data.write(filename)
