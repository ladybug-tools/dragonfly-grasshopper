# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Construct a WEA from hourly data collections and the Zhang-Huang Solar Model.
-

    Args:
        _location = A Ladybug Location object.
        _cloud_cover: Hourly DataCollection with the fraction of total sky cover
            (tenths of coverage). (i.e. 1 is 1/10 covered. 10 is total coverage)
        _relative_humidity: Hourly DataCollection with relative humidity [%].
        _dry_bulb_temp: Hourly DataCollection with dry bulb temperature [C].
        _wind_speed: Hourly DataCollection with wind speed [m/s].
        _atmos_pressure_: Hourly DataCollection with amtospheric pressure [Pa].
            If no value is connected here, pressure at sea level will be
            assumed (101,325 Pa).
        
    Returns:
        wea: A wea object from the input data collections and the Zhang-Huang
            solar model.
"""

ghenv.Component.Name = "DF Wea from Zhang-Huang"
ghenv.Component.NickName = 'Zhang-Huang'
ghenv.Component.Message = '0.1.2'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:
    from ladybug.wea import Wea
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.header import Header
    from ladybug.datatype.pressure import AtmosphericStationPressure
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # perform checks.
    assert isinstance(_cloud_cover, HourlyContinuousCollection), \
        'Data Collections must be Continuous Hourly.'
    if _atmos_pressure_ is None:
        header = Header(AtmosphericStationPressure(), 'Pa',
            _cloud_cover.header.analysis_period, _cloud_cover.header.metadata)
        _atmos_pressure_ = HourlyContinuousCollection(header,
            [101325] * 8760 * _cloud_cover.header.analysis_period.timestep)
    assert HourlyContinuousCollection.are_collections_aligned(
        [_cloud_cover, _relative_humidity, _dry_bulb_temp, _wind_speed]), \
        'Data Collections must be aligned.'
    
    # build the Wea.
    wea = Wea.from_zhang_huang_solar(_location, _cloud_cover, _relative_humidity,
        _dry_bulb_temp, _wind_speed, _atmos_pressure_)