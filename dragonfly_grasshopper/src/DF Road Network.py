# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an RNM Road Network, which represents the streets along which electrical
infrastructure will be placed by RNM.
_
This includes a substation and road geometries running between the buildings.
-

    Args:
        _substation: A Substation object representing the electrical substation
            supplying the network with electricity.
        _road_geo: An array of Lines or Polylines that represent the roads within the
            network.
        _name_: Text to be used for the name and identifier of the Road Newtork. If
            no name is provided, it will be "unnamed".

    Returns:
        report: Reports, errors, warnings, etc.
        network: A Dragonfly Road Newtork object possessing all roads needed for an
            RNM simulation. This should be connected to the network_ input of
            the "DF Model to GeoJSON" component.
"""

ghenv.Component.Name = 'DF Road Network'
ghenv.Component.NickName = 'Roads'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_ep_string, clean_and_id_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.opendss.road import Road
    from dragonfly_energy.opendss.network import RoadNetwork
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_linesegment2d, to_polyline2d
    from ladybug_rhino.grasshopper import all_required_inputs, \
        document_counter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set a default name
    name = clean_ep_string(_name_) if _name_ is not None else 'unnamed'

    # create the roads
    lines = []
    for geo in _road_geo:
        try:
            lines.append(to_polyline2d(geo))
        except AttributeError:
            lines.append(to_linesegment2d(geo))
    roads = []
    for i, geo in enumerate(lines):
        # get the name for the Road
        if _name_ is None:  # make a default Road name
            display_name = 'Road_{}'.format(document_counter('road_count'))
        else:
            display_name = '{}_{}'.format(_name_, i + 1)
        r_name = clean_and_id_string(display_name)
        road = Road(r_name, geo)
        road.display_name = display_name
        roads.append(road)

    # create the network
    network = RoadNetwork(name, _substation, roads)
    if _name_ is not None:
        network.display_name = _name_
