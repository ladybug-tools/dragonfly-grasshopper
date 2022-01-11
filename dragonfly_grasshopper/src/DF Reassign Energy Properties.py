# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Re-assign energy properties to any Dragonfly object (Building, Story, Room2D, Model).
_
This is useful for editing auto-generated child objects separately from their parent.
For example, if you want to assign all of the ground floors of a given auto-generated
Building to have a Retail ProgramType, this can help re-assign a Retail ProgramType
to such stories.
-

    Args:
        _df_obj: A Dragonfly Building, Story or Room2D which is to have its energy
            properties re-assigned. This can also be an entire Dragonfly Model.
        program_: Text to reassign the program of the input objects (to be looked
            up in the ProgramType library) such as that output from the "HB List
            Programs" component. This can also be a custom ProgramType object.
        constr_set_: Text to reassign construction set of the input objects, which
            is usedto assign all default energy constructions needed to create an
            energy model. Text should refer to a ConstructionSet within the library
            such as that output from the "HB List Construction Sets" component.
            This can also be a custom ConstructionSet object.

    Returns:
        df_obj: The input Dragonfly object with its properties re-assigned based
            on the input.
"""

ghenv.Component.Name = 'DF Reassign Energy Properties'
ghenv.Component.NickName = 'ReassignProp'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import ladybug-rhino
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.programtypes import program_type_by_identifier, \
        building_program_type_by_identifier
    from honeybee_energy.lib.constructionsets import construction_set_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy energy:\n\t{}'.format(e))

try:  # import the dragonfly-energy extension
    import dragonfly_energy
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy energy:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    df_obj = _df_obj.duplicate()

    # try to assign the program
    if program_ is not None:
        if isinstance(program_, str):
            try:
                program_ = building_program_type_by_identifier(program_)
            except ValueError:
                program_ = program_type_by_identifier(program_)
        if isinstance(df_obj, (Building, Story)):
            df_obj.properties.energy.set_all_room_2d_program_type(program_)
        elif isinstance(df_obj, Room2D):
            df_obj.properties.energy.program_type = program_
        elif isinstance(df_obj, Model):
            for bldg in df_obj.buildings:
                bldg.properties.energy.set_all_room_2d_program_type(program_)
        else:
            raise ValueError('Expected dragonfly Room2D, Story, Building or Model. '
                             'Got {}.'.format(type(df_obj)))

    # try to assign the construction set
    if constr_set_ is not None:
        if isinstance(constr_set_, str):
            constr_set_ = construction_set_by_identifier(constr_set_)
        if isinstance(df_obj, Model):
            for bldg in df_obj.buildings:
                bldg.properties.energy.construction_set = constr_set_
        else:
            df_obj.properties.energy.construction_set = constr_set_
