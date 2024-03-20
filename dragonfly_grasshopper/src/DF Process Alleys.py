# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Remove windows from any walls that are within a certain distance of other buildings.
_
The component can also optionally set the boundary conditions of these walls to
adiabatic. This is helpful when attempting to account for alleys or parti walls
that may exist between buildings of a denser urban district.
-

    Args:
        _buildings: Dragonfly Building objects which will have their windows removed
            if their walls lie within the distance of another building.
            This can also be an entire Dragonfly Model.
        _distance_: A number for the maximum distance of an alleyway in Rhino model
            units. If a wall is closer to another Building than this distance,
            the windows will be removed. (Default: 1.0 meters).
        adiabatic_: A boolean to note whether the walls that have their windows removed
            should also receive an Adiabatic boundary condition. This is useful
            when the alleyways are more like parti walls than distinct pathways
            that someone could traverse.

    Returns:
        report: Reports, errors, warnings, etc.
        buildings: The Building objects with their windows removed from any detected alleys.
"""

ghenv.Component.Name = 'DF Process Alleys'
ghenv.Component.NickName = 'Alleys'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.building import Building
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance, conversion_to_meters
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects and set a default distance
    buildings = [obj.duplicate() for obj in _buildings]
    dist = _distance_ if _distance_ is not None else 1 / conversion_to_meters()

    # extract the Buildings from any input Models
    bldgs = []
    for obj in buildings:
        if isinstance(obj, Building):
            bldgs.append(obj)
        elif isinstance(obj, Model):
            bldgs.extend(obj.buildings)
        else:
            msg = 'Expected Dragonfly Building or Model. Got {}.'.format(type(obj))
            raise ValueError(msg)

    # process the alleyways
    Building.process_alleys(bldgs, dist, adiabatic_, tolerance)
