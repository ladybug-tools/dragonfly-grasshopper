# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply a template system that only supplies heating and/or cooling (no ventilation)
to a list of Dragonfly Buildings, Stories or Room2Ds.
_
These systems are only designed to satisfy heating + cooling demand and they
cannot meet any minimum ventilation requirements.
_
As such, these systems tend to be used in residential or storage settings where
meeting minimum ventilation requirements may not be required or the density
of occupancy is so low that infiltration is enough to meet fresh air demand.
-

    Args:
        _df_objs: Dragonfly Buildings, Stories or Room2Ds to which the input template
            HVAC will be assigned. If a list of Room2Ds is input, all objects
            will receive the same HVAC instance. Otherwise, each object gets its
            own instance (eg. each input Story will get its own HVAC).
        _system_type: Text for the specific type of heating/cooling system and equipment.
            The "HB HeatCool HVAC Templates" component has a full list of the
            supported Heating/Cooling system templates.
        _vintage_: Text for the vintage of the template system. This will be used
            to set efficiencies for various pieces of equipment within the system.
            The "HB Building Vintages" component has a full list of supported
            HVAC vintages. (Default: 90.1-2013). Choose from the following.
                * DOE Ref Pre-1980
                * DOE Ref 1980-2004
                * 90.1-2004
                * 90.1-2007
                * 90.1-2010
                * 90.1-2013
        _name_: Text to set the name for the heating/cooling system and to be
            incorporated into unique system identifier. If the name is not
            provided, a random name will be assigned.

    Returns:
        df_objs: The input Dragonfly objects with a heating/cooling system applied.
"""

ghenv.Component.Name = "DF HeatCool HVAC"
ghenv.Component.NickName = 'DFHeatCoolHVAC'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import uuid

try:  # import the honeybee extension
    from honeybee.altnumber import autosize
    from honeybee.typing import clean_and_id_ep_string
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.hvac.heatcool import EQUIPMENT_TYPES_DICT
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
    from dragonfly.story import Story
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the dragonfly-energy extension
    import dragonfly_energy
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# dictionary to get correct vintages
vintages = {
    'DOE Ref Pre-1980': 'DOE Ref Pre-1980',
    'DOE Ref 1980-2004': 'DOE Ref 1980-2004',
    '90.1-2004': '90.1-2004',
    '90.1-2007': '90.1-2007',
    '90.1-2010': '90.1-2010',
    '90.1-2013': '90.1-2013',
    'pre_1980': 'DOE Ref Pre-1980',
    '1980_2004': 'DOE Ref 1980-2004',
    '2004': '90.1-2004',
    '2007': '90.1-2007',
    '2010': '90.1-2010',
    '2013': '90.1-2013',
    None: '90.1-2013'
    }

if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    df_objs = [obj.duplicate() for obj in _df_objs]

    # create the instance of the HVAC system to be applied to the rooms
    try:  # get the class for the HVAC system
        hvac_class = EQUIPMENT_TYPES_DICT[_system_type]
    except KeyError:
        raise ValueError('System Type "{}" is not recognized as an all-air HVAC '
                         'system.'.format(_system_type))
    vintage = vintages[_vintage_]  # get the vintage of the HVAC
    # get an identifier for the HVAC system
    name = clean_and_id_ep_string(_name_) if _name_ is not None else str(uuid.uuid4())[:8]
    hvac = hvac_class(name, vintage, _system_type)
    if _name_ is not None:
        hvac.display_name = _name_

    # apply the HVAC system to the objects
    for obj in df_objs:
        if isinstance(obj, (Building, Story)):
            obj.properties.energy.set_all_room_2d_hvac(hvac)
        elif obj.properties.energy.is_conditioned:  # assume it's a Room2D
            obj.properties.energy.hvac = hvac
