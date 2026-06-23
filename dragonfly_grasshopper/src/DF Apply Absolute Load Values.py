# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply absolute load values to dragonfly Room2Ds.
_
Note that, while the assigned load values are absolute, this component will convert
them to the "normalized" value for each room (eg. lighting per floor area) in
order to apply them to the rooms. So any existing specification of load intensity
is overwritten with the absolute load here.
_
This also means that, if a room has no floors (or exterior walls for infiltration),
the resulting load values will be equal to 0 regardless of the input here. The
only exception is the vent_flow_, which will be applied regardless of the room
properties.
_
This component will not edit any of the schedules or other properties associated
with each load value. If no schedule currently exists to describe how the load
varies over the simulation, the "Always On" schedule will be used as a default.
-

    Args:
        _df_objs: Dragonfly Buildings, Stories or Room2Ds to which the input load
            values will be assigned. This can also be an etire dragonfly Model.
        person_count_: A number for the quantity of people in the room.
        lighting_watts_: A number for the installed wattage of lighting in the room (W).
        electric_watts_: A number for the installed wattage of electric equipment
            in the room (W).
        gas_watts_: A number for the installed wattage of gas equipment in the room (W).
        hot_wtr_flow_: Number for the peak flow rate of service hot water in the
            room in liters per hour (L/h).
        infiltration_ach_: A number for the infiltration flow rate in air changes per hour.

    Returns:
        report: Reports, errors, warnings, etc.
        df_objs: The input Dragonfly objects with their load values modified.
"""

ghenv.Component.Name = 'DF Apply Absolute Load Values'
ghenv.Component.NickName = 'AbsoluteLoadVals'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list
    from ladybug_rhino.config import conversion_to_meters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def extract_room2ds(obj):
    """Get all of the Room2Ds assinged to a given dragonfly object."""
    if isinstance(obj, Building):
        return obj.unique_room_2ds
    elif isinstance(obj, Story):
        return obj.room_2ds
    elif isinstance(obj, Room2D):
        return [obj]
    elif isinstance(obj, Model):
        return [room for bldg in obj.buildings for room in bldg.unique_room_2ds]
    else:
        raise ValueError(
            'Expected Dragonfly Room2D, Story, Building, or Model. '
            'Got {}.'.format(type(hb_obj)))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    df_objs = [obj.duplicate() for obj in _df_objs]

    # loop through the rooms and assign absolute loads
    for i, df_obj in enumerate(df_objs):
        for room in extract_room2ds(df_obj):
            # assign the person_count_
            if len(person_count_) != 0:
                room.properties.energy.person_count = longest_list(person_count_, i)
            # assign the lighting_watts_
            if len(lighting_watts_) != 0:
                room.properties.energy.lighting_watts = longest_list(lighting_watts_, i)
            # assign the electric_watts_
            if len(electric_watts_) != 0:
                room.properties.energy.electric_equipment_watts = longest_list(electric_watts_, i)
            # assign the gas_watts_
            if len(gas_watts_) != 0:
                room.properties.energy.gas_equipment_watts = longest_list(gas_watts_, i)
            # assign the hot_wtr_flow_
            if len(hot_wtr_flow_) != 0:
                room.properties.energy.hot_water_flow = longest_list(hot_wtr_flow_, i)
            # assign the infiltration_ach_
            if len(infiltration_ach_) != 0:
                room.properties.energy.infiltration_ach = longest_list(infiltration_ach_, i)
