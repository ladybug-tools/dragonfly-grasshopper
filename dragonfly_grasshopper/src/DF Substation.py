# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an OpenDSS Substation from its footprint geometry (horizontal Rhino surfaces).
-

    Args:
        _geo: A horizontal Rhino surface representing a footprint to be converted
            into a Substation.
        _name_: Text to set the name for the Substation, which will also be incorporated
            into unique Substation identifier.  If the name is not provided,
            a random one will be assigned.

    Returns:
        substation: A Dragonfly Substation object that can be used within an
            Electrical Network.
"""

ghenv.Component.Name = 'DF Substation'
ghenv.Component.NickName = 'Substation'
ghenv.Component.Message = '1.4.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.opendss.substation import Substation
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:  # import ladybug-rhino
    from ladybug_rhino.togeometry import to_polygon2d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    name = clean_string(_name_) if _name_ is not None else 'unnamed'
    substation = Substation(name, to_polygon2d(_geo))
    if _name_ is not None:
        substation.display_name = _name_
