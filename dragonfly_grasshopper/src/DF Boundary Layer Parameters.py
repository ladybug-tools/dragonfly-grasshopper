# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create BoundaryLayerParameters representing the properties of the urban boundary
layer in an Urban Weather Genrator (UWG) simulation.
-

    Args:
        _day_hght_: A number that represents the height in meters of the urban boundary
            layer during the daytime. This is the height to which the urban
            meteorological conditions are stable and representative of the
            overall urban area. Typically, this boundary layer height increases
            with the height of the buildings. (Default: 1000 meters).
        _night_hght_: A number that represents the height in meters of the urban
            boundary layer during the nighttime. This is the height to which the
            urban meteorological conditions are stable and representative of
            the overall urban area. Typically, this boundary layer height
            increases with the height of the buildings. (Default: 80 meters).
        _inversion_hght_: A number that represents the height in meters at which
            the vertical profile of potential temperature becomes stable.
            Can be determined by flying helium balloons equipped
            with temperature sensors and recording the air temperatures
            at different heights. (Default: 150 meters).
        _circ_coeff_: A number representing the circulation coefficient. (Default: 1.2,
            per Bueno (2012)).
        _exch_coeff_: A number representing the exchange coefficient. (Default: 1.0,
            per Bueno (2014)).

    Returns:
        bnd_layer: Boundary layer parameters that can be plugged into the "DF UWG
            Simulation Parameter" component to specify the properties of the
            urban boundary layer.
"""

ghenv.Component.Name = "DF Boundary Layer Parameters"
ghenv.Component.NickName = 'BoundaryLayer'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the dragonfly_uwg dependencies
    from dragonfly_uwg.simulation.boundary import BoundaryLayerParameter
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_uwg:\n\t{}'.format(e))


# process default values
_day_hght_ = _day_hght_ if _day_hght_ is not None else 1000
_night_hght_ = _night_hght_ if _night_hght_ is not None else 80
_inversion_hght_ = _inversion_hght_ if _inversion_hght_ is not None else 150
_circ_coeff_ = _circ_coeff_ if _circ_coeff_ is not None else 1.2
_exch_coeff_ = _exch_coeff_ if _exch_coeff_ is not None else 1.0

# create the traffic parameters
bnd_layer = BoundaryLayerParameter(
    _day_hght_, _night_hght_, _inversion_hght_, _circ_coeff_, _exch_coeff_)
