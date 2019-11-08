# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Construct a design day from a set of parameters.

-

    Args:
        _name: The name of the DesignDay object.
        _day_type: Text indicating the type of design day (ie. 'SummerDesignDay',
            'WinterDesignDay' or other EnergyPlus days).
        _location: A Ladybug Location object describing the location of the design day.
        _analysis_period: Analysis period for the design day
        _dry_bulb_max: Maximum dry bulb temperature over the design day (in C).
        _dry_bulb_range_: Dry bulb range over the design day (in C).
        _humidity_type: Type of humidity to use. (ie. Wetbulb, Dewpoint, HumidityRatio, Enthalpy)
        _humidity_value: The value of the humidity condition above.
        _barometric_p_: Barometric pressure in Pa.
        _wind_speed: Wind speed over the design day in m/s.
        _wind_dir: Wind direction over the design day in degrees.
        _sky_model: Type of solar model to use.  (ie. ASHRAEClearSky, ASHRAETau)
        _sky_properties: A list of properties describing the sky above.
            For ASHRAEClearSky this is a single value for clearness.
            For ASHRAETau, this is the tau_beam and tau_diffuse.
        
    Returns:
        _design_days: A DesignDay object to deconstruct.
"""

ghenv.Component.Name = "DF Construct Design Day"
ghenv.Component.NickName = 'ConstrDesignDay'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '3 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = "2"


try:
    from ladybug.designday import DesignDay
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))


if _name is not None and _day_type is not None and _location is not None and \
    _analysis_period is not None and _dry_bulb_max is not None and \
    _humidity_type is not None and _humidity_value is not None and \
    _wind_speed is not None and _wind_dir is not None and _sky_type is not None \
    and _sky_properties is not None != []:
        if _dry_bulb_range_ is None:
            _dry_bulb_range_ = 0
        if _barometric_p_ is None:
            _barometric_p_ = 101325
        
        design_day = DesignDay.from_design_day_properties(_name, _day_type, _location,
                                    _analysis_period, _dry_bulb_max, _dry_bulb_range_,
                                    _humidity_type, _humidity_value, _barometric_p_,
                                    _wind_speed, _wind_dir, _sky_type, _sky_properties)