# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Solve adjacencies between the Room2Ds of Dragonfly objects.
-

    Args:
        _df_objs: A list of dragonfly Room2Ds for which adjacencies will be solved.
            This can also be Dragonfly Stories, Buildings or an entire Model,
            in which case each Story will have adjacencies solved across its
            Room2Ds.
        adiabatic_: Set to True to have all the discovered wall adjacencies set to
            an adiabatic boundary condition. If False, a Surface boundary
            condition will be used for all adjacencies. Note that adabatic
            conditions are not allowed if interior windows are assigned to
            interior walls. (Default: False).
        air_boundary_: Set to True to have all the discovered wall adjacencies set to
            an AirBoundary type. Note that AirBoundary types are not allowed
            if interior windows are assigned to interior walls. (Default: False).
        no_overwrite_: Boolean to note whether existing Surface boundary conditions should
            be preserved while solving adjacencies. If True, no intersection
            will occur and only newly-discovered adjacencies will be updated.
            If False or unspecified, all geometry will be cleaned and
            intersected before solving adjacencies. In either case, existing
            windows will be preserved.
            _
            Note that, to make use of this option effectively, Room2Ds must
            already have matching edge segments in order for them to be
            discovered as adjacent. The "DF Intersect Room2Ds" component
            can be used to ensure adjacent rooms have matching segments
            without changing any boundary conditions. (Default: False).
        _run: Set to True to run the component and solve adjacencies.

    Returns:
        report: Reports, errors, warnings, etc.
        df_objs: The input Dragonfly objects with adjacencies solved between the
            Room2D wall segments.
"""

ghenv.Component.Name = "DF Solve Adjacency"
ghenv.Component.NickName = 'SolveAdj2D'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import boundary_conditions
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.room2d import Room2D
    from dragonfly.story import Story
    from dragonfly.building import Building
    from dragonfly.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def room2d_solve_adj(adj_room2ds):
    """Solve adjacency across a list of Room2Ds."""
    # solve adjacnecy
    if no_overwrite_:  # only find adjacencies and re-assign them
        adj_info = Room2D.find_adjacency(adj_room2ds, tolerance)
        for wp in adj_info:
            wp[0][0].set_adjacency(wp[1][0], wp[0][1], wp[1][1])
    else:  # remove colinear vertices, intersect and solve
        for room in adj_room2ds:
            room.remove_colinear_vertices(tolerance)
        adj_room2ds = Room2D.intersect_adjacency(adj_room2ds, tolerance)
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

    return adj_room2ds


def solve_story(story_obj):
    """Solve adjacency across a story object."""
    story_obj._room_2ds = room2d_solve_adj(story_obj.room_2ds)


if all_required_inputs(ghenv.Component) and _run:
    # if all objects are Room2Ds, then solve adjacency across them
    if all(isinstance(obj, Room2D) for obj in _df_objs):
        df_objs = [r.duplicate() for r in _df_objs]
        df_objs = room2d_solve_adj(df_objs)
    else:  # solve adjacency across each story
        df_objs = []
        for obj in _df_objs:
            if isinstance(obj, Story):
                new_story = obj.duplicate()
                solve_story(new_story)
                df_objs.append(new_story)
            elif isinstance(obj, Building):
                new_bldg = obj.duplicate()
                for story in new_bldg.unique_stories:
                    solve_story(story)
                df_objs.append(new_bldg)
            elif isinstance(obj, Model):
                new_model = obj.duplicate()
                for bldg in new_model.buildings:
                    for story in bldg.unique_stories:
                        solve_story(story)
                df_objs.append(new_model)
