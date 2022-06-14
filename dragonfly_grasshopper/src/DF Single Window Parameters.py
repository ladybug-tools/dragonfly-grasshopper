# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create Dragonfly window parameters with instructions for a single window in the
face center defined by a width and height.
_
Note that, if these parameters are applied to a base face that is too short
or too narrow for the input width and/or height, the generated window will
automatically be shortened when it is applied to the face. In this way,
setting the width to be a very high number will create parameters that always
generate a ribboin window of the input height.
-

    Args:
        _width: A number for the window width.
        _height: A number for the window height.
        _sill_height_: A number for the window sill height. Default: 0.8 meters.
    
    Returns:
        win_par: Window Parameters that can be applied to a Dragonfly object
            using the "DF Apply Facade Parameters" component.
"""

ghenv.Component.Name = "DF Single Window Parameters"
ghenv.Component.NickName = 'SingleWindowPar'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the core dragonfly dependencies
    from dragonfly.windowparameter import SingleWindow
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set defaults for any blank inputs
    conversion = conversion_to_meters()
    _sill_height_ = _sill_height_ if _sill_height_ is not None else 0.8 / conversion

    # create the window parameters
    if _width != 0 and _height != 0:
        win_par = SingleWindow(_width, _height, _sill_height_)