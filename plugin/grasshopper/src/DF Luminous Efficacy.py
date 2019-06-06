# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Honeybee.
#
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
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
ghenv.Component.NickName = 'lumEff'
ghenv.Component.Message = 'VER 0.0.04\nJUN_05_2019'
ghenv.Component.Category = "DragonflyPlus"
ghenv.Component.SubCategory = '03 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

from ladybug.wea import Wea

if _wea is not None and isinstance(_wea, Wea) and _dew_point is not None:
    glob_ill, dir_ill, diff_ill, zen_lum = \
        _wea.estimate_illuminance_components(_dew_point)