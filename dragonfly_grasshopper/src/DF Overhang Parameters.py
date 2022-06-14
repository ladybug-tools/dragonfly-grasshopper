# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create Dragonfly shading parameters with instructions for a single overhang
(awning, balcony, etc.) over an entire wall.
-

    Args:
        _depth: A number for the overhang depth.
        _angle_: A number for the for an angle to rotate the overhang in degrees.
            Default is 0 for no rotation.
    
    Returns:
        shd_par: Shading Parameters that can be applied to a Dragonfly object
            using the "DF Apply Facade Parameters" component.
"""

ghenv.Component.Name = "DF Overhang Parameters"
ghenv.Component.NickName = 'OverhangPar'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "6"

try:  # import the core dragonfly dependencies
    from dragonfly.shadingparameter import Overhang
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    _angle_ = _angle_ if _angle_ is not None else 0.0
    shd_par = Overhang(_depth, _angle_)