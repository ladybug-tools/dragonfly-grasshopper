# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a FluidParameter object that can be used to customize the fluid properties
within a Ground Heat Exchanger (GHE) sizing simulation.
_
The output of this component can be used with either the "DF GHE Designer"
component or the "DF GHE Thermal Loop" component.
-

    Args:
        _type_: Text to indicate the type of fluid circulating through a ground heat
            exchanger loop. Many ground heat exchangers use only water but
            other options may be used to prevent freezing in conditions
            where the ground is particularly cold. Choose from the options
            below. (Default: Water).
            _
                * Water
                * EthylAlcohol
                * EthyleneGlycol
                * MethylAlcohol
                * PropyleneGlycol
        _concentration_: A number between 0 and 60 for the concentration of the
            fluid_type in water in percent. Note that this variable has no effect
            when the fluid_type is Water. (Default: 35%).
        _temperature_: A number for the average design fluid temperature at peak
            conditions in Celsius. (Default: 20C).

    Returns:
        fluid: A FluidParameter object that can be plugged into the "DF GHE Designer"
            component in order to customize fluid properties of a GHE sizing
            simulation. It can also be plugged into the "DF GHE Thermal Loop"
            component to perform a similar role in a District Energy Simulation
            (DES) of a loop with a ground heat exchanger.
"""

ghenv.Component.Name = 'DF GHE Fluid Parameter'
ghenv.Component.NickName = 'GHEFluid'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from dragonfly_energy.des.ghe import FluidParameter
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))


fluid_type = _type_ if _type_ is not None else 'Water'
concentration = _concentration_ if _concentration_ is not None else 35
temperature = _temperature_ if _temperature_ is not None else 20


fluid = FluidParameter(fluid_type, concentration, temperature)
