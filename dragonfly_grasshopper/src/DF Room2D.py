# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create Dragonfly Room2Ds from floor plate geometry (horizontal Rhino surfaces).
-

    Args:
        _geo: A list of horizontal Rhino surfaces or closed planar polylines
            representing floor plates to be converted into Room2Ds.
        _flr_to_ceiling: A number for the height above the floor where the
            ceiling begins. Typical values range from 3 to 5 meters.
        _name_: Text to set the base name for the Room2D, which will also be
            incorporated into unique Room2D identifier. This will be combined
            with the index of each input _footprint_geo to yield a unique name
            for each output Room2D. If the name is not provided, a random one
            will be assigned.
        _program_: Text for the program of the Room2Ds (to be looked up in the
            ProgramType library) such as that output from the "HB List Programs"
            component. This can also be a custom ProgramType object. If no program
            is input here, the Room2Ds will have a generic office program.
        _constr_set_: Text for the construction set of the Room2Ds, which is used
            to assign all default energy constructions needed to create an energy
            model. Text should refer to a ConstructionSet within the library such
            as that output from the "HB List Construction Sets" component. This
            can also be a custom ConstructionSet object. If nothing is input here,
            the Room2Ds will have a generic construction set that is not sensitive
            to the Room2Ds's climate or building energy code.
        conditioned_: Boolean to note whether the Room2Ds have heating and cooling
            systems.

    Returns:
        report: Reports, errors, warnings, etc.
        room2d: Dragonfly Room2Ds.
"""

ghenv.Component.Name = 'DF Room2D'
ghenv.Component.NickName = 'Room2D'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '4'


try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list, \
        document_counter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the dragonfly-energy extension
    import dragonfly_energy
    from honeybee_energy.lib.programtypes import program_type_by_identifier, \
        building_program_type_by_identifier, office_program
    from honeybee_energy.lib.constructionsets import construction_set_by_identifier
except ImportError as e:
    if len(_program_) != 0:
        raise ValueError('_program_ has been specified but dragonfly-energy '
                         'has failed to import.\n{}'.format(e))
    elif len(_constr_set_) != 0:
        raise ValueError('_constr_set_ has been specified but dragonfly-energy '
                         'has failed to import.\n{}'.format(e))
    elif len(conditioned_) != 0:
        raise ValueError('conditioned_ has been specified but dragonfly-energy '
                         'has failed to import.\n{}'.format(e))


if all_required_inputs(ghenv.Component):
    room2d = []  # list of room2ds that will be returned
    face3ds = [face for geo in _geo for face in to_face3d(geo)]  # convert to lb geo
    for i, geo in enumerate(face3ds):
        # get the name for the Room2D
        if len(_name_) == 0:  # make a default Room2D name
            display_name = 'Room_{}'.format(document_counter('room_count'))
        else:
            display_name = '{}_{}'.format(longest_list(_name_, i), i + 1) \
                if len(_name_) != len(face3ds) else longest_list(_name_, i)
        name = clean_and_id_string(display_name)

        # create the Room2D
        room = Room2D(name, geo, longest_list(_flr_to_ceiling, i), tolerance=tolerance)
        room.display_name = display_name

        # assign the program
        if len(_program_) != 0:
            program = longest_list(_program_, i)
            if isinstance(program, str):
                try:
                    program = building_program_type_by_identifier(program)
                except ValueError:
                    program = program_type_by_identifier(program)
            room.properties.energy.program_type = program 
        else:  # generic office program by default
            try:
                room.properties.energy.program_type = office_program
            except (NameError, AttributeError):
                pass  # honeybee-energy is not installed

        # assign the construction set
        if len(_constr_set_) != 0:
            constr_set = longest_list(_constr_set_, i)
            if isinstance(constr_set, str):
                constr_set = construction_set_by_identifier(constr_set)
            room.properties.energy.construction_set = constr_set

        # assign an ideal air system
        if len(conditioned_) == 0 or longest_list(conditioned_, i):
            try:
                room.properties.energy.add_default_ideal_air()
            except (NameError, AttributeError):
                pass  # honeybee-energy is not installed

        room2d.append(room)
