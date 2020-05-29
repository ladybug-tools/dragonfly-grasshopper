# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Load any dragonfly object from a dragonfly JSON file
-
This includes any Model, Building, Story, Room2D, WindowParameter, or ShadingParameter.
-
It also includes any energy Material, Construction, ConstructionSet, Schedule, 
Load, ProgramType, or Simulation object.
-

    Args:
        _df_file: A file path to a dragonfly JSON from which objects will be loaded
            back into Grasshopper. The objects in the file must be non-abridged
            in order to be loaded back correctly.
        _load: Set to "True to load the objects from the _df_file.
    
    Returns:
        df_objs: A list of dragonfly objects that have been re-serialized from
            the input file.
"""

ghenv.Component.Name = 'DF Load Objects'
ghenv.Component.NickName = 'LoadObjects'
ghenv.Component.Message = '0.1.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '2 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    import honeybee.model as hb_model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    import dragonfly.dictutil as df_dict_util
    from dragonfly.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the core honeybee_energy dependencies
    import honeybee_energy.dictutil as energy_dict_util
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
    from ladybug_rhino.config import units_system, tolerance
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import json


def model_units_tolerance_check(model):
    """Convert a model to the current Rhino units and check the tolerance.

    Args:
        model: A dragonfly Model, which will have its units checked.
    """
    # check the model units
    if model.units != units_system():
        print('Imported model units "{}" do not match that of the current Rhino '
            'model units "{}"\nThe model is being automatically converted '
            'to the Rhino doc units.'.format(model.units, units_system()))
        model.convert_to_units(units_system())

    # check that the model tolerance is not too far from the Rhino tolerance
    if model.tolerance / tolerance >= 100:
        msg = 'Imported Model tolerance "{}" is significantly coarser than the ' \
            'current Rhino model tolerance "{}".\nIt is recommended that the ' \
            'Rhino document tolerance be changed to be coarser and this ' \
            'component is re-reun.'.format(new_tol, tolerance)
        give_warning(msg)


if all_required_inputs(ghenv.Component) and _load:
    with open(_df_file) as json_file:
        data = json.load(json_file)

    try:
        df_objs = df_dict_util.dict_to_object(data, False)  # re-serialize as a core object
        if df_objs is None:  # try to re-serialize it as an energy object
            df_objs = energy_dict_util.dict_to_object(hb_dict, False)
        elif isinstance(df_objs, Model):
            model_units_tolerance_check(df_objs)
    except ValueError:  # no 'type' key; assume that its a group of objects
        df_objs = []
        for hb_dict in data.values():
            df_obj = df_dict_util.dict_to_object(hb_dict, False)  # re-serialize as a core object
            if df_obj is None:  # try to re-serialize it as an energy object
                df_obj = energy_dict_util.dict_to_object(hb_dict, False)
            df_objs.append(df_obj)