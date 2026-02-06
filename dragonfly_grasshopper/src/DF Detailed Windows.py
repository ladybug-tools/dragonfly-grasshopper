# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Add detailed window geometries to Dragonfly Room2Ds.
-

    Args:
        _df_objs: A Dragonfly Model, Building, Story or Room2D, to which the _windows
            should be added.
        _windows: A list of Breps that will be added to the input _df_objs as detailed
            windows. This can also be a list of orphaned Honeybee Apertures and/or
            Doors to be added to the Dragonfly objects. In the case of Doors, they
            will be assigned to the Dragonfly object as such.
        project_dist_: An optional number to be used to project the Aperture/Door geometry
            onto parent Faces. If specified, then sub-faces within this distance
            of the parent Face will be projected and added. Otherwise,
            Apertures/Doors will only be added if they are coplanar with a parent Face.

    Returns:
        report: Reports, errors, warnings, etc.
        df_objs: The input dragonfly objects with the input _windows added to it.
"""

ghenv.Component.Name = "DF Detailed Windows"
ghenv.Component.NickName = 'DetailedWindows'
ghenv.Component.Message = '1.9.1'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the core dragonfly dependencies
    from dragonfly.windowparameter import DetailedWindows
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.aperture import Aperture
    from honeybee.door import Door
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.config import current_tolerance, angle_tolerance
    from ladybug_rhino.togeometry import to_face3d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
tolerance = current_tolerance()


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects and convert windows to sub-faces
    df_objs = [obj.duplicate() for obj in _df_objs]
    win_geo = []
    for geo in _windows:
        if isinstance(geo, (Aperture, Door)):
            win_geo.append(geo)
        else:
            for f in to_face3d(geo):
                win_geo.append(Aperture('Dummy_Ap', f))
    project_dist = 0 if project_dist_ is None else project_dist_

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
        room.assign_sub_faces(win_geo, project_dist, tolerance=tolerance,
                              angle_tolerance=angle_tolerance)
