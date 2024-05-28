# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a PipeParameter object that can be used to customize the pipe properties
within a Ground Heat Exchanger (GHE) sizing simulation.
_
The output of this component can be used with either the "DF GHE Designer"
component or the "DF GHE Thermal Loop" component.
-

    Args:
        _inner_diameter_: A number in Rhino model units (eg. Meters, Feet, etc.) for the
            diameter of the inner pipe surface in meters. (Default: 0.0216 meters).
        _outer_diameter_: A number in Rhino model units (eg. Meters, Feet, etc.) for the
            diameter of the outer pipe surface in meters. (Default: 0.0266 meters).
        _shank_spacing_: A number in Rhino model units (eg. Meters, Feet, etc.) for the
            spacing between the U-tube legs, as referenced from outer surface of
            the pipes in meters. (NOT referenced from each pipe's respective
            centerline). (Default: 0.0323 meters).
        _conductivity_: A number for the conductivity of the pipe material in W/m-K. (Default: 0.4).
        _heat_capacity_: A number for the volumetric heat capacity of the pipe
            material in J/m3-K. (Default: 1,542,000).
        _arrangement_: Text for the specified pipe arrangement. Choose from the
            following options. (Default: SingleUTube).
            _
                * SingleUTube
                * DoubleUTubeSeries
                * DoubleUTubeParallel

    Returns:
        soil: A PipeParameter object that can be plugged into the "DF GHE Designer"
            component in order to customize pipe properties of a GHE sizing
            simulation. It can also be plugged into the "DF GHE Thermal Loop"
            component to perform a similar role in a District Energy Simulation
            (DES) of a loop with a ground heat exchanger.
"""

ghenv.Component.Name = 'DF GHE Pipe Parameter'
ghenv.Component.NickName = 'GHEPipe'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from dragonfly_energy.des.ghe import PipeParameter
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


inner_diameter = _inner_diameter_ * conversion_to_meters() \
    if _inner_diameter_ is not None else 0.0216
outer_diameter = _outer_diameter_ * conversion_to_meters() \
    if _outer_diameter_ is not None else 0.0266
shank_spacing = _shank_spacing_ * conversion_to_meters() \
    if _shank_spacing_ is not None else 0.0323
conductivity = _conductivity_ if _conductivity_ is not None else 0.4
heat_capacity = _heat_capacity_ if _heat_capacity_ is not None else 1542000
arrangement = _arrangement_ if _arrangement_ is not None else 'SingleUTube'


pipe = PipeParameter(
    inner_diameter=inner_diameter, outer_diameter=outer_diameter, shank_spacing=shank_spacing,
    conductivity=conductivity, heat_capacity=heat_capacity, arrangement=arrangement)
