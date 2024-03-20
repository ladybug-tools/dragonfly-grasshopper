# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a Dragonfly Building from detailed Honeybee Rooms.
_
This is useful when there are parts of the Building geometry that cannot easily
be represented with the extruded floor plate and sloped roof assumptions that
underlie Dragonfly Room2Ds and RoofSpecification. Cases where this input is most
useful include sloped walls and certain types of domed roofs that become tedious
to implement with RoofSpecification.
-

    Args:
        base_bldg_: An optional Dragonfly Building.
        _hb_rooms: Honeybee Room objects for additional Rooms that are a part of the
            Building but are not represented within the Stories or Room2Ds.
            Matching the Honeybee Room story property (assigned with the
            "HB Set Multiplier" component) to the Dragonfly Story name
            will effectively place the Honeybee Room on that Story for the
            purposes of floor_area, exterior_wall_area, etc. However, note
            that the Honeybee Room.multiplier property takes precedence over
            whatever multiplier is assigned to the Dragonfly Story that the
            Room.story may reference.
        _name_: Text to set the name for the Building, which will also be incorporated
            into unique Building identifier. If the name is not provided a random
            one will be assigned.

    Returns:
        report: Reports, errors, warnings, etc.
        building: Dragonfly Building.
"""

ghenv.Component.Name = 'DF Building from Detailed Rooms'
ghenv.Component.NickName = 'BuildingHBRooms'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_string, clean_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, document_counter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # generate a default identifier
    if _name_ is None:  # get a default Building name
        display_name = 'Building_{}'.format(document_counter('bldg_count'))
        name = clean_and_id_string(display_name)
    else:
        display_name = _name_
        name = clean_string(display_name)

    # create the Building
    room_3ds = [r.duplicate() for r in _hb_rooms]
    if base_bldg_ is not None:
        building = base_bldg_.duplicate()
        building = name
        building.add_room_3ds(room_3ds)
    else:  # make the building entirely from the 
        building = Building(name, room_3ds=room_3ds)
    building.display_name = display_name
