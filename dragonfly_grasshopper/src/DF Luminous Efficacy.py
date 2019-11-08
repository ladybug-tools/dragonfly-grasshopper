# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Esimtate sky illuminance from the irradiance contained within a WEA object.

-

    Args:
        _wea: A Ladybug WEA object.
        _dew_point:  An annual data collection representing dew point temperature [C].
    
    Returns:
        dir_ill: A data collection of direct normal illuminance values at each
            timestep of the WEA.
        diff_ill: A list of diffuse sky solar illuminance values at each
            timestep of the WEA.
        glob_ill: A list of global horizontal illuminance values at each
            timestep of the WEA.
"""

ghenv.Component.Name = "DF Luminous Efficacy"
ghenv.Component.NickName = 'LumEff'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '3 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

from ladybug.wea import Wea

if _wea is not None and isinstance(_wea, Wea) and _dew_point is not None:
    glob_ill, dir_ill, diff_ill, zen_lum = \
        _wea.estimate_illuminance_components(_dew_point)