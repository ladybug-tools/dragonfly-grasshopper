# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Quickly preview any Dragonfly geometry object within the Rhino scene.
_
Any stories represented by multipliers will not be included in the output, allowing
for a faster preview of large lists of objects but without the ability to check the
multipliers of objects.
-

    Args:
        _df_objs: A Dragonfly Model, Building, Story, Room2D, or ContextShade to
            be previewed in the Rhino scene.

    Returns:
        geo: The Rhino version of the Dragonfly geometry object, which will be
            visible in the Rhino scene.
"""

ghenv.Component.Name = 'DF Visualize Quick'
ghenv.Component.NickName = 'VizQuick'
ghenv.Component.Message = '1.8.1'
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

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3d, from_face3d_to_solid , \
        from_polyface3d, from_mesh3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def room_2d_geometry(room_2ds):
    """Get Rhino geometry from a list of Room2Ds."""
    room_geo = []
    for room in room_2ds:
        if room.has_parent and room.parent.roof is not None:
            hb_rm, adj_info = room.to_honeybee()
            room_geo.append(from_polyface3d(hb_rm.geometry))
        else:
            room_geo.append(
                from_face3d_to_solid(room.floor_geometry, room.floor_to_ceiling_height))
    return room_geo


def room_3d_geometry(room_3ds):
    """Get Rhino geometry from a list of 3D Rooms."""
    room_geo = []
    for room in room_3ds:
        room_geo.append(from_polyface3d(room.geometry))
    return room_geo


def context_shade_geometry(context_shades):
    """Get Rhino geometry from a list of ContextShades."""
    shds = []
    for shd_geo in context_shades:
        for fc in shd_geo.geometry:
            go = from_face3d(fc) if isinstance(fc, Face3D) else from_mesh3d(fc)
            shds.append(go)
    return shds


if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    geo = []

    # loop through all objects and add them
    for df_obj in _df_objs:
        if isinstance(df_obj, Model):
            geo.extend(room_2d_geometry(df_obj.room_2ds))
            geo.extend(room_3d_geometry(df_obj.room_3ds))
            geo.extend(context_shade_geometry(df_obj.context_shades))
        elif isinstance(df_obj, Building):
            geo.extend(room_2d_geometry(df_obj.unique_room_2ds))
            geo.extend(room_3d_geometry(df_obj.room_3ds))
        elif isinstance(df_obj, Story):
            geo.extend(room_2d_geometry(df_obj.room_2ds))
        elif isinstance(df_obj, Room2D):
            geo.extend(room_2d_geometry([df_obj]))
        elif isinstance(df_obj, ContextShade):
            geo.extend(context_shade_geometry([df_obj]))
