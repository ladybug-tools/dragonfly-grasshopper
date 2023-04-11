# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an District Energy System (DES) Thermal Connector from linear geometry.
-

    Args:
        _geo: A line or polyline representing an Thermal Connector.
        _name_: Text to set the base name for the Thermal Connector, which will also
            be incorporated into unique ThermalConnector identifier. If the
            name is not provided, a random one will be assigned.

    Returns:
        connector: A Dragonfly Thermal Connector object that can be used within
            a District Energy System (DES).
"""

ghenv.Component.Name = 'DF Thermal Connector'
ghenv.Component.NickName = 'DESConnector'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.des.connector import ThermalConnector
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:  # import ladybug-rhino
    from ladybug_rhino.togeometry import to_linesegment2d, to_polyline2d
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list, \
        document_counter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # convert rhino geometry to ladybug geometry
    lines = []
    for geo in _geo:
        try:
            lines.append(to_polyline2d(geo))
        except AttributeError:
            lines.append(to_linesegment2d(geo))

    connector = []  # list of connectors that will be returned
    for i, geo in enumerate(lines):
        # get the name for the ThermalConnector
        if len(_name_) == 0:  # make a default ThermalConnector name
            display_name = 'ThermalConnector_{}'.format(
                document_counter('t_connector_count'))
        else:
            display_name = '{}_{}'.format(longest_list(_name_, i), i + 1) \
                if len(_name_) != len(lines) else longest_list(_name_, i)
        name = clean_and_id_string(display_name)

        # create the ThermalConnector
        conn = ThermalConnector(name, geo)
        conn.display_name = display_name
        connector.append(conn)
