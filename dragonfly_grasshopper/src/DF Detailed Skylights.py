# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Add detailed skylight geometries to Dragonfly Room2Ds.
-

    Args:
        _df_objs: A Dragonfly Model, Building, Story or Room2D, to which the _windows
            should be added.
        _skylights: A list of Breps that will be added to the input _df_objs as
            detailed skylights.

    Returns:
        report: Reports, errors, warnings, etc.
        df_objs: The input dragonfly objects with the input _windows added to it.
"""

ghenv.Component.Name = 'DF Detailed Skylights'
ghenv.Component.NickName = 'DetailedSkylights'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry2d import Point2D, Polygon2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.skylightparameter import DetailedSkylights
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.config import tolerance, angle_tolerance
    from ladybug_rhino.togeometry import to_face3d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects and convert skylights to Face3D
    df_objs = [obj.duplicate() for obj in _df_objs]
    sky_faces = [f for geo in _skylights for f in to_face3d(geo)]
    sky_polys = [Polygon2D((Point2D(pt.x, pt.y) for pt in f.boundary)) for f in sky_faces]

    # collect all of the Room2Ds in the connected dragonfly objects
    room_2ds = []
    for df_obj in df_objs:
        if isinstance(df_obj, Model):
            room_2ds.extend(df_obj.room_2ds)
        elif isinstance(df_obj, Building):
            room_2ds.extend(df_obj.unique_room_2ds)
        elif isinstance(df_obj, Story):
            room_2ds.extend(df_obj.room_2ds)
        elif isinstance(df_obj, Room2D):
            room_2ds.append(df_obj)

    # assign the relevant geometries to the Room2Ds
    for room in room_2ds:
        if room.is_top_exposed:
            room_bound = room.floor_geometry.boundary_polygon2d
            hole_polys = room.floor_geometry.hole_polygon2d
            geo_to_add = []
            for geo in sky_polys:
                if room_bound.is_polygon_inside(geo):
                    if not hole_polys:
                        geo_to_add.append(geo)
                    elif all(hp.is_polygon_outside(geo)):
                            geo_to_add.append(geo)
            if len(geo_to_add) != 0:
                det_sky = DetailedSkylights(geo_to_add)
                room.skylight_parameters = det_sky
