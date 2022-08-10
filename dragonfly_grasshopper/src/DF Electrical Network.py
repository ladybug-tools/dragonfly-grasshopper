# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an OpenDSS Electrical Network, which represents all electrical infrastructure
for an OpenDSS simulation.
_
This includes a substation, transformers, and all electrical connectors needed
to connect these objects to Dragonfly Buildings.
-

    Args:
        _substation: A Substation object representing the electrical substation
            supplying the network with electricity.
        _transformers: An array of Transformer objects that are included within the
            electrical network. Generally, there should always be a transformer
            somewhere between the substation and a given building.
        _connectors: An array of ElectricalConnector objects that are included within
            the electrical network. In order for a given connector to be valid
            within the network, each end of the connector must touch either
            another connector, a transformer/substation or a Dragonfly Building
            footprint. In order for the network as a whole to be valid, all
            Buildings and Transformers must be connected back to the Substation
            via connectors.
        _name_: Text to be used for the name and identifier of the Electrical
            Newtork. If no name is provided, it will be "unnamed".

    Returns:
        report: Reports, errors, warnings, etc.
        network: A Dragonfly Electrical Newtork object possessing all electrical
            infrastructure for an OpenDSS simulation. This should be connected
            to the network_ input of the "DF Model to GeoJSON" component.
"""

ghenv.Component.Name = 'DF Electrical Network'
ghenv.Component.NickName = 'Network'
ghenv.Component.Message = '1.5.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.opendss.network import ElectricalNetwork
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set a default name
    name = clean_ep_string(_name_) if _name_ is not None else 'unnamed'

    # create the network
    network = ElectricalNetwork(name, _substation, _transformers, _connectors)
    if _name_ is not None:
        network.display_name = _name_
