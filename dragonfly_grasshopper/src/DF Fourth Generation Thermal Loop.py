# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an Fourth Generation Loop for a District Energy Simulation (DES) simulation.
_
This includes a central hot and chilled water plant for the district.
-

    Args:
        _heating_plant_: Optional HeatingPlant object from the "DF Heating Plant" component
            to specify the properties of the heating plant in the loop. If unspecified,
            default heating plant properties will be used.
        _cooling_plant_: Optional CoolingPlant object from the "DF Cooling Plant" component
            to specify the properties of the cooling plant in the loop. If unspecified,
            default cooling plant properties will be used.
        _name_: Text to be used for the name and identifier of the Thermal Loop.
            If no name is provided, it will be "unnamed".

    Returns:
        report: Reports, errors, warnings, etc.
        loop: A Dragonfly Thermal Loop object possessing all infrastructure for a
            District Energy Simulation (DES) simulation. This should be connected
            to the loop_ input of the "DF Model to GeoJSON" component.
"""

ghenv.Component.Name = 'DF Fourth Generation Thermal Loop'
ghenv.Component.NickName = 'Gen4Loop'
ghenv.Component.Message = '1.10.2'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.des.loop import FourthGenThermalLoop
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


# set defaults
name = clean_ep_string(_name_) if _name_ is not None else 'unnamed'
# create the loop
des_loop = FourthGenThermalLoop(name, _cooling_plant_, _heating_plant_)
if _name_ is not None:
    des_loop.display_name = _name_
