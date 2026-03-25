# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a HeatingPlant object that can be used in a District Energy System (DES).
_
The output of this component can be used with the "DF Fourth Generation
Thermal Loop" component.
-

    Args:
        _hw_setpoint_: A number for the temperature of hot water in the DES in degrees C. (Default: 55).
        _heating_limit_: A number for the nominal district heating load in Watts. (Default: 5000).
        _hw_mass_flow_: A number for the nominal heating water mass flow rate in kg/s. (Default: 1.0).

    Returns:
        heating: A HeatingPlant object that can be plugged into the "DF Fourth
            Generation Thermal Loop" component to customize the heating plant
            in the District Energy Simulation (DES).
"""

ghenv.Component.Name = 'DF Heating Plant'
ghenv.Component.NickName = 'HeatingPlant'
ghenv.Component.Message = '1.10.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from dragonfly_energy.des.plant import HeatingPlant
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))
try:
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


_hw_setpoint_ = _hw_setpoint_ if _hw_setpoint_ is not None else 55
_heating_limit_ = _heating_limit_ if _heating_limit_ is not None else 5000
_hw_mass_flow_ = _hw_mass_flow_ if _hw_mass_flow_ is not None else 1.0

heating = HeatingPlant(
    hw_setpoint=_hw_setpoint_,
    heating_limit=_heating_limit_,
    hw_mass_flow=_hw_mass_flow_
)
