# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply a customized IdealAirSystem to Dragonfly Buildings, Stories or Room2Ds.
-

    Args:
        _df_objs: Dragonfly Buildings, Stories or Room2Ds to which the input ideal
            air properties will be assigned. This can also be an etire
            dragonfly Model.
        _economizer_: Text to indicate the type of air-side economizer used on
            the ideal air system. Economizers will mix in a greater amount of
            outdoor air to cool the zone (rather than running the cooling system)
            when the zone needs cooling and the outdoor air is cooler than the zone.
            Choose from the options below. Default: DifferentialDryBulb.
                * NoEconomizer
                * DifferentialDryBulb
                * DifferentialEnthalpy
        dcv_: Boolean to note whether demand controlled ventilation should be
            used on the system, which will vary the amount of ventilation air
            according to the occupancy schedule of the zone. Default: False.
        sensible_hr_: A number between 0 and 1 for the effectiveness of sensible
            heat recovery within the system. Default: 0.
        latent_hr_: A number between 0 and 1 for the effectiveness of latent heat
            recovery within the system. Default: 0.
        _heat_temp_: A number for the maximum heating supply air temperature
            [C]. Default: 50, which is typical for many air-based HVAC systems.
        _cool_temp_: A number for the minimum cooling supply air temperature
            [C]. Default: 13, which is typical for many air-based HVAC systems.
        _heat_limit_: A number for the maximum heating capacity in Watts. This
            can also be the text 'autosize' to indicate that the capacity should
            be determined during the EnergyPlus sizing calculation. This can also
            be the text 'NoLimit' to indicate no upper limit to the heating
            capacity. Default: 'autosize'.
        _cool_limit_: A number for the maximum cooling capacity in Watts. This
            can also be the text 'autosize' to indicate that the capacity should
            be determined during the EnergyPlus sizing calculation. This can also
            be the text 'NoLimit' to indicate no upper limit to the cooling
            capacity. Default: 'autosize'.

    Returns:
        df_objs: The input Dragonfly object with the custom Ideal Air System assigned.
"""

ghenv.Component.Name = "DF IdealAir"
ghenv.Component.NickName = 'DFIdealAir'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '3'


try:  # import the honeybee extension
    from honeybee.altnumber import autosize, no_limit
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.hvac.idealair import IdealAirSystem
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

# dictionary to get alterante number types
alt_numbers = {
    'nolimit': no_limit,
    'NoLimit': no_limit,
    'autosize': autosize,
    'Autosize': autosize,
    None: autosize
    }


def extract_room2ds(obj):
    """Get all of the Room2Ds assinged to a given dragonfly object."""
    if isinstance(obj, Building):
        return obj.unique_room_2ds
    elif isinstance(obj, Story):
        return obj.room_2ds
    elif isinstance(obj, Room2D):
        return [obj]
    elif isinstance(obj, Model):
        return [room for bldg in obj.buildings for room in bldg.unique_room_2ds]
    else:
        raise ValueError(
            'Expected Dragonfly Room2D, Story, Building, or Model. '
            'Got {}.'.format(type(hb_obj)))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    df_objs = [obj.duplicate() for obj in _df_objs]

    for df_obj in df_objs:
        for room in extract_room2ds(df_obj):
            if room.properties.energy.is_conditioned:
                # check to be sure the assigned HVAC system is an IdealAirSystem
                if not isinstance(room.properties.energy.hvac, IdealAirSystem):
                    room.properties.energy.add_default_ideal_air()

                # create the customized ideal air system
                new_ideal_air = room.properties.energy.hvac.duplicate()
                if _economizer_ is not None:
                    new_ideal_air.economizer_type = _economizer_
                if dcv_ is not None:
                    new_ideal_air.demand_controlled_ventilation = dcv_
                if sensible_hr_ is not None:
                    new_ideal_air.sensible_heat_recovery = sensible_hr_
                if latent_hr_ is not None:
                    new_ideal_air.latent_heat_recovery = latent_hr_
                if _heat_temp_ is not None:
                    new_ideal_air.heating_air_temperature = _heat_temp_
                if _cool_temp_ is not None:
                    new_ideal_air.cooling_air_temperature = _cool_temp_
                try:
                    new_ideal_air.heating_limit = alt_numbers[_heat_limit_]
                except KeyError:
                    new_ideal_air.heating_limit = _heat_limit_
                try:
                    new_ideal_air.cooling_limit = alt_numbers[_cool_limit_]
                except KeyError:
                    new_ideal_air.cooling_limit = _cool_limit_

                # assign the HVAC to the Room
                room.properties.energy.hvac = new_ideal_air
