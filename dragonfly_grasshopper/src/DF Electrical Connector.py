# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an OpenDSS Electrical Connector from linear geometry and power line
properties, which include the wires and their geometrical arrangement.
-

    Args:
        _geo: A line or polyline representing an Electrical Connector.
        _power_line: Text for the ID of a PowerLine carried along the electrical connector,
            which will be looked up in the Power Lines library (the output from the
            "DF OpenDSS Libraries" component). This can also be a custom
            PowerLine object created using the Ladybug Tools SDK.
        _name_: Text to set the base name for the Electrical Connector, which will also
            be incorporated into unique ElectricalConnector identifier. If the
            name is not provided, a random one will be assigned.

    Returns:
        connector: A Dragonfly Electrical Connector object that can be used within an
            Electrical Network.
"""

ghenv.Component.Name = 'DF Electrical Connector'
ghenv.Component.NickName = 'ElecConnect'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: Electric Grid'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.opendss.lib.powerlines import power_line_by_identifier
    from dragonfly_energy.opendss.connector import ElectricalConnector
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:  # import ladybug-rhino
    from ladybug_rhino.togeometry import to_polyline2d
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list, \
        document_counter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # get the power line object used by the connector
    if isinstance(_power_line, str):
        _power_line = power_line_by_identifier(_power_line)

    # convert rhino geometry to ladybug geometry
    lines = []
    for geo in _geo:
        lines.append(to_polyline2d(geo))

    connector = []  # list of connectors that will be returned
    for i, geo in enumerate(lines):
        # get the name for the ElectricalConnector
        if len(_name_) == 0:  # make a default ElectricalConnector name
            display_name = 'ElectricalConnector_{}'.format(
                document_counter('e_connector_count'))
        else:
            display_name = '{}_{}'.format(longest_list(_name_, i), i + 1) \
                if len(_name_) != len(lines) else longest_list(_name_, i)
        name = clean_and_id_string(display_name)

        # create the ElectricalConnector
        conn = ElectricalConnector(name, geo, _power_line)
        conn.display_name = display_name
        connector.append(conn)
