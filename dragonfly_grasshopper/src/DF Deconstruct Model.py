# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Deconstruct a Dragonfly Model object into all of its constituent Dragonfly objects.
-

    Args:
        _model: A Dragonfly Model to be deconstructed into into its constituent
            objects (Buildings, ContextShades).
    
    Returns:
        buildings: All of the Building objects contained within the input Model.
        context: All of the ContextShade objects within the input Model.
"""

ghenv.Component.Name = "DF Deconstruct Model"
ghenv.Component.NickName = 'DeconstructModel'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    buildings = _model.buildings
    context = _model.context_shades
