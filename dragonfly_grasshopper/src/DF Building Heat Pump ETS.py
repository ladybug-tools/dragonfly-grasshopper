# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Assign an Energy Transfer Station (ETS) with a heat pump to a dragonfly Building
to be used within a District Energy System (DES) simulation.
_
This type of ETS is used for fifth generation district energy systems, including
both the "DF Fifth Generation Thermal Loop" and the "DF GHE Thermal Loop".
-

    Args:
        _building: A Dragonfly Building to which a heat pump Energy Transfer
            Station (ETS) will be asigned.
        _cooling_temp_: A number for the building's chilled water supply
            temperature in Celsius. (Default: 5C).
        _heating_temp_: A number for the building's heating water supply
            temperature in Celsius. (Default: 50C).
        _shw_temp_: A number for the building's service hot water supply
            temperature in Celsius. (Default: 50C).
        _cop_cooling_: A number for the coefficient of performance (COP) of the
            heat pump producing chilled water. (Default: 3.5).
        _cop_heating_: A number for the coefficient of performance (COP) of the
            heat pump producing hot water for space heating. (Default: 2.5).
        _cop_shw_: A number for the coefficient of performance (COP) of the
            heat pump producing service hot water. (Default: 2.5).
        _pump_head_: A number for the design head pressure of the ETS pump
            in pascals. (Default: 10000).

    Returns:
        building: The input Dragonfly Building with a heat pump Energy Transfer
            Station (ETS) assigned to it. The ETS parameters specified here
            will be assigned whenever the Building is used with the "DF Fifth
            Generation Thermal Loop" or the "DF GHE Thermal Loop."
"""

ghenv.Component.Name = 'DF Building Heat Pump ETS'
ghenv.Component.NickName = 'HeatPumpETS'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the dragonfly-energy dependencies
    from dragonfly_energy.des.ets import HeatPumpETS
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:  # import ladybug-rhino
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check the inputs
    assert isinstance(_building, Building), 'Expected Dragonfly Building. ' \
        'Got {}.'.format(type(_building))
    building = _building.duplicate()
    cooling_supply_temp = 5 if _cooling_temp_ is None else _cooling_temp_
    heating_supply_temp = 50 if _heating_temp_ is None else _heating_temp_
    shw_supply_temp = 50 if _shw_temp_ is None else _shw_temp_
    cop_cooling = 3.5 if _cop_cooling_ is None else _cop_cooling_
    cop_heating = 2.5 if _cop_heating_ is None else _cop_heating_
    cop_shw = 2.5 if _cop_shw_ is None else _cop_shw_
    pump_head = 10000 if _pump_head_ is None else _pump_head_

    # create the HeatPumpETS and assign it to the building
    ets = HeatPumpETS(
        cooling_supply_temp=cooling_supply_temp,
        heating_supply_temp=heating_supply_temp,
        shw_supply_temp=shw_supply_temp,
        cop_cooling=cop_cooling,
        cop_heating=cop_heating,
        cop_shw=cop_shw,
        pump_head=pump_head
    )
    building.properties.energy.heat_pump_ets = ets
