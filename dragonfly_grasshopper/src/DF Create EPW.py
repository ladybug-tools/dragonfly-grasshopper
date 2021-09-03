# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a custom EPW object from a location and data collections of annual
hourly data.
-

    Args:
        _location: A location object for the epw_file.
        _dry_bulb_temp_: Annual hourly data collection for dry bulb temperature [C]
        _dew_point_temp_: Annual hourly data collection for dew point temperature [C]
        _wind_speed_: Annual hourly data collection for wind speed [m/s]
        _wind_direction_: Annual hourly data collection for wind direction [degrees]
        _direct_normal_rad_: Annual hourly data collection for direct normal
            radiation [Wh/m2] or [W/m2]
        _diffuse_horiz_rad_: Annual hourly data collection for diffuse horizontal
            radiation [Wh/m2] or [W/m2]
        _horiz_infrared_rad_: Annual hourly data collection for horizontal
            infrared radiation intensity [Wh/m2] or [W/m2]
        _direct_normal_ill_: Annual hourly data collection for direct normal
            illuminance [lux]
        _diffuse_horiz_ill_: Annual hourly data collection for diffuse
            horizontal illuminance [lux]
        _total_sky_cover_: Annual hourly data collection for the fraction for
            total sky cover [tenths]
        _atmos_pressure_: Annual hourly data collection for weather station
            pressure [Pa]
        _visibility_: Annual hourly data collection for visibility [km]
        _ceiling_height_: Annual hourly data collection for cloud ceiling height [m]
        _model_year_: Annual hourly data collection for the year from which the
            hourly data has been extracted. This input is necessary when the
            input data collections are from a leap year.
        base_epw_: File path to an optional .epw to fill empty slots for data
            that has not been connected here.
        _run: Set to True to run the component and create the epw_obj.

    Returns:
        report: Reports, errors, warnings, etc.
        epw_obj: An EPW object that can be written to a file using the Write EPW
            component.
"""

ghenv.Component.Name = 'DF Create EPW'
ghenv.Component.NickName = 'CreateEPW'
ghenv.Component.Message = '1.3.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import math

try:
    from ladybug.epw import EPW
    from ladybug.wea import Wea
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.sunpath import Sunpath
    from ladybug.datatype.temperature import Temperature
    from ladybug.datatype.fraction import Fraction, RelativeHumidity
    from ladybug.datatype.speed import Speed
    from ladybug.datatype.angle import Angle
    from ladybug.datatype.energyflux import EnergyFlux
    from ladybug.datatype.illuminance import Illuminance
    from ladybug.datatype.pressure import Pressure
    from ladybug.datatype.distance import Distance
    from ladybug.psychrometrics import rel_humid_from_db_dpt
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def check_data(name, data_coll, data_type, unit, is_leap_year):
    assert isinstance(data_coll, HourlyContinuousCollection), \
        '{} must be an hourly continuous data collection. Got {}.'.format(
            name, type(data_coll))
    assert data_coll.header.analysis_period.is_annual, '{} analysis_period must ' \
        'be annual. Got {}'.format(header.analysis_period)
    assert data_coll.header.analysis_period.is_leap_year == is_leap_year, \
        '{} analysis_period must is_leap_year must match across input data collections.'
    assert isinstance(data_coll.header.data_type, data_type), '{} data_type is not {}. '\
        'Got {}.'.format(name, data_type(), data_coll.header.data_type)
    assert data_coll.header.unit == unit, '{} unit is not {}. '\
        'Got {}.'.format(name, unit, data_coll.header.unit)
    return data_coll.values


if all_required_inputs(ghenv.Component) and _run:
    # initialize the EPW
    if base_epw_ is not None:
        epw_obj = EPW(base_epw_)
        leap_yr = epw_obj.is_leap_year
    else:
        if _model_year_:
            leap_yr = _model_year_.header.analysis_period.is_leap_year
        else:
            leap_yr = False
        epw_obj = EPW.from_missing_values(is_leap_year=leap_yr)
    
    # assign data to the EPW
    epw_obj.location = _location
    if _dry_bulb_temp_:
        epw_obj.dry_bulb_temperature.values = check_data(
            '_dry_bulb_temp_', _dry_bulb_temp_, Temperature, 'C', leap_yr)
    if _dew_point_temp_:
        epw_obj.dew_point_temperature.values = check_data(
            '_dew_point_temp_', _dew_point_temp_, Temperature, 'C', leap_yr)
    if _wind_speed_:
        epw_obj.wind_speed.values = check_data(
            '_wind_speed_', _wind_speed_, Speed, 'm/s', leap_yr)
    if _wind_direction_:
        epw_obj.wind_direction.values = check_data(
            '_wind_direction_', _wind_direction_, Angle, 'degrees', leap_yr)
    if _direct_normal_rad_:
        epw_obj.direct_normal_radiation.values = _direct_normal_rad_.values
    if _diffuse_horiz_rad_:
        epw_obj.diffuse_horizontal_radiation.values = _diffuse_horiz_rad_.values
    if _horiz_infrared_rad_:
        epw_obj.horizontal_infrared_radiation_intensity.values = check_data(
            '_horiz_infrared_rad_', _horiz_infrared_rad_, EnergyFlux, 'W/m2', leap_yr)
    if _direct_normal_ill_:
        epw_obj.direct_normal_illuminance.values = check_data(
            '_direct_normal_ill_', _direct_normal_ill_, Illuminance, 'lux', leap_yr)
    if _diffuse_horiz_ill_:
        epw_obj.diffuse_horizontal_illuminance.values = check_data(
            '_diffuse_horiz_ill_', _diffuse_horiz_ill_, Illuminance, 'lux', leap_yr)
    if _total_sky_cover_:
        epw_obj.total_sky_cover.values = check_data(
            '_total_sky_cover_', _total_sky_cover_, Fraction, 'tenths', leap_yr)
        epw_obj.opaque_sky_cover.values = _total_sky_cover_.values
    if _atmos_pressure_:
        epw_obj.atmospheric_station_pressure.values = check_data(
            '_atmos_pressure_', _atmos_pressure_, Pressure, 'Pa', leap_yr)
    if _visibility_:
        epw_obj.visibility.values = check_data(
            '_visibility_', _visibility_, Distance, 'km', leap_yr)
    if _ceiling_height_:
        epw_obj.ceiling_height.values = check_data(
            '_ceiling_height_', _ceiling_height_, Distance, 'm', leap_yr)
    if _model_year_:
        epw_obj.years.values = _model_year_.values
    
    # calculate properties that are derived from other inputs
    if _dry_bulb_temp_ and _dew_point_temp_:
        rel_humid = HourlyContinuousCollection.compute_function_aligned(
            rel_humid_from_db_dpt, [_dry_bulb_temp_, _dew_point_temp_],
            RelativeHumidity(), '%')
        epw_obj.relative_humidity.values = rel_humid.values
    if _direct_normal_rad_ and _diffuse_horiz_rad_:
        wea = Wea(_location, _direct_normal_rad_, _diffuse_horiz_rad_)
        epw_obj.global_horizontal_radiation.values = wea.global_horizontal_irradiance.values
    if _direct_normal_ill_ and _diffuse_horiz_ill_:
        glob_horiz = []
        sp = Sunpath.from_location(_location)
        sp.is_leap_year = leap_yr
        for dt, dni, dhi in zip(_direct_normal_ill_.datetimes,
                _direct_normal_ill_, _diffuse_horiz_ill_):
            sun = sp.calculate_sun_from_date_time(dt)
            glob_horiz.append(dhi + dni * math.sin(math.radians(sun.altitude)))
        epw_obj.global_horizontal_radiation.values = glob_horiz
