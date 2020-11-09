# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Dragonfly window parameters with instructions for a single window using
an area ratio with the base surface.
-

    Args:
        _ratio: A number between 0 and 1 for the ratio between the window
            area and the parent wall surface area.
    
    Returns:
        win_par: Window Parameters that can be applied to a Dragonfly object
            using the "DF Apply Facade Parameters" component.
"""

ghenv.Component.Name = "DF Simple Window Ratio Parameters"
ghenv.Component.NickName = 'SimpleRatioPar'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the core dragonfly dependencies
    from dragonfly.windowparameter import SimpleWindowRatio
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    win_par = SimpleWindowRatio(_ratio)