# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Solve adjacencies between a series of dragonfly Room2Ds.
_
Note that rooms must have matching edge segments in order for them to be discovered
as adjacent. The "DF Intersect Room2Ds" component can be used to ensure adjacent
rooms have matching segments.
-

    Args:
        _room2ds: A list of dragonfly Room2Ds for which adjacencies will be solved.
        adiabatic_: Set to True to have all of the adjacencies discovered by this
            component set to an adiabatic boundary condition. If False, a Surface
            boundary condition will be used for all adjacencies. Note that adabatic
            conditions are not allowed if interior windows are assigned to interior
            walls. (Default: False).
        air_boundary_: Set to True to have all of the wall adjacencies discovered
            by this component set to an AirBoundary type. Note that AirBoundary
            types are not allowed if interior windows are assigned to interior
            walls. (Default: False).
        overwrite_: Boolean to note whether existing Surface boundary conditions
            should be overwritten. If False or None, only newly-assigned
            adjacencies will be updated.
        _run: Set to True to run the component and solve adjacencies.

    Returns:
        report: Reports, errors, warnings, etc.
        adj_room2ds: The input Room2Ds but with adjacencies solved for between
            segments.
"""

ghenv.Component.Name = "DF Solve Adjacency"
ghenv.Component.NickName = 'SolveAdj2D'
ghenv.Component.Message = '1.5.1'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import boundary_conditions
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    adj_room2ds = [] # duplicate the initial objects
    for room in _room2ds:
        assert isinstance(room, Room2D), 'Expected Room2D. Got {}.'.format(type(room))
        adj_room2ds.append(room.duplicate())

    # solve adjacnecy
    if overwrite_:  # find adjscencies and re-assign them
        adj_info = Room2D.find_adjacency(adj_room2ds, tolerance)
        for wp in adj_info:
            wp[0][0].set_adjacency(wp[1][0], wp[0][1], wp[1][1])
    else:
        adj_info = Room2D.solve_adjacency(adj_room2ds, tolerance)

    # set adiabatic boundary conditions if requested
    if adiabatic_:
        for room_pair in adj_info:
            for room_adj in room_pair:
                room, wall_i = room_adj
                room.set_boundary_condition(wall_i, boundary_conditions.adiabatic)

    # set air boundary type if requested
    if air_boundary_:
        for room_pair in adj_info:
            for room_adj in room_pair:
                room, wall_i = room_adj
                room.set_air_boundary(wall_i)
