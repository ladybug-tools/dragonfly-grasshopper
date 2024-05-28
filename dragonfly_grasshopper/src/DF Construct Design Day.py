# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Construct a design day from a set of parameters.

-

    Args:
        _name: The name of the DesignDay object.
        _day_type: Text indicating the type of design day (ie. 'SummerDesignDay',
            'WinterDesignDay' or other EnergyPlus days).
        _location: A Ladybug Location object describing the location of the design day.
        _date: A Ladybug Date for the day of the year on which the design day occurs.
            This should be in the format of 'DD Month' (eg. '1 Jan', '4 Jul').
            The LB Calculate HOY component can also be used to construct this date.
        _dry_bulb_max: Maximum dry bulb temperature over the design day (in C).
        _dry_bulb_range_: Dry bulb range over the design day (in C).
        _humidity_type: Type of humidity to use. (ie. Wetbulb, Dewpoint, HumidityRatio, Enthalpy)
        _humidity_value: The value of the humidity condition above.
        _barometric_p_: Barometric pressure in Pa.
        _wind_speed: Wind speed over the design day in m/s.
        _wind_dir: Wind direction over the design day in degrees.
        _sky_type: Type of solar model to use.  (eg. ASHRAEClearSky, ASHRAETau)
        _sky_properties: A list of properties describing the sky above.
            For ASHRAEClearSky this is a single value for clearness.
            For ASHRAETau, this is the tau_beam and tau_diffuse.

    Returns:
        _design_days: A DesignDay object to deconstruct.
"""

ghenv.Component.Name = 'DF Construct Design Day'
ghenv.Component.NickName = 'ConstrDesignDay'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '6 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = '3'


try:
    from ladybug.designday import DesignDay
    from ladybug.dt import Date, DateTime
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set defaults for relevant items
    if _dry_bulb_range_ is None:
        _dry_bulb_range_ = 0
    if _barometric_p_ is None:
        _barometric_p_ = 101325
    
    # process the input date
    try:
        date = Date.from_date_string(_date)
    except ValueError:
        date = DateTime.from_date_time_string(_date).date
    
    design_day = DesignDay.from_design_day_properties(
        _name, _day_type, _location, date, _dry_bulb_max, _dry_bulb_range_,
        _humidity_type, _humidity_value, _barometric_p_, _wind_speed, _wind_dir,
        _sky_type, _sky_properties)