# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

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

ghenv.Component.Name = 'DF Visualize Wireframe'
ghenv.Component.NickName = 'VizWireF'
ghenv.Component.Message = '1.8.2'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry3d import Face3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
    from dragonfly.context import ContextShade
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.facetype import Floor
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3d_to_wireframe, \
        from_mesh3d_to_wireframe
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def room_2d_geometry(room_2ds):
    """Get Rhino geometry curves from a list of Room2Ds."""
    return [curve for room in room_2ds for curve in
            from_face3d_to_wireframe(room.floor_geometry)]


def room_3d_geometry(room_3ds):
    """Get Rhino geometry from a list of 3D Rooms."""
    room_geo = []
    for room in room_3ds:
        for face in room.faces:
            if isinstance(face.type, Floor):
                room_geo.extend(from_face3d_to_wireframe(face.geometry))
    return room_geo


def context_shade_geometry(context_shades):
    """Get Rhino geometry from a list of ContextShades."""
    shds = []
    for shd_geo in context_shades:
        for fc in shd_geo.geometry:
            go = from_face3d_to_wireframe(fc) if isinstance(fc, Face3D) else \
                from_mesh3d_to_wireframe(fc)
            shds.extend(go)
    return shds


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
            geo.extend(room_3d_geometry(df_obj.room_3ds))
            geo.extend(context_shade_geometry(df_obj.context_shades))
        elif isinstance(df_obj, Building):
            geo.extend(room_2d_geometry(df_obj.all_room_2ds()))
            geo.extend(room_3d_geometry(df_obj.room_3ds))
        elif isinstance(df_obj, Story):
            geo.extend(room_2d_geometry(df_obj.room_2ds))
        elif isinstance(df_obj, Room2D):
            geo.extend(room_2d_geometry([df_obj]))
        elif isinstance(df_obj, ContextShade):
            geo.extend(context_shade_geometry([df_obj]))
