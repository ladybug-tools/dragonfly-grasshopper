# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a CoolingPlant object that can be used in a District Energy System (DES).
_
The output of this component can be used with the "DF Fourth Generation
Thermal Loop" component.
-

    Args:
        _chw_setpoint_: A number for the temperature of chilled water in the DES in degrees C. (Default: 6).
        _cooling_limit_: A number for the nominal district cooling load in Watts. (Default: 8000).
        _chw_mass_flow_: A number for the nominal chilled water mass flow rate in kg/s. (Default: 10.0).
        _min_chw_mass_flow_: A number for the minimum chilled water mass flow rate in kg/s. (Default: 10.0).
        _cw_mass_flow_: A number for the nominal condenser water mass flow rate in kg/s. (Default: 1.0).
        _chw_pump_head_: A number for the chilled water pump head in Pa. (Default: 300000).
        _cw_pump_head_: A number for the condenser water pump head in Pa. (Default: 200000).
        _chw_press_drop_: A number for the nominal chilled water (evaporator) side pressure drop in Pa. (Default: 55000).
        _cw_press_drop_: A number for the nominal cooling water (condenser) side pressure drop in Pa. (Default: 80000).
        _press_drop_setpoint_: A number for the chilled water circuit pressure drop setpoint in Pa. (Default: 50000).
        _chw_vpress_drop_: A number for the chiller isolation valve pressure drop in Pa. (Default: 6000).
        _cw_vpress_drop_: A number for the cooling tower isolation valve pressure drop in Pa. (Default: 6000).
        _tower_fan_power_: A number for the cooling tower fan power in Watts. (Default: 5000).
        _tower_delta_temp_: A number for the nominal water temperature difference of the tower in degrees C. (Default: 7).
        _approach_delta_temp_: A number for the approach temperature difference in degrees C. (Default: 3).
        _cw_inlet_temp_: A number for the nominal cooling water inlet temperature in degrees C. (Default: 35).
        _outdoor_wb_temp_: A number for the design air wet-bulb temperature in degrees C. (Default: 25).

    Returns:
        borehole: A CoolingPlant object that can be plugged into the "DF Fourth
            Generation Thermal Loop" component to customize the cooling plant
            in the District Energy Simulation (DES).
"""

ghenv.Component.Name = 'DF Cooling Plant'
ghenv.Component.NickName = 'CoolingPlant'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from dragonfly_energy.des.plant import CoolingPlant
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))
try:
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


_chw_setpoint_ = _chw_setpoint_ if _chw_setpoint_ is not None else 6
_cooling_limit_ = _cooling_limit_ if _cooling_limit_ is not None else 8000
_chw_mass_flow_ = _chw_mass_flow_ if _chw_mass_flow_ is not None else 10
_min_chw_mass_flow_ = _min_chw_mass_flow_ if _min_chw_mass_flow_ is not None else 10
_cw_mass_flow_ = _cw_mass_flow_ if _cw_mass_flow_ is not None else 10
_chw_pump_head_ = _chw_pump_head_ if _chw_pump_head_ is not None else 300000
_cw_pump_head_ = _cw_pump_head_ if _cw_pump_head_ is not None else 200000
_chw_press_drop_ = _chw_press_drop_ if _chw_press_drop_ is not None else 55000
_cw_press_drop_ = _cw_press_drop_ if _cw_press_drop_ is not None else 80000
_press_drop_setpoint_ = _press_drop_setpoint_ if _press_drop_setpoint_ is not None else 50000
_chw_vpress_drop_ = _chw_vpress_drop_ if _chw_vpress_drop_ is not None else 6000
_cw_vpress_drop_ = _cw_vpress_drop_ if _cw_vpress_drop_ is not None else 6000
_tower_fan_power_ = _tower_fan_power_ if _tower_fan_power_ is not None else 5000
_tower_delta_temp_ = _tower_delta_temp_ if _tower_delta_temp_ is not None else 7
_approach_delta_temp_ = _approach_delta_temp_ if _approach_delta_temp_ is not None else 3
_cw_inlet_temp_ = _cw_inlet_temp_ if _cw_inlet_temp_ is not None else 35
_outdoor_wb_temp_ = _outdoor_wb_temp_ if _outdoor_wb_temp_ is not None else 25


cooling = CoolingPlant(
    chw_setpoint=_chw_setpoint_,
    cooling_limit=_cooling_limit_,
    chw_mass_flow=_chw_mass_flow_,
    min_chw_mass_flow=_min_chw_mass_flow_,
    cw_mass_flow=_cw_mass_flow_,
    chw_pump_head=_chw_pump_head_,
    cw_pump_head=_cw_pump_head_,
    chw_pressure_drop=_chw_press_drop_,
    cw_pressure_drop=_cw_press_drop_,
    pressure_drop_setpoint=_press_drop_setpoint_,
    chw_valve_pressure_drop=_chw_vpress_drop_,
    cw_valve_pressure_drop=_cw_vpress_drop_,
    cooling_tower_fan_power=_tower_fan_power_,
    cooling_tower_delta_temperature=_tower_delta_temp_,
    approach_delta_temperature=_approach_delta_temp_,
    cw_inlet_temperature=_cw_inlet_temp_,
    outdoor_wb_temperature=_outdoor_wb_temp_
)
