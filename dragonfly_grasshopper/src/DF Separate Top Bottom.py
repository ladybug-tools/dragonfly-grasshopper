# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Separate the top and bottom floors of a Building into unique Stories with a multiplier
of 1 and automatically assign the first story Room2Ds to have a ground contact
floor and the top story Room2Ds to have an outdoor-exposed roof.
_
This is particularly helpful when trying to account for the heat exchange of the
top or bottom floors with the gound or outdoors.
-

    Args:
        _buildings: Dragonfly Building objects which will have their top and bottom
            stories separated into unique ones with a multiplier of 1.
            This can also be an entire Dragonfly Model.
        sep_mid_: Boolean to note whether all mid-level Stories with non-unity multipliers
            should be separated into two or three Stories. This means that the
            top of each unique story will have outdoor-exposed roofs when no Room2Ds
            are sensed above a given room. (Default: False).

    Returns:
        buildings: The Building objects with their top and bottom floors separated.
"""

ghenv.Component.Name = "DF Separate Top Bottom"
ghenv.Component.NickName = 'TopBottom'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # get the building objects from the input ones
    buildings = [bldg.duplicate() for bldg in _buildings]
    for bldg in buildings:
        if sep_mid_:
            if isinstance(bldg, Model):
                for b in bldg.buildings:
                    b.separate_mid_floors(tolerance)
            else:
                bldg.separate_mid_floors(tolerance)
        else:
            bldg.separate_top_bottom_floors()
