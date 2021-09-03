# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Serialize any dragonfly JSON text string back to a dragonfly object.
-
This includes any Model, Building, Story, Room2D, WindowParameter, or ShadingParameter.
-
It also includes any dragonfly energy Material, Construction, ConstructionSet,
Schedule, Load, ProgramType, or Simulation object.
-

    Args:
        _df_str: A text string that completely describes the dragonfly object.
    
    Returns:
        df_obj: A Dragonfly object serialized from the input string.
"""

ghenv.Component.Name = 'DF String to Object'
ghenv.Component.NickName = 'StrToObj'
ghenv.Component.Message = '1.3.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '2 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:  # import the core dragonfly dependencies
    import dragonfly.dictutil as df_dict_util
    from dragonfly.model import Model
    from dragonfly.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the core honeybee_energy dependencies
    import honeybee_energy.dictutil as energy_dict_util
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the core honeybee_radiance dependencies
    import honeybee_radiance.dictutil as radiance_dict_util
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
    from ladybug_rhino.config import units_system, tolerance
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import json


def model_units_tolerance_check(model):
    """Convert a model to the current Rhino units and check the tolerance.

    Args:
        model: A honeybee Model, which will have its units checked.
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
            'component is re-run.'.format(model.tolerance, tolerance)
        print msg
        give_warning(ghenv.Component, msg)


def version_check(data):
    """Check the version of the object if it was included in the dictionary.

    This is most useful in cases of importing entire Models to make sure
    the Model isn't newer than the currently installed Dragonfly.

    Args:
        data: Dictionary of the object, which optionally has the "version" key.
    """
    if 'version' in data and data['version'] is not None:
        model_ver = tuple(int(d) for d in data['version'].split('.'))
        df_ver = folders.dragonfly_schema_version
        if model_ver > df_ver:
            msg = 'Imported Model schema version "{}" is newer than that with the ' \
            'currently installed Dragonfly "{}".\nThe Model may fail to import ' \
            'or (worse) some newer features of the Model might not be imported ' \
            'without detection.'.format(data['version'], folders.dragonfly_schema_version_str)
            print msg
            give_warning(ghenv.Component, msg)
        elif model_ver != df_ver:
            msg = 'Imported Model schema version "{}" is older than that with the ' \
            'currently installed Dragonfly "{}".\nThe Model will be upgraded upon ' \
            'import.'.format(data['version'], folders.dragonfly_schema_version_str)
            print msg


if all_required_inputs(ghenv.Component):
    df_dict = json.loads(_df_str)
    version_check(df_dict)  # try to check the version
    df_obj = df_dict_util.dict_to_object(df_dict, False)  # re-serialize as a core object
    if df_obj is None:  # try to re-serialize it as an energy object
        df_obj = energy_dict_util.dict_to_object(df_dict, False)
        if df_obj is None:  # try to re-serialize it as a radiance object
            df_obj = radiance_dict_util.dict_to_object(df_dict, False)
    elif isinstance(df_obj, Model):
        model_units_tolerance_check(df_obj)
