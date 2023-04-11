# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an Ground Heat Exchanger Thermal Loop, which represents all infrastructure
for a District Energy Simulation (DES) simulation.
_
This includes a ground heat exchanger and all thermal connectors needed
to connect these objects to Dragonfly Buildings.
-

    Args:
        _ghe: A GroundHeatExchanger object representing the field
            of boreholes that supplies the loop with thermal capacity.
        _connectors: An array of ThermalConnector objects that are included
            within the thermal loop. In order for a given connector to be
            valid within the loop, each end of the connector must touch either
            another connector, a building footprint, or the ground_heat_exchanger. In
            order for the loop as a whole to be valid, the connectors must form a
            single continuous loop when passed through the buildings and the heat
            exchanger field.
        _clockwise_: A boolean to note whether the direction of flow through the
            loop is clockwise (True) when viewed from above in the GeoJSON or it
            is counterclockwise (False). (Default: False).
        _name_: Text to be used for the name and identifier of the Thermal Loop.
            If no name is provided, it will be "unnamed".

    Returns:
        report: Reports, errors, warnings, etc.
        loop: A Dragonfly Thermal Loop object possessing all infrastructure for a
            District Energy Simulation (DES) simulation. This should be connected
            to the loop_ input of the "DF Model to GeoJSON" component.
"""

ghenv.Component.Name = 'DF GHE Thermal Loop'
ghenv.Component.NickName = 'GHELoop'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.des.loop import GHEThermalLoop
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set a default name
    name = clean_ep_string(_name_) if _name_ is not None else 'unnamed'

    # create the loop
    des_loop = GHEThermalLoop(name, _ghe, _connectors, _clockwise_)
    if _name_ is not None:
        des_loop.display_name = _name_
