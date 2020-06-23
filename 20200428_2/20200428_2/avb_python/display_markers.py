from pprint import PrettyPrinter
from argparse import ArgumentParser

from lib import Markers


parser = ArgumentParser()
parser.add_argument('avbfile', help='avb file')
parser.add_argument('--debug', action='store_true', default=False)

args = parser.parse_args()
printer = PrettyPrinter(indent=2, width=200)


def display_marker(marker):
    text = '--NO TEXT--'
    if '_ATN_CRM_COM' in marker.attributes:
        text = marker.attributes['_ATN_CRM_COM']
    print("   Marker", marker.comp_offset, "   ", text)
    if args.debug:
        printer.pprint(marker.property_data)
        print()


data = Markers(args.avbfile)
components = data.get_components()

for idx, component in data.enumerate_components().items():

    print(f"COMPONENT ({idx}) name {component.name} length {component.length}")

    for m in data.get_markers(component):
        display_marker(m)

    if hasattr(component, 'components'):
        if callable(component.components):
            ll = component.components()
        else:
            ll = component.components
        for x in ll:
            # if x.class_id.decode() != 'SCLP':
            # continue

            # print(x.property_data)
            for m in data.get_markers(x):
                display_marker(m)
    print()
    print()
