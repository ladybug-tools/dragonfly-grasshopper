# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply a template Service Hot Water (SHW) system to Dragonfly Buildings, Stories
or Room2Ds.
-

    Args:
        _df_objs: Dragonfly Buildings, Stories or Room2Ds to which the input template
            system will be assigned. This can also be a Honeybee Model for
            which all Rooms will be assigned the SHW system.
        _system_type: Text for the specific type of service hot water system and equipment.
            The "HB SHW Templates" component has a full list of the supported
            system templates.
        _name_: Text to set the name for the Service Hot Water system and to be
            incorporated into unique system identifier. If the name is not
            provided, a random name will be assigned.
        _efficiency_: A number for the efficiency of the heater within the system.
            For Gas systems, this is the efficiency of the burner. For HeatPump
            systems, this is the rated COP of the system. For electric systems,
            this should usually be set to 1. If unspecified this value will
            automatically be set based on the equipment_type. See below for
            the default value for each equipment type:
                * Gas_WaterHeater - 0.8
                * Electric_WaterHeater - 1.0
                * HeatPump_WaterHeater - 3.5
                * Gas_TanklessHeater - 0.8
                * Electric_TanklessHeater - 1.0
        _condition_: A number for the ambient temperature in which the hot water tank
            is located [C]. This can also be a Room in which the tank is
            located. (Default: 22).
        _loss_coeff_: A number for the loss of heat from the water heater tank to the
            surrounding ambient conditions [W/K]. (Default: 6 W/K).

    Returns:
        rooms: The input Dragonfly objects with a Service Hot Water system applied.
"""

ghenv.Component.Name = "DF SHW System"
ghenv.Component.NickName = 'SHW'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the honeybee extension
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.shw import SHWSystem
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


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    df_objs = [obj.duplicate() for obj in _df_objs]

    # set default value for the inputs
    name = clean_and_id_ep_string('SHW System') if _name_ is None \
        else clean_ep_string(_name_)
    if _condition_ is None:
        _condition_ = 22
    elif isinstance(_condition_, Room):
        _condition_ = _condition_.identifier
    else:
        try:
            _condition_ = float(_condition_)
        except Exception:
            raise ValueError(
                'Input _condition_ must be a Room in which the system is located '
                'or a number\nfor the ambient temperature in which the hot water '
                'tank is located [C].\nGot {}.'.format(type(_condition_))
            )
    _loss_coeff_ = 6 if _loss_coeff_ is None else _loss_coeff_

    # create the SHW System
    shw = SHWSystem(name, _system_type, _efficiency_, _condition_, _loss_coeff_)
    if _name_ is not None:
        shw.display_name = _name_

    # apply the HVAC system to the objects
    for obj in df_objs:
        if isinstance(obj, (Building, Story)):
            obj.properties.energy.set_all_room_2d_shw(shw)
        elif isinstance(obj, Room2D) and obj.properties.energy.is_conditioned:
            obj.properties.energy.shw = shw
        elif isinstance(obj, Model):
            for bldg in obj.buildings:
                bldg.properties.energy.set_all_room_2d_shw(shw)
        else:
            raise ValueError(
                'Expected Dragonfly Room2D, Story, Building, or Model. '
                'Got {}.'.format(type(hb_obj)))
