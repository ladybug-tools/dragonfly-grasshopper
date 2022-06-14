# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply process loads to a Dragonfly Room2D or all Room2Ds of a Dragonfly Story,
Building or Model.
_
Examples of process loads include wood burning fireplaces, kilns, manufacturing
equipment, and various industrial processes. They can also be used to represent 
certain specialized pieces of equipment to be separated from the other end uses,
such as MRI machines, theatrical lighting, elevators, etc.
-

    Args:
        _df_obj: A Dragonfly Room2D, Story or Building to which process loads should
            be assigned.
        _name_: Text to set the name for the Process load and to be incorporated into a
            unique Process load identifier. If None, a unique name will be
            generated.
        _watts: A number for the process load power in Watts.
        _schedule: A fractional schedule for the use of the process over the course of
            the year. The fractional values will get multiplied by the _watts
            to yield a complete process load profile.
        _fuel_type: Text to denote the type of fuel consumed by the process. Using the
            "None" type indicates that no end uses will be associated with the
            process, only the zone gains. Choose from the following.
                * Electricity
                * NaturalGas
                * Propane
                * FuelOilNo1
                * FuelOilNo2
                * Diesel
                * Gasoline
                * Coal
                * Steam
                * DistrictHeating
                * DistrictCooling
                * OtherFuel1
                * OtherFuel2
                * None
        use_category_: Text to indicate the end-use subcategory, which will identify
            the process load in the EUI output. For example, “Cooking”,
            “Clothes Drying”, etc. (Default: General).
        radiant_fract_: A number between 0 and 1 for the fraction of the total
            process load given off as long wave radiant heat. (Default: 0).
        latent_fract_: A number between 0 and 1 for the fraction of the total
            process load that is latent (as opposed to sensible). (Default: 0).
        lost_fract_: A number between 0 and 1 for the fraction of the total
            process load that is lost outside of the zone and the HVAC system.
            Typically, this is used to represent heat that is exhausted directly
            out of a zone (as you would for a stove). (Default: 0).

    Returns:
        report: Reports, errors, warnings, etc.
        rooms: The input Dragonfly object with process loads assigned to them.
"""

ghenv.Component.Name = 'DF Process Load'
ghenv.Component.NickName = 'DFProcess'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the honeybee extension
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.load.process import Process
    from honeybee_energy.lib.schedules import schedule_by_identifier
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
    # duplicate the initial object and collect all room2d objects
    df_obj = _df_obj.duplicate()
    if isinstance(df_obj, Room2D):
        rooms = [df_obj]
    elif isinstance(df_obj, Building):
        rooms = df_obj.unique_room_2ds
    elif isinstance(df_obj, (Story, Model)):
        rooms = df_obj.room_2ds
    else:
        raise ValueError('Expected dragonfly Room2D, Story, Building or Model. '
                         'Got {}.'.format(type(df_obj)))

    # set default values and check the inputs
    use_category_ = 'Process' if use_category_ is None else use_category_
    radiant_fract_ = 0.0 if radiant_fract_ is None else radiant_fract_
    latent_fract_ = 0.0 if latent_fract_ is None else latent_fract_
    lost_fract_ = 0.0 if lost_fract_ is None else lost_fract_
    if isinstance(_schedule, str):
        _schedule = schedule_by_identifier(_schedule)

    # loop through the rooms and assign process loads
    if _watts != 0:
        for room in rooms:
            name = clean_and_id_ep_string('Process') if _name_ is None else \
                clean_ep_string(_name_)
            process = Process(
                '{}..{}'.format(name, room.identifier), _watts, _schedule,
                _fuel_type, use_category_, radiant_fract_, latent_fract_, lost_fract_
            )
            room.properties.energy.add_process_load(process)
