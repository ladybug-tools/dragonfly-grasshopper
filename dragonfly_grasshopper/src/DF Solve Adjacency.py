# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Solve adjacencies between a series of dragonfly Room2Ds.
_
Note that rooms must have matching edge segments in order for them to be discovered
as adjacent.
-

    Args:
        _room2ds: A list of dragonfly Room2Ds for which adjacencies will be solved.
        _run: Set to True to run the component and solve adjacencies.
    
    Returns:
        report: Reports, errors, warnings, etc.
        adj_room2ds: The input Room2Ds but with adjacencies solved for between
            segments.
"""

ghenv.Component.Name = "DF Solve Adjacency"
ghenv.Component.NickName = 'SolveAdj2D'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

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
    adj_room2ds = [room.duplicate() for room in _room2ds] # duplicate the initial objects
    
    # solve adjacnecy
    Room2D.solve_adjacency(adj_room2ds, tolerance)
