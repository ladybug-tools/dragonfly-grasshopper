# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get properties of any Dragonfly geometry object.
-

    Args:
        _df_objs: A Dragonfly Model, Building, Story or Room2D for which
            properties will be output.
    
    Returns:
        height: For a Model or a Building, this will be the average height of the
            object above the ground. For a Story, this will be the floor-to-floor
            height and, for a Room2D, this will be the floor-to-ceiling height.
        floor_area: A number for the floor area  of all Rooms in the dragonfly object.
        ext_wall_area: A number for the total area of walls in the dragonfly object
            with an Outdoors boundary condition.
        ext_win_area: A number for the total area of windows in the dragonfly object
            with an Outdoors boundary condition.
        volume: A number for the volume of all Rooms in the dragonfly object.
"""

ghenv.Component.Name = 'DF Geometry Properties'
ghenv.Component.NickName = 'GeoProp'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # get the properties that all objects share
    floor_area = [df_obj.floor_area for df_obj in _df_objs]
    ext_wall_area = [df_obj.exterior_wall_area for df_obj in _df_objs]
    ext_win_area = [df_obj.exterior_aperture_area for df_obj in _df_objs]
    volume = [df_obj.volume for df_obj in _df_objs]

    # extract the height info by height
    height = []
    for df_obj in _df_objs:
        if isinstance(df_obj, Model):
            height.append(df_obj.average_height_above_ground)
        elif isinstance(df_obj, Building):
            height.append(df_obj.height_above_ground)
        elif isinstance(df_obj, Story):
            height.append(df_obj.floor_to_floor_height)
        elif isinstance(df_obj, Room2D):
            height.append(df_obj.floor_to_ceiling_height)
