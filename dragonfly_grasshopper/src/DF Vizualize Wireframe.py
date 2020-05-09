# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Quickly preview any Dragonfly geometry object as a wire frame within the Rhino
scene, including all stories represented by multipliers
-

    Args:
        _df_objs: A Dragonfly Model, Building, Story, Room2D, or ContextShade to
            be previewed as a wire frame in the Rhino scene.
    
    Returns:
        geo: The Rhino version of the Dragonfly geometry object, which will be
            visible in the Rhino scene.
"""

ghenv.Component.Name = 'DF Vizualize Wireframe'
ghenv.Component.NickName = 'VizWireF'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
    from dragonfly.context import ContextShade
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3d_to_wireframe
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def room_2d_geometry(room_2ds):
    """Get Rhino geometry from a list of Room2Ds."""
    return [from_face3d_to_wireframe(room.floor_geometry) for room in room_2ds]


def context_shade_geometry(context_shades):
    """Get Rhino geometry from a list of ContextShades."""
    return [from_face3d_to_wireframe(fc) for shd_geo in context_shades
            for fc in shd_geo.geometry]


if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    geo = []

    # loop through all objects and add them
    for df_obj in _df_objs:
        if isinstance(df_obj, Model):
            rooms = []
            for bldg in df_obj.buildings:
                rooms.extend(bldg.all_room_2ds())
            geo.extend(room_2d_geometry(rooms))
            geo.extend(context_shade_geometry(df_obj.context_shades))
        elif isinstance(df_obj, Building):
            geo.extend(room_2d_geometry(df_obj.all_room_2ds()))
        elif isinstance(df_obj, Story):
            geo.extend(room_2d_geometry(df_obj.room_2ds))
        elif isinstance(df_obj, Room2D):
            geo.extend(room_2d_geometry([df_obj]))
        elif isinstance(df_obj, ContextShade):
            geo.extend(context_shade_geometry([df_obj]))
