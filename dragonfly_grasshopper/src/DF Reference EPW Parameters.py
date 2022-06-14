# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create Reference EPW Site parameters that represent the properties of the stie
where rural EPW data was recorded for an Urban Weather Genrator (UWG) simulation.
-

    Args:
        _obstacle_hght_: A number that represents the height in meters of objects that
            obstruct the view to the sky at the weather station site. This
            includes both trees and buildings. (Default: 0.1 m).
        _veg_cover_: A number between 0 and 1 that represents the fraction of the 
            reference EPW site that is covered in grass. (Default: 0.9).
        _temp_hght_: A number that represents the height in meters at which
            temperature is measured on the weather station. (Default: 10m, the
            standard measurement height for US DoE EPW files).
        _wind_hght_: A number that represents the height in meters at which
            wind speed is measured on the weather station. (Default: 10m, the
            standard measurement height for US DoE EPW files).

    Returns:
        epw_site: Reference EPW site parameters that can be plugged into the "DF UWG
            Simulation Parameter" component to specify the behavior of vegetation
            in the simulation.
"""

ghenv.Component.Name = "DF Reference EPW Parameters"
ghenv.Component.NickName = 'RefEPWPar'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the dragonfly_uwg dependencies
    from dragonfly_uwg.simulation.refsite import ReferenceEPWSite
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_uwg:\n\t{}'.format(e))


# process default values
_obstacle_hght_ = _obstacle_hght_ if _obstacle_hght_ is not None else 0.1
_veg_cover_ = _veg_cover_ if _veg_cover_ is not None else 0.9
_temp_hght_ = _temp_hght_ if _temp_hght_ is not None else 10
_wind_hght_ = _wind_hght_ if _wind_hght_ is not None else 10

# create the traffic parameters
epw_site = ReferenceEPWSite(
    _obstacle_hght_, _veg_cover_, _temp_hght_, _wind_hght_)
