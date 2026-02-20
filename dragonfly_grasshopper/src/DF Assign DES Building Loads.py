# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Assign cooling, heating and hot water loads to a Dragonfly Building to be used
within a District Energy System (DES) simulation.
_
This component is intended specifically for the case that District Energy System
(DES) simulation is to be performed without using URBANopt to generate building
energy loads through EnergyPlus.
-

    Args:
        _building: A Dragonfly Building, Story or Room2D which is to have its energy
            properties re-assigned. This can also be an entire Dragonfly Model.
        _cooling_: An annual hourly data collection for building cooling loads
            for simulation with a DES. Note that this data collection must have
            a data type of Power.
        _heating_: An annual hourly data collection for building heating loads
            for simulation with a DES. Note that this data collection must have
            a data type of Power.
        _hot_water_: An annual hourly data collection for building service hot water loads
            for simulation with a DES. Note that this data collection must have
            a data type of Power.

    Returns:
        building: The input Dragonfly Building with DES loads assigned to it. The Model
            created with this Building can be converted directly into a format
            that works with DES simulation using the "DF Model to DES"
            component without the need to run EnergyPlus simulations with
            the "DF Run URBANopt" component.
"""

ghenv.Component.Name = 'DF Assign DES Building Loads'
ghenv.Component.NickName = 'AssignBldgLoad'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import ladybug-rhino
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    assert isinstance(_building, Building), 'Expected Dragonfly Building. ' \
        'Got {}.'.format(type(_building))
    building = _building.duplicate()
    building.properties.energy.des_cooling_load = _cooling_
    building.properties.energy.des_heating_load = _heating_
    building.properties.energy.des_hot_water_load = _hot_water_
