class MxfFileNameGenerator():
    def __init__(self, mxf_files=None):
        self.mxf_files = mxf_files

    def retrieve_by_mob_id(self, mob_id):
        pieces = str(mob_id).split('.')
        if len(pieces) < 5:
            return

        id_code = str(mob_id).split('.')[4].upper()

        if self.mxf_files:
            for x in self.mxf_files:
                if id_code in x:
                    return x

    def build_from_mob_and_component(self, mob, component):
        name = mob.name
        if component.media_kind == 'sound':
            type_letter = 'A'
        else:
            type_letter = 'V'

        id_code = str(component.mob_id).split('.')[4].upper()
        number = str(component.track_id)

        return f"{name}.{type_letter}{number}{id_code}{type_letter}.mxf"

    def display_warning(self, mxf_file):
        if self.mxf_files and mxf_file not in self.mxf_files:
            print(f"WARNING: generated mxf filename {mxf_file} not found in pmr file")
            return

        return mxf_file
