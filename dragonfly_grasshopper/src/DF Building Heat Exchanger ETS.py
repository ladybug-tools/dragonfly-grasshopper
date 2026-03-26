# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Assign an Energy Transfer Station (ETS) with a heat exchanger to a dragonfly Building
to be used within a District Energy System (DES) simulation.
_
This type of ETS is used for fourth generation district energy systems and is
specifically intended to be used in conjunction with the "DF Fourth Generation
Thermal Loop" component.
-

    Args:
        _building: A Dragonfly Building to which a heat exchanger Energy Transfer
            Station (ETS) will be asigned.
        _cooling_temp_: A number for the building's chilled water supply
            temperature in Celsius. (Default: 7C).
        _heating_temp_: A number for the building's heating water supply
            temperature in Celsius. (Default: 50C).
        _exchanger_efficiency_: A number between 0 and 1 for the heat exchanger
            efficiency. (Default: 0.8).
        _primary_press_drop_: A number for the heat exchanger primary side
            pressure drop in pascals. (Default: 500).
        _secondary_press_drop_: A number for the heat exchanger secondary side
            pressure drop in pascals. (Default: 500).

    Returns:
        building: The input Dragonfly Building with a heat exchanger Energy Transfer
            Station (ETS) assigned to it. The ETS parameters specified here
            will be assigned whenever the Building is used with the "DF Fourth
            Generation Thermal Loopp" component.
"""

ghenv.Component.Name = 'DF Building Heat Exchanger ETS'
ghenv.Component.NickName = 'HeatExchangerETS'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the dragonfly-energy dependencies
    from dragonfly_energy.des.ets import HeatExchangerETS
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
    cooling_supply_temp = 7 if _cooling_temp_ is None else _cooling_temp_
    heating_supply_temp = 50 if _heating_temp_ is None else _heating_temp_
    efficiency = 0.8 if _exchanger_efficiency_ is None else _exchanger_efficiency_
    ppd = 500 if _primary_press_drop_ is None else _primary_press_drop_
    spd = 500 if _secondary_press_drop_ is None else _secondary_press_drop_

    # create the HeatExchangerETS and assign it to the building
    ets = HeatExchangerETS(
        cooling_supply_temp=cooling_supply_temp,
        heating_supply_temp=heating_supply_temp,
        exchanger_efficiency=efficiency,
        primary_pressure_drop=ppd,
        secondary_pressure_drop=spd
    )
    building.properties.energy.heat_exchanger_ets = ets
