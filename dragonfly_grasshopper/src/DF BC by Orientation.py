# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Make boundary conditions of Dragonfly Room2Ds Adiabatic or Ground by oreintation.
_
Note that this component will remove windows for any wall segment that is set to
have an Adiabatic or Ground boundary condition.
-

    Args:
        _df_obj: A Dragonfly Building, Story or Room2D which will have boundary conditions
            assigned to its walls according to the inputs below.
        adiabatic_: A list of Booleans to denote whether exterior walls of a given
            orientation should be set to adiabatic. Different adiabatic
            values will be assigned based on the cardinal direction,
            starting with north and moving clockwise. The "HB Facade
            Parameters" component can be used to order this list correctly
            for four main orientations.
        ground_: A list of Booleans to denote whether exterior walls of a given
            orientation should be set to ground. Different ground
            values will be assigned based on the cardinal direction,
            starting with north and moving clockwise. The "HB Facade
            Parameters" component can be used to order this list correctly
            for four main orientations.

    Returns:
        df_obj: The input Dragonfly object with the wall boundary conditions changed.
"""

ghenv.Component.Name = 'DF BC by Orientation'
ghenv.Component.NickName = 'BCByOrient'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import boundary_conditions, Outdoors
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


def apply_boundary_condition(rooms, bc_list, bc_to_assign):
    """Apply a boundary condition list to the dragonfly objects."""
    angles = angles_from_num_orient(len(bc_list))
    rooms = extract_room_2ds(df_obj)
    for room in rooms:
        room_bcs, room_glz = [], []
        zip_props = zip(room.boundary_conditions, room.window_parameters,
                        room.segment_orientations())
        for bc, glz, orient in zip_props:
            orient_i = orient_index(orient, angles)
            use_ad = bc_list[orient_i] if isinstance(bc, Outdoors) else None
            final_bc = bc_to_assign if use_ad else bc
            room_bcs.append(final_bc)
            final_glz = None if use_ad else glz
            room_glz.append(final_glz)
        room.window_parameters = room_glz
        room.boundary_conditions = room_bcs


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    df_obj = [obj.duplicate() for obj in _df_obj]
    rooms = extract_room_2ds(df_obj)

    # add the adiabatic parameters
    if len(adiabatic_) != 0:
        apply_boundary_condition(rooms, adiabatic_, boundary_conditions.adiabatic)

    # add the ground parameters
    if len(ground_) != 0:
        apply_boundary_condition(rooms, ground_, boundary_conditions.ground)
