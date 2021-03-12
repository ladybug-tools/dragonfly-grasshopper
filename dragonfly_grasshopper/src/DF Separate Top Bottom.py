# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Separate the top and bottom floors of a Building into unique Stories with a multiplier
of 1 and automatically assign the first story Room2Ds to have a ground contact
floor and the top story Room2Ds to have an outdoor-exposed roof.
_
This is particularly helpful when using to_honeybee workflows with
multipliers but one wants to account for the heat exchange of the top
or bottom floors with the gound or outdoors.
-

    Args:
        _buildings: Dragonfly Building objects which will have their top and bottom
            stories separated into unique ones with a multiplier of 1.
    
    Returns:
        buildings: The Building objects with their top and bottom floors separated.
"""

ghenv.Component.Name = "DF Separate Top Bottom"
ghenv.Component.NickName = 'TopBottom'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    buildings = []
    for bldg in _buildings:
        new_bldg = bldg.duplicate()
        new_bldg.separate_top_bottom_floors()
        buildings.append(new_bldg)
