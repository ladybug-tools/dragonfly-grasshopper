# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a HorizontalPipeParameter object that can be used to customize the properties
of horizontal pipes contained within ThermalConnectors.
_
The output of this component can be used with the "DF GHE Thermal Loop" component.
-

    Args:
        _buried_depth_: The buried depth of the pipes in Rhino model units (eg. Meters,
            Feet, etc.). (Default: 1.5 meters).
        _diameter_ratio_: A number for the ratio of pipe outer diameter to pipe
            wall thickness. (Default: 11).
        _pressure_drop_: A number for the pressure drop in pascals per meter of pipe. (Default: 300).
        _insulation_conduct_: A positive number for the conductivity of the pipe insulation
            material in W/m-K. If no insulation exists, this value should be a
            virtual insulation layer of soil since this value must be greater
            than zero. (Default: 3.0).
        _insulation_thick_: A positive number for the thickness of pipe insulation in
            Rhino model units (eg. Meters, Feet, etc.). If no insulation exists,
            this value should be a virtual insulation layer of soil since this
            value must be greater than zero. (Default: 0.2 meters).

    Returns:
        horiz_pipe: A HorizontalPipeParameter object that can be plugged into the "DF GHE 
            Thermal Loop" component to customize the properties of horizonal pipes
            in a District Energy System (DES) simulation.
"""

ghenv.Component.Name = 'DF Horizontal Pipe Parameter'
ghenv.Component.NickName = 'HorizPipe'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from dragonfly_energy.des.connector import HorizontalPipeParameter
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))
try:
    from ladybug_rhino.config import conversion_to_meters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
try:
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


buried_depth = _buried_depth_ * conversion_to_meters() \
    if _buried_depth_ is not None else 1.5
insulation_thickness = _insulation_thick_ * conversion_to_meters() \
    if _insulation_thick_ is not None else 0.2
diameter_ratio = _diameter_ratio_ if _diameter_ratio_ is not None else 11
pressure_drop_per_meter = _pressure_drop_ if _pressure_drop_ is not None else 300
insulation_conductivity = _insulation_conduct_ if _insulation_conduct_ is not None else 3.0


horiz_pipe = HorizontalPipeParameter(
    buried_depth=buried_depth, diameter_ratio=diameter_ratio,
    pressure_drop_per_meter=pressure_drop_per_meter,
    insulation_conductivity=insulation_conductivity,
    insulation_thickness=insulation_thickness)
