# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Dragonfly window parameters with instructions for repeating windows
derived from an area ratio with the base surface.
-

    Args:
        _ratio: A number between 0 and 0.95 for the ratio between the area of
            the apertures and the area of the parent face. If an array of values
            are input here, different ratios will be assigned based on
            cardinal direction, starting with north and moving clockwise.
        _subdivide_: Boolean to note whether to generate a single window in the
            center of each Face (False) or to generate a series of rectangular
            windows using the other inputs below (True). The latter is often more
            realistic and is important to consider for detailed daylight and
            thermal comfort simulations but the former is likely better when the
            only concern is building energy use since energy use doesn't change
            much while the window ratio remains constant. Default: True.
        _win_height_: A number for the target height of the output apertures.
            Note that, if the ratio is too large for the height, the ratio will
            take precedence and the actual aperture height will be larger
            than this value. If an array of values are input here, different
            heights will be assigned based on cardinal direction, starting with
            north and moving clockwise. Default: 2 meters.
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
        vert_separ_: An optional number to create a single vertical
            separation between top and bottom apertures. If an array of values
            are input here, different separation distances will be assigned based
            on cardinal direction, starting with north and moving clockwise.
            Default: 0.
    
    Returns:
        win_par: Window Parameters that can be applied to a Dragonfly object
            using the "DF Apply Facade Parameters" component.
"""

ghenv.Component.Name = "DF Repeating Window Ratio Parameters"
ghenv.Component.NickName = 'RepeatingRatioPar'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the core dragonfly dependencies
    from dragonfly.windowparameter import RepeatingWindowRatio
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
    _sill_height_ = _sill_height_ if _sill_height_ is not None else 0.8 / conversion
    _horiz_separ_ = _horiz_separ_ if _horiz_separ_ is not None else 3.0 / conversion
    vert_separ_ = vert_separ_ if vert_separ_ is not None else 0.0
    
    win_par = RepeatingWindowRatio(_ratio, _win_height_, _sill_height_,
                                    _horiz_separ_, vert_separ_)