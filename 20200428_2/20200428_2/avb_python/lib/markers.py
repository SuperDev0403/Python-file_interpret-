import avb
import random
import time
import datetime


def valid_mob(mob):
    if mob.mob_type_id == 2 and mob.usage_code == 7:
        return True
    if mob.mob_type_id == 1 and mob.usage_code in [2, 4]:
        return True

    return False


class Markers():
    def __init__(self, filename):
        self.data = avb.open(filename)

    def get_mobs(self):
        # mobs = [mob for mob in self.data.content.mobs if mob.mob_type in ['MasterMob', 'CompositionMob']]
        mobs = [mob for mob in self.data.content.mobs if valid_mob(mob)]
        return mobs

    def enumerate_components(self):
        result = {}
        for idx, mob in enumerate(self.get_mobs()):
            for t_idx, t in enumerate(mob.tracks):
                if hasattr(t, 'component'):
                    result[f"{idx}_{t_idx}"] = t.component

        return result

    def get_component_by_id(self, id):
        d = self.enumerate_components()
        if id not in d:
            return
        return d[id]

    def get_components(self):
        result = []

        for mob in self.get_mobs():
            for t in mob.tracks:
                # print(t)
                if hasattr(t, 'component'):
                    result.append(t.component)

        return result

    def get_markers(self, component):
        if hasattr(component, 'attributes'):
            if component.attributes and '_TMP_CRM' in component.attributes:
                return component.attributes['_TMP_CRM']

        return []

    def get_component(self, name):
        for c in self.get_components():
            if c.name == name:
                return c

    def write(self, filename):
        self.data.content.uid = random.randint(10**15, 10**16 - 1)
        self.data.write(filename)

    def create_marker(self, offset, text, color, user):
        marker = self.data.create.Marker()
        marker.mob_id = avb.mobid.UniqueMobID()
        marker.position = 0
        marker.comp_offset = offset
        marker.handled_codes = True
        # IPython.embed()
        marker.attributes = self.data.create.Attributes()
        marker.attributes['_ATN_CRM_LONG_CREATE_DATE'] = int(time.time())
        marker.attributes['_ATN_CRM_USER'] = user
        marker.attributes['_ATN_CRM_DATE'] = str(datetime.date.today())
        marker.attributes['_ATN_CRM_TIME'] = datetime.datetime.today().strftime("%H:%M")
        marker.attributes['_ATN_CRM_COLOR'] = color
        marker.attributes['_ATN_CRM_COM'] = text
        marker.attributes['_ATN_CRM_LONG_MOD_DATE'] = int(time.time())
        marker.attributes['_ATN_CRM_ID'] = '060a2b340101010501010f1013-000000-e1fd69f' + '%09x' % random.randrange(16**9) + '-' + '%05x' % random.randrange(16**5) + 'c8590ab-3577'
        marker.color = [13107, 52428, 52428]

        return marker

    def add_marker_to_attributes(self, attributes, marker):
        if '_TMP_CRM' in attributes:
            markers = attributes['_TMP_CRM']

            for m in markers:
                if m.comp_offset == marker.comp_offset:
                    m.attributes['_ATN_CRM_COM'] = m.attributes['_ATN_CRM_COM'] + ' ' + marker.attributes['_ATN_CRM_COM']

                    return markers

            markers.append(marker)
            return markers
        else:
            attributes['_TMP_CRM'] = self.data.create.TimeCrumbList()
            attributes['_TMP_CRM'].append(marker)
            return attributes['_TMP_CRM']

    def add_marker(self, component, marker):
        if not hasattr(component, 'components') or (component.attributes and '_TMP_CRM' in component.attributes):
            if not component.attributes:
                component.attributes = self.data.create.Attributes()
            self.add_marker_to_attributes(component.attributes, marker)
            return

        components = component.components
        if callable(components):
            components = components()
            print("Calling")

        for x in components:
            if x.class_id.decode() != 'SCLP':
                continue
            if hasattr(x, 'attributes'):
                if not x.attributes:
                    x.attributes = self.data.create.Attributes()

                self.add_marker_to_attributes(x.attributes, marker)

        return []
