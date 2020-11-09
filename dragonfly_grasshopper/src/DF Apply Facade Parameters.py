# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply WindowParameters and/or ShadingParameters to any Dragonfly object (Building,
Story, Room2D).
-

    Args:
        _df_obj: A Dragonfly Building, Story or Room2D which will have the input
            WindowParameters and/or ShadingParameters assigned to it.
        _win_par_: A WindowParameter object that dictates how the window geometries
            will be generated for each of the walls. If None, the window
            parameters will remain unchanged across the input object. If an array
            of values are input here, different WindowParameters will be assigned
            based on cardinal direction, starting with north and moving clockwise.
        _shd_par_: A ShadingParameter objects that dictate how the shade geometries
            will be generated for each of the walls. If None, the shading
            parameters will remain unchanged across the input object. If an array
            of values are input here, different ShadingParameters will be assigned
            based on cardinal direction, starting with north and moving clockwise.
    
    Returns:
        df_obj: The input Dragonfly object with the WindowParameters and/or
            ShadingParameters assigned to it.
"""

ghenv.Component.Name = "DF Apply Facade Parameters"
ghenv.Component.NickName = 'ApplyFacadePar'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Outdoors
    from honeybee.orientation import angles_from_num_orient, orient_index
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def extract_room_2ds(df_objs):
    """Extract the Room2Ds from any dragonfly objects (Building, Story, etc.)"""
    rooms = []
    for obj in df_objs:
        if isinstance(obj, Building):
            rooms.extend(obj.unique_room_2ds)
        elif isinstance(obj, Story):
            rooms.extend(obj.room_2ds)
        elif isinstance(obj, Room2D):
            rooms.append(obj)
    return rooms


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    df_obj = [obj.duplicate() for obj in _df_obj]
    
    # add the window parameters
    if len(_win_par_) == 1:  # one window parameter for all
        for obj in df_obj:
            obj.set_outdoor_window_parameters(_win_par_[0])
    elif len(_win_par_) > 1:  # different window parameters by cardinal direction
        angles = angles_from_num_orient(len(_win_par_))
        rooms = extract_room_2ds(df_obj)
        for room in rooms:
            room_win_par = []
            for bc, orient in zip(room.boundary_conditions, room.segment_orientations()):
                orient_i = orient_index(orient, angles)
                win_p = _win_par_[orient_i] if isinstance(bc, Outdoors) else None
                room_win_par.append(win_p)
            room.window_parameters = room_win_par
    
    # add the shading parameters
    if len(_shd_par_) == 1:  # one shading parameter for all
        for obj in df_obj:
            obj.set_outdoor_shading_parameters(_shd_par_[0])
    elif len(_shd_par_) > 1:  # different shading parameters by cardinal direction
        angles = angles_from_num_orient(len(_shd_par_))
        rooms = extract_room_2ds(df_obj)
        for room in rooms:
            room_shd_par = []
            for bc, orient in zip(room.boundary_conditions, room.segment_orientations()):
                orient_i = orient_index(orient, angles)
                shd_p = _shd_par_[orient_i] if isinstance(bc, Outdoors) else None
                room_shd_par.append(shd_p)
            room.shading_parameters = room_shd_par
