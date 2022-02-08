# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a REopt ground-mounted photovoltaic system from its footprint geometry
(horizontal Rhino surfaces).
-

    Args:
        _geo: A horizontal Rhino surface (or closed polyline) representing a footprint
            to be converted into a ground-mounted photovoltaic system.
        _name_: Text to set the name for the PV system, which will also be incorporated
            into unique PV system identifier.  If the name is not provided,
            a random one will be assigned.
        bldg_: An optional Dragonfly Building with which the photovoltaic system is
            associated. If None, the PV system will be assumed to be a
            community PV field that isn't associated with a particular
            building meter.

    Returns:
        ground_pv: A Dragonfly ground-mounted PV system object that can be exported to
            a GeoJSON in order to account for ground-mounted photovoltaics in
            a REopt simulation.
"""

ghenv.Component.Name = 'DF Ground Photovoltaics'
ghenv.Component.NickName = 'GroundPV'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.reopt import GroundMountPV
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:  # import ladybug-rhino
    from ladybug_rhino.togeometry import to_polygon2d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    name = clean_string(_name_) if _name_ is not None else 'unnamed'
    ground_pv = GroundMountPV(name, to_polygon2d(_geo))
    if _name_ is not None:
        ground_pv.display_name = _name_
    if bldg_ is not None:
        assert isinstance(bldg_, Building), \
            'Expected Dragonfly Building. Got {}.'.format(type(bldg_))
        ground_pv.building_identifier = bldg_.identifier
