# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Set the ceiling plenum and/or floor plenum depth of rooms for any Dragonfly
object (Room2Ds, Stories, Buildings, Model).
-

    Args:
        _df_obj: A Dragonfly Model, Building, Story or Room2D to have plenum depths
            assigned to it.
        ceil_plenum_: A number for the depth that ceiling plenums extend into rooms.
            Setting this to a positive value will result in a separate plenum
            room being split off of the Room2D volume during translation from
            Dragonfly to Honeybee.
        floor_plenum_: A number for the depth that floor plenums extend into rooms.
            Setting this to a positive value will result in a separate plenum
            room being split off of the Room2D volume during translation from
            Dragonfly to Honeybee.

    Returns:
        report: Reports, errors, warnings, etc.
        df_obj: The input Dragonfly object with ceiling or floor plenum depths set.
"""

ghenv.Component.Name = 'DF Set Plenums'
ghenv.Component.NickName = 'SetPlenums'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    df_obj = [obj.duplicate() for obj in _df_obj]

    # extract rooms from inputs
    in_rooms = []
    for df_o in df_obj:
        if isinstance(df_o, Model):
            in_rooms.extend(df_o.room_2ds)
        elif isinstance(df_o, Building):
            in_rooms.extend(df_o.unique_room_2ds)
        elif isinstance(df_o, Story):
            in_rooms.extend(df_o.room_2ds)
        elif isinstance(df_o, Room2D):
            in_rooms.append(df_o)

    # set the plenum depths
    if ceil_plenum_ is not None:
        for rm in in_rooms:
            rm.ceiling_plenum_depth = ceil_plenum_
    if floor_plenum_ is not None:
        for rm in in_rooms:
            rm.floor_plenum_depth = floor_plenum_
