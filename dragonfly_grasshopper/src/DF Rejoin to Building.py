# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Rejoin a list of Room2Ds that were originally a part of a Building back to a new
Building with updated Room2Ds.
_
In the event that the input contains Room2Ds that were not a part of an original
Building, this component can still be used but the stories will be regenerated
based on the Room2D floor elevations and a warning will be given.
-

    Args:
        _room2ds: A list of Dragonfly Room2D objects to be re-joined into Buildings.

    Returns:
        report: Reports, errors, warnings, etc.
        buildings: Dragonfly Buildings containing the input Room2Ds. This may be multiple
            buildings when the input Room2Ds originally had several different
            parent buildings.
"""

ghenv.Component.Name = 'DF Rejoin to Building'
ghenv.Component.NickName = 'Rejoin'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

from collections import OrderedDict

try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
    from dragonfly.colorobj import ColorRoom2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning, \
        document_counter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    room2ds = []
    for rm in _room2ds:
        assert isinstance(rm, Room2D), 'Expected Room2D. Got {}.'.format(type(rm))
        room2ds.append(rm.duplicate())

    # organize the rooms into a nested dictionary by story/building
    orphaned_rooms = []
    org_dict, bldg_dict = OrderedDict(), OrderedDict()
    for rm in room2ds:
        if rm.has_parent and rm.parent.has_parent:
            story = rm.parent
            bldg = story.parent
            if bldg.identifier not in bldg_dict:
                bldg_dict[bldg.identifier] = bldg
                org_dict[bldg.identifier] = OrderedDict()
            try:
                org_dict[bldg.identifier][story.identifier].append(rm)
            except KeyError:
                org_dict[bldg.identifier][story.identifier] = [rm]
        else:
            orphaned_rooms.append(rm)

    # re-generate the Buildings and add the new Room2Ds
    buildings = []
    for bldg in bldg_dict.values():
        new_bldg = bldg.duplicate()
        for story in new_bldg:
            try:
                rm_2ds = org_dict[bldg.identifier][story.identifier]
                story._room_2ds = ()
                story.add_room_2ds(rm_2ds)
            except KeyError:  # story missing from the input; raise an error
                msg = 'Building "{}" could not be reconstructed from the input Room2Ds.\n' \
                    'This is likely because the input Room2Ds were created using the "DF Deconstruct ' \
                    'All Object" component\ninstead of the "DF Deconstruct Object" ' \
                    'component, which preserves the connection of the Room2Ds to the ' \
                    'original Building.\nSo you should either relace this component on your ' \
                    'canvas or, if this is not possible, then you must create the ' \
                    'Building\nby joining the Rooms into a new "DF Story" and then ' \
                    'making a new "DF Building from Stories".'.format(new_bldg.display_name)
                print(msg)
                raise ValueError(msg)
        buildings.append(new_bldg)

    # if there were orphaned Room2Ds, add them to their own building
    if len(orphaned_rooms) != 0:
        # give a warning about the orphaned Room2Ds
        display_name = 'Building_{}'.format(document_counter('bldg_count'))
        name = clean_and_id_string(display_name)
        msg = '{} of the input Room2Ds were not a part of an original Dragonfly ' \
            'Building.\nThey have been added to a new Building with the auto-generated ' \
            'name "{}"\nBetter practice is to add these Room2Ds to new Stories and ' \
            'then a Building.'.format(len(orphaned_rooms), display_name)
        give_warning(ghenv.Component, msg)
        # create the stories and the building
        color_obj = ColorRoom2D(orphaned_rooms, 'floor_height')
        story_groups = [[] for val in values]
        values = color_obj.attributes_unique
        for atr, room in zip(color_obj.attributes, in_rooms):
            atr_i = values.index(atr)
            story_groups[atr_i].append(room)
        stories = [Story('{}_Story{}'.format(name, i), r_group)
                   for i, r_group in enumerate(story_groups)]
        o_building = Building(name, stories)
        o_building.display_name = display_name
        buildings.append(o_building)
