# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

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
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

try:
    from ladybug.wea import Wea
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    glob_ill, dir_ill, diff_ill, zen_lum = \
        _wea.estimate_illuminance_components(_dew_point)