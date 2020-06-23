from argparse import ArgumentParser
from pprint import PrettyPrinter
import os.path
import json

from lib import AvbParser, PMRReader


parser = ArgumentParser()
parser.add_argument('avbfile', help='avb file')
parser.add_argument('--pmrfile', help='pmr file')
parser.add_argument('--debug', action='store_true', default=False)
parser.add_argument('--mobtype')

args = parser.parse_args()

if args.pmrfile:
    pmr = PMRReader(args.pmrfile)
    mxf_files = []
    item = pmr.readnextitem()
    while item[0]:
        mxf_files.append(item[1])
        item = pmr.readnextitem()
else:
    mxf_files = None

avb = AvbParser(args.avbfile, mxf_files=mxf_files)
result = avb.transform()

print()
print()
print("Done parsing")
print()
print()

printer = PrettyPrinter(indent=2, width=200)


def collect_ids_and_tracks(result, mob_id):
    if mob_id not in result:
        return [], []
    ids = result[mob_id]['source_clips']
    tracks = result[mob_id]['tracks']

    for mid in result:
        if result[mid]['match_id'] == mob_id:
            ids.append(mid)

    return ids, tracks


def convert_path(folder, track):
    if not track:
        return

    return os.path.join(folder, track)


def add_path_to_tracks(pmrfile, tracks):
    abspath = os.path.abspath(pmrfile)
    folder = os.path.dirname(abspath)

    return [convert_path(folder, t) for t in tracks]


if args.debug:
    printer.pprint(result)
else:
    rr = {}
    for mob_id in result:
        if result[mob_id]['user_placed']:
            ids, tracks = collect_ids_and_tracks(result, mob_id)
            processed = [mob_id]
            ids = list(set(ids))

            while len(ids) > 0:
                ii, tt = collect_ids_and_tracks(result, ids[0])
                processed.append(ids[0])
                ids = list(set(ids[1:] + ii))
                ids = [i for i in ids if i not in processed]
                tracks = list(set(tt + tracks))
            tracks = [t for t in tracks if t != "Not generated"]
            if args.pmrfile:
                tracks = add_path_to_tracks(args.pmrfile, tracks)
            rr[mob_id] = {
                "tracks": tracks,
                "mob_type_id": result[mob_id]["mob_type_id"],
                "usage_code": result[mob_id]["usage_code"],
                "name": result[mob_id]["name"]
            }
    print(json.dumps(rr, indent=4, sort_keys=True))
    # printer.pprint(rr)

# if args.debug:
#     if args.mobtype:
#         printer.pprint(result[args.mobtype])
#     else:
#         printer.pprint(result)

#     if args.pmrfile:
#         print()
#         print()
#         print("PMR INFORMATION")
#         print()
#         print()
#         print(pmr.outprintable())
# else:
#     printer.pprint(result['MasterMob'])
