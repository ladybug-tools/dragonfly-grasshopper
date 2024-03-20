# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply an All-Air template HVAC to a list of Dragonfly Buildings, Stories or Room2Ds.
_
All-air systems provide both ventilation and satisfaction of heating + cooling
demand with the same stream of warm/cool air. As such, they often grant tight
control over zone humidity. However, because such systems often involve the
cooling of air only to reheat it again, they are often more energy intensive
than systems that separate ventilation from the meeting of thermal loads.
-

    Args:
        _df_objs: Dragonfly Buildings, Stories or Room2Ds to which the input template
            HVAC will be assigned. If a list of Room2Ds is input, all objects
            will receive the same HVAC instance. Otherwise, each object gets its
            own instance (eg. each input Story will get its own HVAC). This can
            also be an etire dragonfly Model.
        _system_type: Text for the specific type of all-air system and equipment.
            The "HB All-Air HVAC Templates" component has a full list of the
            supported all-air system templates.
        _vintage_: Text for the vintage of the template system. This will be used
            to set efficiencies for various pieces of equipment within the system.
            The "HB Building Vintages" component has a full list of supported
            HVAC vintages. (Default: ASHRAE_2019).
        _name_: Text to set the name for the HVAC system and to be incorporated into
            unique HVAC identifier. If the name is not provided, a random name
            will be assigned.
        _economizer_: Text to indicate the type of air-side economizer used on the
            HVAC system. Economizers will mix in a greater amount of outdoor
            air to cool the zone (rather than running the cooling system) when
            the zone needs cooling and the outdoor air is cooler than the zone.
            Choose from the options below. (Default: NoEconomizer).
                * NoEconomizer
                * DifferentialDryBulb
                * DifferentialEnthalpy
                * DifferentialDryBulbAndEnthalpy
                * FixedDryBulb
                * FixedEnthalpy
                * ElectronicEnthalpy
        sensible_hr_: A number between 0 and 1 for the effectiveness of sensible
            heat recovery within the system. Typical values range from 0.5 for
            simple glycol loops to 0.81 for enthalpy wheels (the latter tends to
            be fiarly expensive for air-based systems). (Default: 0).
        latent_hr_: A number between 0 and 1 for the effectiveness of latent heat
            recovery within the system. Typical values are 0 for all types of
            heat recovery except enthalpy wheels, which can have values as high
            as 0.76. (Default: 0).
        dcv_: Boolean to note whether demand controlled ventilation should be
            used on the system, which will vary the amount of ventilation air
            according to the occupancy schedule of the zone. (Default: False).

    Returns:
        df_objs: The input Dragonfly objects with an all-air HVAC system applied.
"""

ghenv.Component.Name = "DF All-Air HVAC"
ghenv.Component.NickName = 'DFAllAirHVAC'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import os
import json

try:  # import the honeybee extension
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.config import folders
    from honeybee_energy.hvac.allair import EQUIPMENT_TYPES_DICT
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
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
    'DOE_Ref_Pre_1980': 'DOE_Ref_Pre_1980',
    'DOE_Ref_1980_2004': 'DOE_Ref_1980_2004',
    'ASHRAE_2004': 'ASHRAE_2004',
    'ASHRAE_2007': 'ASHRAE_2007',
    'ASHRAE_2010': 'ASHRAE_2010',
    'ASHRAE_2013': 'ASHRAE_2013',
    'ASHRAE_2016': 'ASHRAE_2016',
    'ASHRAE_2019': 'ASHRAE_2019',
    'DOE Ref Pre-1980': 'DOE_Ref_Pre_1980',
    'DOE Ref 1980-2004': 'DOE_Ref_1980_2004',
    '90.1-2004': 'ASHRAE_2004',
    '90.1-2007': 'ASHRAE_2007',
    '90.1-2010': 'ASHRAE_2010',
    '90.1-2013': 'ASHRAE_2013',
    'pre_1980': 'DOE_Ref_Pre_1980',
    '1980_2004': 'DOE_Ref_1980_2004',
    '2004': 'ASHRAE_2004',
    '2007': 'ASHRAE_2007',
    '2010': 'ASHRAE_2010',
    '2013': 'ASHRAE_2013',
    '2016': 'ASHRAE_2016',
    '2019': 'ASHRAE_2019',
    None: 'ASHRAE_2019'
}

# dictionary of HVAC template names
ext_folder = folders.standards_extension_folders[0]
hvac_reg = os.path.join(ext_folder, 'hvac_registry.json')
with open(hvac_reg, 'r') as f:
    hvac_dict = json.load(f)


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    df_objs = [obj.duplicate() for obj in _df_objs]

    # process any input properties for the HVAC system
    try:  # get the class for the HVAC system
        try:
            _sys_name = hvac_dict[_system_type]
        except KeyError:
            _sys_name = _system_type
        hvac_class = EQUIPMENT_TYPES_DICT[_sys_name]
    except KeyError:
        raise ValueError('System Type "{}" is not recognized as an all-air HVAC '
                         'system.'.format(_system_type))
    vintage = vintages[_vintage_]  # get the vintage of the HVAC
    name = clean_and_id_ep_string('All-Air HVAC') if _name_ is None else clean_ep_string(_name_)

    # create the HVAC
    hvac = hvac_class(name, vintage, _sys_name)
    if _economizer_ is not None:
        hvac.economizer_type = _economizer_
    if sensible_hr_ is not None:
        hvac.sensible_heat_recovery = sensible_hr_
    if latent_hr_ is not None:
        hvac.latent_heat_recovery = latent_hr_
    if dcv_:
        hvac.demand_controlled_ventilation = True
    if _name_ is not None:
        hvac.display_name = _name_

    # apply the HVAC system to the objects
    for obj in df_objs:
        if isinstance(obj, (Building, Story)):
            obj.properties.energy.set_all_room_2d_hvac(hvac)
        elif isinstance(obj, Room2D):
            if obj.properties.energy.is_conditioned:
                obj.properties.energy.hvac = hvac
        elif isinstance(obj, Model):
            for bldg in obj.buildings:
                bldg.properties.energy.set_all_room_2d_hvac(hvac)
        else:
            raise ValueError(
                'Expected Dragonfly Room2D, Story, Building, or Model. '
                'Got {}.'.format(type(obj)))
