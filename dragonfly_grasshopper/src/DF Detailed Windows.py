# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
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
        _windows: A list of Breps that will be added to the input _df_objs as
            detailed windows.

    Returns:
        report: Reports, errors, warnings, etc.
        df_objs: The input dragonfly objects with the input _windows added to it.
"""

ghenv.Component.Name = "DF Detailed Windows"
ghenv.Component.NickName = 'DetailedWindows'
ghenv.Component.Message = '1.5.0'
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

try:
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.config import tolerance, angle_tolerance
    from ladybug_rhino.togeometry import to_face3d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects and convert windows to Face3D
    df_objs = [obj.duplicate() for obj in _df_objs]
    win_geo = [f for geo in _windows for f in to_face3d(geo)]

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
        new_win_pars = []
        for seg, win_par in zip(room.floor_segments, room.window_parameters):
            win_to_add = []
            for geo in win_geo:
                if DetailedWindows.is_face3d_in_segment_plane(
                        geo, seg, room.floor_to_ceiling_height,
                        tolerance, angle_tolerance):
                    win_to_add.append(geo)
            if len(win_to_add) != 0:
                det_win = DetailedWindows.from_face3ds(win_to_add, seg)
                new_win_pars.append(det_win)
            else:
                new_win_pars.append(win_par)
        room.window_parameters = new_win_pars
