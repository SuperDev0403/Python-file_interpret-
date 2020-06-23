import sys
import tempfile
import os

from argparse import ArgumentParser

from lib import Markers


parser = ArgumentParser()
parser.add_argument('avbfile', help='avb file')
parser.add_argument('--output', help='avb file to write to; Default behavior is overwrite current file', default=None)
parser.add_argument('--id', help="Id of component e.g. 2_1")
parser.add_argument('--name', help='component name e.g. "A001_03060916_C022_A01"')
parser.add_argument('--offset', default=0, type=int)
parser.add_argument('--text', default="bla")
parser.add_argument('--color', default="Cyan")
parser.add_argument('--user', default="davidnorden")

args = parser.parse_args()


data = Markers(args.avbfile)

if args.id:
    component = data.get_component_by_id(args.id)
else:
    component = data.get_component(args.name)

if not component:
    print("Component not found")
    sys.exit(1)

length = component.length
print("Found component", component, "with length", length)

if args.offset >= length:
    print("Offset larger than length")
    sys.exit(1)


new_marker = data.create_marker(args.offset, args.text, args.color, args.user)
ms = data.add_marker(component, new_marker)

filename = tempfile.mkstemp(suffix='.avb')[1]
data.write(filename)

if args.output:
    os.rename(filename, args.output)
else:
    os.rename(filename, args.avbfile)
