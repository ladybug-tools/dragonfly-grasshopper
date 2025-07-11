# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Load any dragonfly object from a dragonfly JSON file
-
This includes any Model, Building, Story, Room2D, WindowParameter, or ShadingParameter.
-
It also includes any energy Material, Construction, ConstructionSet, Schedule, 
Load, ProgramType, or Simulation object.
-

    Args:
        _df_file: A file path to a dragonfly JSON (or DFJSON representing a full dragonfly
            Model) from which objects will be loaded into Grasshopper. This can
            also be the path to a Pollination Model Format (.POMF) file from which
            a dragonfly Model will be loaded. Note that, if the objects in the JSON
            are not a full model, they must be non-abridged in order to be
            loaded correctly.
        _load: Set to "True to load the objects from the _df_file.
    
    Returns:
        df_objs: A list of dragonfly objects that have been re-serialized from
            the input file.
"""

ghenv.Component.Name = 'DF Load Objects'
ghenv.Component.NickName = 'LoadObjects'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '2 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import os
import io
import zipfile
import tempfile
import uuid

try:  # import the core dragonfly dependencies
    import dragonfly.dictutil as df_dict_util
    from dragonfly.model import Model
    from dragonfly.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the dragonfly_energy dependencies
    from dragonfly_energy.opendss.network import ElectricalNetwork, RoadNetwork
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:  # import the core honeybee_energy dependencies
    import honeybee_energy.dictutil as energy_dict_util
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the core honeybee_radiance dependencies
    import honeybee_radiance.dictutil as radiance_dict_util
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug.futil import unzip_file
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
    from ladybug_rhino.config import units_system, tolerance
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import json


def df_energy_dict_to_object(df_energy_dict, raise_exception=True):
    """Re-serialize a dictionary of an object within dragonfly_energy.

    Args:
        df_energy_dict: A dictionary of a Dragonfly energy object. Note
            that this should be a non-abridged dictionary to be valid.
        raise_exception: Boolean to note whether an exception should be raised
            if the object is not identified as a part of dragonfly_energy.

    Returns:
        A Python object derived from the input df_energy_dict.
    """
    try:  # get the type key from the dictionary
        obj_type = df_energy_dict['type']
    except KeyError:
        raise ValueError('Dragonfly_energy dictionary lacks required "type" key.')

    if obj_type == 'ElectricalNetwork':
        return ElectricalNetwork.from_dict(df_energy_dict)
    elif obj_type == 'RoadNetwork':
        return RoadNetwork.from_dict(df_energy_dict)
    elif raise_exception:
        raise ValueError(
            '{} is not a recognized dragonfly energy object'.format(obj_type)
        )


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
            'component is re-reun.'.format(model.tolerance, tolerance)
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


if all_required_inputs(ghenv.Component) and _load:
    # first, check whether the file is a Pollination Model Format (.POMF) file
    if zipfile.is_zipfile(_df_file):
        folder_name = str(uuid.uuid4())[:6]
        temp_dir = tempfile.gettempdir()
        folder_path = os.path.join(temp_dir, folder_name)
        os.mkdir(folder_path)
        unzip_file(_df_file, folder_path)
        _df_file = os.path.join(folder_path, 'model.json')

    # then
    with io.open(_df_file, encoding='utf-8') as inf:
        first_char = inf.read(1)
        second_char = inf.read(1)
    with io.open(_df_file, encoding='utf-8') as inf:
        if second_char == '{':
            inf.read(1)
        data = json.load(inf)

    version_check(data)  # try to check the version
    if 'type' in data:
        df_objs = df_dict_util.dict_to_object(data, False)  # re-serialize as a core object
        if df_objs is None:  # try to re-serialize it as an energy object
            df_objs = df_energy_dict_to_object(data, False)
            if df_objs is None:
                df_objs = energy_dict_util.dict_to_object(data, False)
                if df_objs is None:  # try to re-serialize it as a radiance object
                    df_objs = radiance_dict_util.dict_to_object(data, False)
        elif isinstance(df_objs, Model):
            model_units_tolerance_check(df_objs)
    else:  # no 'type' key; assume that its a group of objects
        df_objs = []
        for df_dict in data.values():
            df_obj = df_dict_util.dict_to_object(df_dict, False)  # re-serialize as a core object
            if df_obj is None:  # try to re-serialize it as an energy object
                df_objs = df_energy_dict_to_object(data, False)
                if df_obj is None:
                    df_obj = energy_dict_util.dict_to_object(df_dict, False)
                    if df_obj is None:  # try to re-serialize it as a radiance object
                        df_obj = radiance_dict_util.dict_to_object(df_dict, False)
            df_objs.append(df_obj)