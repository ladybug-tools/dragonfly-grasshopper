# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Make the lowest unique Story(s) of a Building into basements.
_
This involves setting the outdoor walls of the basement stories to have ground
boundary conditions and setting the is_ground_contact property on all relevant
Room2Ds that are a basement or have a basement story below them.
-

    Args:
        _building: A Dragonfly Building that will have some if its stories set
            to be basements. This can also be an entire Dragonfly Model
            in which case all Buildings in the model will have their
            basements set.
        _bsmnt_count_: A positive integer for the number of unique Stories
            on the Building to make into basements. (Default: 1).
        remove_win_: Boolean to note whether basement Room2D segments with windows
            should have their outdoor boundary conditions and windows kept (True)
            or whether the windows should be removed in order to assign a ground
            boundary condition to all walls (False). (Default: False).

    Returns:
        df_obj: The input Dragonfly object with stories set to basements.
"""

ghenv.Component.Name = 'DF Make Basements'
ghenv.Component.NickName = 'MakeBasements'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.units import parse_distance_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.building import Building
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import units_system
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# tolerance for computing the pole of inaccessibility
p_tol = parse_distance_string('0.01m', units_system())


if all_required_inputs(ghenv.Component):
    # set defaults and duplicate the initial object
    basement_count = 1 if _bsmnt_count_ is None else _bsmnt_count_
    remove_windows = False if remove_win_ is None else remove_win_
    building = _building.duplicate()
    buildings = building.buildings if isinstance(building, Model) else [building]

    # loop through the buildings and make the basements
    for bldg in buildings:
        assert isinstance(bldg, Building), 'Expected Building. Got {}.'.format(type(bldg))
        bldg.make_basement_stories(basement_count, remove_windows, p_tol)
