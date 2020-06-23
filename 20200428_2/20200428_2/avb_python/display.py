import re
import avb

from argparse import ArgumentParser


def cleanup_string(string):
    string = re.sub('at 0x[0-9a-f]+', 'at 0xXXX', string)
    return string


def display_object(obj, indent=""):
    if isinstance(obj, list):
        for idx, item in enumerate(obj):
            display_object(item, indent + f"[{idx}]")
    else:
        print(indent, cleanup_string(str(obj)))

        if hasattr(obj, 'propertydefs'):
            defs = [x.name for x in obj.propertydefs]
            for x in defs:
                if x == 'attributes':
                    if hasattr(obj, 'attributes') and obj.attributes:
                        attr = obj.attributes
                        for item in attr:
                            display_object(attr[item], indent=f"{indent}.{item}")
                elif hasattr(obj, x):
                    # print(indent, x, ":")
                    display_object(getattr(obj, x), indent=f"{indent}.{x}")


parser = ArgumentParser()
parser.add_argument('avbfile')

args = parser.parse_args()

data = avb.open(args.avbfile)

display_object(data.content)
