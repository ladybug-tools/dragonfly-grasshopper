# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create Dragonfly Buildings from footprint geometry (horizontal Rhino surfaces).
-

    Args:
        _footprint_geo: A list of horizontal Rhino surfaces or closed planar curves
            to be converted into Buildings.
        _floor_to_floor: A list of float values with a length equal to the number of
            stories in each Building. Each value in the list represents the
            floor_to_floor height of the Story starting from the first floor and
            then moving to the top floor.
        perim_offset_: An optional positive number that will be used to offset
            the perimeter of the footprint to create core/perimeter Rooms.
            If this value is None or 0, no offset will occur and each floor
            plate will be represented with a single Room2D.
        _name_: Text to set the base name for the Building, which will also be
            incorporated into unique Building identifier. This will be combined
            with the index of each input _footprint_geo to yield a unique name
            for each output Building. If the name is not provided, a random one
            will be assigned.
        _program_: Text for the program of the Buildings (to be looked up in the
            ProgramType library) such as that output from the "HB List Programs"
            component. This can also be a custom ProgramType object. If no program
            is input here, the Buildings will have a generic office program.
        _constr_set_: Text for the construction set of the Buildings, which is used
            to assign all default energy constructions needed to create an energy
            model. Text should refer to a ConstructionSet within the library such
            as that output from the "HB List Construction Sets" component. This
            can also be a custom ConstructionSet object. If nothing is input here,
            the Buildings will have a generic construction set that is not sensitive
            to the Buildings's climate or building energy code.
        conditioned_: Boolean to note whether the Buildings have heating and cooling
            systems.
        _run: Set to True to run the component and create Dragonfly Buildings.

    Returns:
        report: Reports, errors, warnings, etc.
        buildings: Dragonfly buildings.
"""

ghenv.Component.Name = 'DF Building from Footprint'
ghenv.Component.NickName = 'BuildingFootprint'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_string, clean_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs, document_counter, \
        longest_list
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


if all_required_inputs(ghenv.Component) and _run:
    perim_offset_ = 0 if perim_offset_ is None else perim_offset_
    buildings = []  # list of buildings that will be returned
    for i, geo in enumerate(_footprint_geo):
        # get the name for the Building
        if len(_name_) == 0:  # make a default Building name
            display_name = 'Building_{}'.format(document_counter('bldg_count'))
            name = clean_and_id_string(display_name)
        else:
            display_name = '{}_{}'.format(longest_list(_name_, i), i + 1) \
                if len(_name_) != len(_footprint_geo) else longest_list(_name_, i)
            name = clean_string(display_name)

        # create the Building
        building = Building.from_footprint(
            name, footprint=to_face3d(geo), floor_to_floor_heights=_floor_to_floor,
            perimeter_offset=perim_offset_, tolerance=tolerance)
        building.display_name = display_name

        # assign the program
        if len(_program_) != 0:
            program = longest_list(_program_, i)
            if isinstance(program, str):
                try:
                    program = building_program_type_by_identifier(program)
                except ValueError:
                    program = program_type_by_identifier(program)
            building.properties.energy.set_all_room_2d_program_type(program)
            try:
                building.properties.uwg.infer_program_from_energy_program()
            except  (NameError, AttributeError):
                pass  # dragonfly-uwg is not installed
        else:  # generic office program by default
            try:
                building.properties.energy.set_all_room_2d_program_type(office_program)
            except (NameError, AttributeError):
                pass  # honeybee-energy is not installed

        # assign the construction set
        if len(_constr_set_) != 0:
            constr_set = longest_list(_constr_set_, i)
            if isinstance(constr_set, str):
                constr_set = construction_set_by_identifier(constr_set)
            building.properties.energy.construction_set = constr_set

        # assign an ideal air system
        if len(conditioned_) == 0 or longest_list(conditioned_, i):
            try:
                building.properties.energy.add_default_ideal_air()
            except (NameError, AttributeError):
                pass  # honeybee-energy is not installed

        buildings.append(building)
