# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Calculate downwelling horizontal infrared radiation intensity from sky cover,
dry bulb temperature, and dew point temperature.
-

    Args:
        _sky_cover: A value or data collection representing sky cover [tenths]
        _dry_bulb: A value or data collection representing  dry bulb temperature [C]
        _dew_point: A value or data collection representing dew point temperature [C]
    
    Returns:
        horiz_infrared: A data collection or value indicating the downwelling
            horizontal infrared radiation [W/m2]
"""

ghenv.Component.Name = "DF Horizontal Infrared"
ghenv.Component.NickName = 'HorizInfr'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '3 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:
    from ladybug.skymodel import calc_horizontal_infrared
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.datatype.energyflux import HorizontalInfraredRadiationIntensity
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if _sky_cover and _dry_bulb and _dew_point:
    horiz_infrared = HourlyContinuousCollection.compute_function_aligned(
        calc_horizontal_infrared, [_sky_cover, _dry_bulb, _dew_point],
        HorizontalInfraredRadiationIntensity(), 'W/m2')