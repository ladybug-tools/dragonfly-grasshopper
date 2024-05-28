# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a SoilParameter object that can be used to customize the soil and grout
properties within a Ground Heat Exchanger (GHE) sizing simulation.
_
The output of this component can be used with either the "DF GHE Designer"
component or the "DF GHE Thermal Loop" component.
-

    Args:
        _conductivity_: A number for the soil conductivity in W/m-K. (Default: 2.3).
        _heat_capacity_: A number for the volumetric heat capacity of the soil
            in J/m3-K. (Default: 2,343,500).
        _temperature_: A number for the undisturbed annual average soil temperature in
            degrees Celsius. If unspecified, this value will automatically be
            replaced with the average EPW temperature before simulation of a
            District Energy System (DES). Alternatively, if this component
            is used with the "DF GHE Designer" component, it will be 18.3C.
        _grout_conduct_: A number for the grout conductivity in W/m-K. (Default: 1.0).
        _grout_capacity_: A number for the volumetric heat capacity of the soil
            in J/m3-K. (Default: 3,901,000).

    Returns:
        soil: A SoilParameter object that can be plugged into the "DF GHE Designer"
            component in order to customize soil properties of a GHE sizing
            simulation. It can also be plugged into the "DF GHE Thermal Loop"
            component to perform a similar role in a District Energy Simulation
            (DES) of a loop with a ground heat exchanger.
"""

ghenv.Component.Name = 'DF GHE Soil Parameter'
ghenv.Component.NickName = 'GHESoil'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from honeybee.altnumber import autocalculate
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from dragonfly_energy.des.ghe import SoilParameter
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))


conductivity = _conductivity_ if _conductivity_ is not None else 2.3
heat_capacity = _heat_capacity_ if _heat_capacity_ is not None else 2343500
undisturbed_temp = _temperature_ if _temperature_ is not None else autocalculate
grout_conduct = _grout_conduct_ if _grout_conduct_ is not None else 1.0
grout_heat_capacity = _grout_capacity_ if _grout_capacity_ is not None else 3901000


soil = SoilParameter(conductivity, heat_capacity, undisturbed_temp,
                     grout_conduct, grout_heat_capacity)
