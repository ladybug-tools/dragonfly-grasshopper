# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a Ground Heat Exchanger for a District Energy System (DES) from its
footprint geometry (horizontal Rhino surfaces).
-

    Args:
        _geo: A horizontal Rhino surface representing a footprint to be converted
            into a Ground Heat Exchanger.
        _name_: Text to set the name for the Ground Heat Exchanger, which will also
            be incorporated into unique Ground Heat Exchanger identifier.
            If the name is not provided, a random one will be assigned.
        _soil_conduct_: A number for the soil conductivity in W/m-K. (Default: 2.3).
        _soil_heat_cap_: A number for the volumetric heat capacity of the soil
            in J/m3-K. (Default: 2,343,500).
        _soil_temper_: A number the undisturbed annual average soil temperature in
            degrees Celsius. If unspecified, this value will be the average EPW
            temperature.
        _bore_length_: A number for the length of the borehole in meters. This is the
            distance from the bottom of the heat exchanging part of the borehole
            to the top. (Default: 96).
        _bore_depth_: A number for the depth below the ground surface at which
            the top of the heat exchanging part of the borehole sits in
            meters. (Default: 2).

    Returns:
        ghe: A Dragonfly Ground Heat Exchanger object that can be used within an
            District Energy System (DES).
"""

ghenv.Component.Name = 'DF Ground Heat Exchanger'
ghenv.Component.NickName = 'GHE'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.des.ghe import GroundHeatExchanger
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:  # import ladybug-rhino
    from ladybug_rhino.togeometry import to_polygon2d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # create the ground heat exchanger object
    name = clean_string(_name_) if _name_ is not None else 'unnamed'
    ghe = GroundHeatExchanger(name, to_polygon2d(_geo))
    if _name_ is not None:
        ghe.display_name = _name_

    # assign any of the optional properties if they are specified
    if _soil_conduct_:
        ghe.soil_parameters.conductivity = _soil_conduct_
    if _soil_heat_cap_:
        ghe.soil_parameters.heat_capacity = _soil_heat_cap_
    if _soil_temper_ is not None:
        ghe.soil_parameters.undisturbed_temp = _soil_temper_
    if _bore_length_:
        ghe.borehole_parameters.length = _bore_length_
    if _bore_depth_:
        ghe.borehole_parameters.buried_depth = _bore_depth_
