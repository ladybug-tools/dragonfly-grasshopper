# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Separate and group dragonfly Room2Ds by any attribute that the room possesses.
_
This can be used to group Room2Ds by program, whether rooms are conditioned, etc.
-

    Args:
        _df_obj: A Dragonfly Model, Building, Story or Room2D to be separated
            and grouped based on room attributes.
        _attribute: Text for the name of the Room2D attribute by which the Room2Ds
            should be separated. The "DF Room2D Attributes" component lists
            all of the attributes of the Room2D.

    Returns:
        values: A list of values with one attribute value for each branch of the
            output rooms.
         room2ds: A data tree of honeybee rooms with each branch of the tree
            representing a different attribute value.
"""

ghenv.Component.Name = 'DF Room2Ds by Attribute'
ghenv.Component.NickName = 'Room2DsByAttr'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the core dragonfly dependencies
    from dragonfly.colorobj import ColorRoom2D
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # extract any rooms from input Models
    in_rooms = []
    for df_obj in _df_obj:
        if isinstance(df_obj, Model):
            in_rooms.extend(df_obj.room_2ds)
        elif isinstance(df_obj, Building):
            in_rooms.extend(df_obj.unique_room_2ds)
        elif isinstance(df_obj, Story):
            in_rooms.extend(df_obj.room_2ds)
        elif isinstance(df_obj, Room2D):
            in_rooms.append(df_obj)

    # use the ColorRoom object to get a set of attributes assigned to the rooms
    color_obj = ColorRoom2D(in_rooms, _attribute)
    values = color_obj.attributes_unique

    # loop through each of the room_2ds and get the attributes
    room2ds = [[] for val in values]
    for atr, room in zip(color_obj.attributes, in_rooms):
        atr_i = values.index(atr)
        room2ds[atr_i].append(room)
    room2ds = list_to_data_tree(room2ds)
