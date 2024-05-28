# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a BoreholeParameter object that can be used to customize the geometric
constraints governing the boreholes of a GHE sizing simulation.
_
The output of this component can be used with either the "DF GHE Designer"
component or the "DF GHE Thermal Loop" component.
-

    Args:
        _min_spacing_: A number in Rhino model units (eg. Meters, Feet, etc.) for the minimum
            spacing between boreholes. When the system demand cannot be met 
            using boreholes with the maximum spacing, the borehole spacing
            will be reduced until either the loads or met or they reach
            this minimum spacing. So this typically represents the spacing
            at which each borehole will interfere with neighboring ones so much
            that it is not worthwhile to decrease the spacing further. (Default: 3 meters).
        _max_spacing_: A number in Rhino model units (eg. Meters, Feet, etc.) for the maximum
            spacing between boreholes in meters. This will set the starting
            value for the spacing (Default: 25 meters).
        _min_depth_: A number in Rhino model units (eg. Meters, Feet, etc.) for the
            minimum depth of the heat-exchanging part of the boreholes in meters.
            This will set the starting value for the depth (Default: 60 meters).
        _max_depth_: A number in Rhino model units (eg. Meters, Feet, etc.) for the
            maximum depth of the heat-exchanging part of the boreholes in meters.
            When the system demand cannot be met using boreholes with the
            minimum depth, the boreholes will be extended until either the
            loads or met or they reach the maximum depth specified here. So this
            typically represents the depth of bedrock or the point at which drilling
            deeper ceases to be practical. (Default: 135 meters).
        _buried_depth_: A number in Rhino model units (eg. Meters, Feet, etc.) for the
            depth below the ground surface at which the top of the heat exchanging
            part of the borehole sits in meters. (Default: 2 meters).
        _diameter_: A number for the diameter of the borehole in meters. (Default: 0.15 meters).

    Returns:
        borehole: A BoreholeParameter object that can be plugged into the
            "DF GHE Designer" component in order to customize the properties
            of borehole min/max depth and borehole min/max spacing. It can
            also be plugged into the "DF GHE Thermal Loop" component to
            perform a similar role in a District Energy Simulation (DES)
            of a loop with a ground heat exchanger.
"""

ghenv.Component.Name = 'DF GHE Borehole Parameter'
ghenv.Component.NickName = 'GHEBorehole'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from dragonfly_energy.des.ghe import BoreholeParameter
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


min_depth = _min_depth_ * conversion_to_meters() if _min_depth_ is not None else 60
max_depth = _max_depth_ * conversion_to_meters() if _max_depth_ is not None else 135
min_spacing = _min_spacing_ * conversion_to_meters() if _min_spacing_ is not None else 3
max_spacing = _max_spacing_ * conversion_to_meters() if _max_spacing_ is not None else 25
buried_depth = _buried_depth_ * conversion_to_meters() if _buried_depth_ is not None else 2
diameter = _diameter_ * conversion_to_meters() if _diameter_ is not None else 0.15


borehole = BoreholeParameter(min_depth, max_depth, min_spacing, max_spacing,
                             buried_depth, diameter)
