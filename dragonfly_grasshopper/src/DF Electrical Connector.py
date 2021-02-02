# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create an OpenDSS Electrical Connector from its linear geometry and the wires
carried along it.
-

    Args:
        _geo: A line or polyline representing an Electrical Connector.
        _wires: A list of text for the wires carried along the electrical connector,
            which will be looked up in the Wires library (the output from the
            "DF OpenDSS Libraries" component). This can also be a list of
            custom Wire objects.
        _name_: Text to set the base name for the Electrical Connector, which will also
            be incorporated into unique ElectricalConnector identifier. If the
            name is not provided, a random one will be assigned.

    Returns:
        connector: A Dragonfly Electrical Connector object that can be used within an
            Electrical Network.
"""

ghenv.Component.Name = 'DF Electrical Connector'
ghenv.Component.NickName = 'Connector'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.opendss.lib.wires import wire_by_identifier
    from dragonfly_energy.opendss.connector import ElectricalConnector
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:  # import ladybug-rhino
    from ladybug_rhino.togeometry import to_linesegment2d, to_polyline2d
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list, \
        document_counter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # get the wires carried along the connector
    wire_objs = []
    for wire in _wires:
        if isinstance(wire, str):
            wire_objs.append(wire_by_identifier(wire))
        else:
            wire_objs.append(wire)

    # convert rhino geometry to ladybug geometry
    lines = []
    for geo in _geo:
        try:
            lines.append(to_polyline2d(geo))
        except AttributeError:
            lines.append(to_linesegment2d(geo))

    connector = []  # list of connectors that will be returned
    for i, geo in enumerate(lines):
        # get the name for the ElectricalConnector
        if len(_name_) == 0:  # make a default ElectricalConnector name
            display_name = 'ElectricalConnector_{}'.format(
                document_counter('e_connector_count'))
        else:
            display_name = '{}_{}'.format(longest_list(_name_, i), i + 1) \
                if len(_name_) != len(lines) else longest_list(_name_, i)
        name = clean_and_id_ep_string(display_name)

        # create the ElectricalConnector
        conn = ElectricalConnector(name, geo, wire_objs)
        conn.display_name = display_name
        connector.append(conn)
