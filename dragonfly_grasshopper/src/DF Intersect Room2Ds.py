# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Take a list of Dragonfly Room2Ds and split their adjacent Walls to ensure that
there are matching segments between each of the adjacent Room2Ds.
_
Note that this component effectively erases all assigned boundary conditions,
glazing parameters and shading parameters as the original segments are
subdivided. As such, it is recommended that this component be used before all
other steps when creating a Story.
_
Also note that this component does not actually set the walls that are next to one
another to be adjacent. The "DF Solve Adjacency" component must be used for this
after runing this component.
-

    Args:
        _room2ds: A list of Room2Ds for which adjacencent segments will be
            intersected.
        _run: Set to True to run the component.
    
    Returns:
        int_room2ds: An array of Room2Ds that have been intersected with one another.
            Note that these Room2Ds lack all assigned boundary conditions, glazing
            parameters and shading parameters of the original Room2Ds.
"""

ghenv.Component.Name = "DF Intersect Room2Ds"
ghenv.Component.NickName = 'IntRoom2D'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"


try:  # import the core dragonfly dependencies
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# add an compile toggle, set _compile to True to run the function
if all_required_inputs(ghenv.Component) and _run:
    int_room2ds = Room2D.intersect_adjacency(_room2ds, tolerance)