import avb
# import inspect

from .mxf_file_name_generator import MxfFileNameGenerator


class AvbParser():
    def __init__(self, filename, debug=False, mxf_files=None):
        self.data = avb.open(filename)
        self.debug = debug
        self.mxf_files = mxf_files
        self.mxf_file_name_generator = MxfFileNameGenerator(mxf_files)

    def transform(self):
        result = {}
        for item in self.data.content.items:
            # if not item.user_placed:
            # continue
            mob = item.mob
            if mob.mob_type == 'SourceMob':
                continue
            mob_id = self.parse_id(mob)
            name = mob.name

            tracks = self.build_track_list(mob)

            match_id = self.get_match_id(mob)

            result[mob_id] = {
                'mob_id': mob_id,
                'name': name,
                'user_placed': item.user_placed,
                'usage_code': mob.usage_code,
                'mob_type_id': mob.mob_type_id,
                'mob_type': mob.mob_type,
                'tracks': tracks,
                'match_id': match_id,
                'source_clips': self.get_source_clips(mob)
            }

        return result

    def get_match_id(self, mob):
        if not hasattr(mob, 'attributes'):
            return
        attr = mob.attributes
        # import IPython
        # IPython.embed()
        if not attr or '_MATCH' not in attr:
            return

        return self.parse_id(attr['_MATCH'])

    def get_source_clips(self, mob):

        result = []
        for track in mob.tracks:
            # import IPython
            # IPython.embed()
            component = track.component
            mob_id = self.parse_id(component)
            if mob_id:
                result.append(mob_id)
            if hasattr(component, 'tracks'):
                result = result + self.get_source_clips(component)

            if hasattr(component, 'components'):
                cc = component.components
                if callable(cc):
                    cc = cc()
                for c in cc:
                    mob_id = self.parse_id(c)
                    if mob_id:
                        result.append(mob_id)

        return result

    def parse(self):
        result = {
            "MasterMob": {},
        }

        for mob in self.data.content.mobs:
            if mob.mob_type not in result:
                result[mob.mob_type] = {}
            result[mob.mob_type][mob.name] = self.parse_mob(mob)

        return result

    def retrieve_component_mob_id(self, component):
        if hasattr(component, 'mob_id'):
            return component.mob_id

        if hasattr(component, 'components'):
            components = component.components
            if callable(components):
                components = components()

            for c in components:
                if hasattr(c, 'mob_id'):
                    return c.mob_id

    def parse_id(self, mob):
        if not hasattr(mob, 'mob_id'):
            return
        s = str(mob.mob_id)
        return s.split(':')[-1]

    def parse_mob(self, mob):
        result = {
            "type": mob.mob_type,
            "id": self.parse_id(mob)
        }

        if self.debug:
            result['property_data'] = mob.property_data

        if mob.mob_type == "MasterMob" or self.debug:
            result['tracks'] = self.build_track_list(mob)

        return result

    def build_track_list(self, mob):
        track_info = []
        for track in mob.tracks:
            component = track.component
            mob_id = self.retrieve_component_mob_id(component)
            mxf_file = self.mxf_file_name_generator.retrieve_by_mob_id(mob_id)

            if not mxf_file:
                if hasattr(component, 'mob_id'):
                    mxf_file = self.build_track_info(mob, component)
                else:
                    if component.name:
                        mxf_file = component.name
                    else:
                        mxf_file = "Not generated"
                        print(f"WARNING: not generating track name for {track} with {component}")

            if self.debug:
                component_components = []
                if hasattr(component, 'components'):
                    cc = component.components
                    if callable(cc):
                        cc = cc()
                    for c in cc:
                        component_components.append(c.property_data)
                track_info.append({
                    'mxf_file': mxf_file,
                    'component_property_data': component.property_data,
                    'track_property_data': track.property_data,
                    'component_components': component_components
                })
            else:
                track_info.append(mxf_file)

        if mob.name:
            if any(x == mob.name + '_v1' for x in track_info):
                track_info = [mob.name + '.mxf' if x == mob.name +
                              '_v1' else x + '.mxf' for x in track_info]

        track_info = [self.mxf_file_name_generator.display_warning(mxf_file) for mxf_file in track_info if track_info]

        return track_info

    def build_track_info(self, mob, component):
        mxf_file = self.mxf_file_name_generator.retrieve_by_mob_id(component.mob_id)
        if mxf_file:
            return mxf_file

        return self.mxf_file_name_generator.build_from_mob_and_component(mob, component)
