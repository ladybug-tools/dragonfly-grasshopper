# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Dragonfly window parameters with instructions for repeating rectangular
windows of a fixed width and height.
_
This effectively fills a wall with windows at the specified width, height
and separation.
-

    Args:
        _win_height_: A number for the target height of the windows.
            Note that, if the window_height is larger than the height of the wall,
            the generated windows will have a height equal to the wall height in
            order to avoid having windows extend outside the wall face. Default:
            2 meters.
        _win_width_: A number for the target width of the windows.
            Note that, if the window_width is larger than the width of the wall,
            the generated windows will have a width equal to the wall width in
            order to avoid having windows extend outside the wall face. Default:
            1.5 meters
        _sill_height_: A number for the target height above the bottom edge of
            the face to start the apertures. Note that, if the ratio is too large
            for the height, the ratio will take precedence and the sill_height
            will be smaller than this value. If an array of values are input here,
            different heights will be assigned based on cardinal direction, starting
            with north and moving clockwise. Default: 0.8 meters.
        _horiz_separ_: A number for the horizontal separation between
            individual aperture centerlines.  If this number is larger than
            the parent face's length, only one aperture will be produced.
            If an array of values are input here, different separation distances
            will be assigned based on cardinal direction, starting with north
            and moving clockwise. Default: 3 meters.
    
    Returns:
        win_par: Window Parameters that can be applied to a Dragonfly object
            using the "DF Apply Facade Parameters" component.
"""

ghenv.Component.Name = "DF Repeating Window Width Height Parameters"
ghenv.Component.NickName = 'RepeatingWHPar'
ghenv.Component.Message = '1.3.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the core dragonfly dependencies
    from dragonfly.windowparameter import RepeatingWindowWidthHeight
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
    _win_height_ = _win_height_ if _win_height_ is not None else 2.0 / conversion
    _win_width_ = _win_width_ if _win_width_ is not None else 1.5 / conversion
    _sill_height_ = _sill_height_ if _sill_height_ is not None else 0.8 / conversion
    _horiz_separ_ = _horiz_separ_ if _horiz_separ_ is not None else 3.0 / conversion
    
    win_par = RepeatingWindowWidthHeight(
        _win_height_, _win_width_, _sill_height_, _horiz_separ_)