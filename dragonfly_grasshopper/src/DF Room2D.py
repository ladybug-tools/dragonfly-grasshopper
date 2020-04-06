# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Dragonfly Room2Ds from floor plate geometry (horizontal Rhino surfaces).
-

    Args:
        _geo: A list of horizontal Rhino surfaces representing floor plates to
            be converted into Room2Ds.
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
        _run: Set to True to run the component and create Dragonfly Room2Ds.
    
    Returns:
        report: Reports, errors, warnings, etc.
        room2d: Dragonfly Room2Ds.
"""

ghenv.Component.Name = "DF Room2D"
ghenv.Component.NickName = 'Room2D'
ghenv.Component.Message = '0.1.3'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

# document-wide counter to generate new unique Room2D names
import scriptcontext
try:
    scriptcontext.sticky["room_count"]
except KeyError:  # first time that the component is running
    scriptcontext.sticky["room_count"] = 1

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
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the dragonfly-energy extension
    import dragonfly_energy
    from honeybee_energy.lib.programtypes import program_type_by_identifier, \
        office_program
    from honeybee_energy.lib.constructionsets import construction_set_by_identifier
except ImportError as e:
    if _program_ is not None:
        raise ValueError('_program_ has been specified but dragonfly-energy '
                         'has failed to import.\n{}'.format(e))
    elif _constr_set_ is not None:
        raise ValueError('_constr_set_ has been specified but dragonfly-energy '
                         'has failed to import.\n{}'.format(e))
    elif conditioned_ is not None:
        raise ValueError('conditioned_ has been specified but dragonfly-energy '
                         'has failed to import.\n{}'.format(e))

import uuid


if all_required_inputs(ghenv.Component) and _run:
    room2d = []  # list of room2ds that will be returned
    for i, geo in enumerate(_geo):
        # get the name for the Room2D
        if _name_ is None:  # make a default Room2D name
            name = "Building_{}_{}".format(scriptcontext.sticky["bldg_count"],
                                           str(uuid.uuid4())[:8])
            scriptcontext.sticky["bldg_count"] += 1
        else:
            display_name = '{}_{}'.format(_name_, i + 1)
            name = clean_and_id_string(display_name)

        # create the Room2D
        room = Room2D(name, to_face3d(geo)[0], _flr_to_ceiling, tolerance=tolerance)
        if _name_ is not None:
            room.display_name = display_name

        # assign the program
        if _program_ is not None:
            if isinstance(_program_, str):
                _program_ = program_type_by_identifier(_program_)
            room.properties.energy.program_type = _program_ 
        else:  # generic office program by default
            try:
                room.properties.energy.program_type = office_program
            except (NameError, AttributeError):
                pass  # honeybee-energy is not installed
        
        # assign the construction set
        if _constr_set_ is not None:
            if isinstance(_constr_set_, str):
                _constr_set_ = construction_set_by_identifier(_constr_set_)
            room.properties.energy.construction_set = _constr_set_
        
        # assign an ideal air system
        if conditioned_ or conditioned_ is None:  # conditioned by default
            try:
                room.properties.energy.add_default_ideal_air()
            except (NameError, AttributeError):
                pass  # honeybee-energy is not installed
        
        room2d.append(room)
