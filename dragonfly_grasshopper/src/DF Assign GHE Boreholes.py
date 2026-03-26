# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Assign borehole positions to the GHEs of a GHE Thermal Loop.
_
These borehole positions override the grid of auto-generated positions that
typically result from the GHE autosizing calculation and ensure that boreholes
can only be placed at the specified locations.
_
If a given GHE in the loop does not have any input boreholes associated with it,
it will be autosized with a grid of boreholes like usual.
-

    Args:
        _des_loop: The GHE Thermal Loop object output by the "DF GHE Thermal Loop",
            which contains the geometry of the district energy system.
        _boreholes: A list of points to be assigned to the GHEs of the loop in
            order to specify the exact locations of boreholes within each
            borehole field. Each input point will be evaluated against the
            loop's GHE geometry to determine if the borehole position lies
            within a given field.

    Returns:
        report: Reports, errors, warnings, etc.
        des_loop: The input GHE Thermal Loop with the borehole positions assigned to it.
        unassigned: Points that were not assigned to any GHEs within the Thermal Loop.
"""

ghenv.Component.Name = 'DF Assign GHE Boreholes'
ghenv.Component.NickName = 'GHELoop'
ghenv.Component.Message = '1.10.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.des.loop import GHEThermalLoop
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_point3d
    from ladybug_rhino.fromgeometry import from_point3d
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # process the inputs
    assert isinstance(_des_loop, GHEThermalLoop), \
        'Expected GHEThermalLoop for _des_loop. Got {}.'.format(type(_des_loop))
    des_loop = _des_loop.duplicate()
    boreholes = [to_point3d(pt) for pt in _boreholes]

    # assign the borehole positions to the loop
    unassigned = des_loop.assign_borehole_positions(boreholes)

    # give a warning about any aunassigned boreholes
    if len(unassigned) != 0:
        unassigned = [from_point3d(pt) for pt in unassigned]
        msg = 'A total of {} boreholes could not be associated with any GHE '\
            'geometry in the loop.'.format(len(unassigned))
        print(msg)
        give_warning(ghenv.Component, msg)
