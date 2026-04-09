# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Parse the plant loop temperature results for a District Energy System (DES).
-
    Args:
        _sql: The path of an SQL result file that has been generated from an
            EnergyPlus simulation with the "DF Export District Energy System"
            component.

    Returns:
        chilled_water: DataCollections for the temperature of chilled water of
            plant loops in C.
        hot_water: DataCollections for the temperature of hot water of plant
            loops in C.
        condenser: DataCollections for the temperature of condenser plant loops in C.
            This includes both traditional condenser loops that cool central
            chillers as well as fifth generation loops aimed at load sharing
            and ground heat exchange.
        ground: DataCollections for the temperature of Ground Heat Exchanger (GHE)
            boreholes in C. This also includes the "far field" ground
            temeprature with which the boreholes interact.
"""

ghenv.Component.Name = 'DF Read DES Temperature Result'
ghenv.Component.NickName = 'DESTemperatureResult'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

import os
import subprocess
import json

try:
    from ladybug.sql import SQLiteResult
    from ladybug.datacollection import HourlyContinuousCollection, \
        MonthlyCollection, DailyCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def serialize_data(data_dicts):
    """Reserialize a list of collection dictionaries."""
    if len(data_dicts) == 0:
        return []
    elif data_dicts[0]['type'] == 'HourlyContinuous':
        return [HourlyContinuousCollection.from_dict(data) for data in data_dicts]
    elif data_dicts[0]['type'] == 'Monthly':
        return [MonthlyCollection.from_dict(data) for data in data_dicts]
    elif data_dicts[0]['type'] == 'Daily':
        return [DailyCollection.from_dict(data) for data in data_dicts]


# List of all the output strings that will be requested
plant_outputs = 'Plant Supply Side Inlet Temperature'
ground_outputs = (
    'Ground Heat Exchanger Average Borehole Temperature',
    'Ground Heat Exchanger Farfield Ground Temperature'
)
all_output = [plant_outputs, ground_outputs]


if all_required_inputs(ghenv.Component):
    # check the size of the SQL file to see if we should use the CLI
    assert os.path.isfile(_sql), 'No sql file found at: {}.'.format(_sql)
    if os.name == 'nt' and os.path.getsize(_sql) < 1e8:
        # small file on windows; use IronPython like usual
        # create the SQL result parsing object
        sql_obj = SQLiteResult(_sql)

        # get all of the results relevant for energy use
        condenser = sql_obj.data_collections_by_output_name(plant_outputs)
        ground = sql_obj.data_collections_by_output_name(ground_outputs)

    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the results via CPython
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'data-by-outputs', _sql]
        for outp in all_output:
            out_str = json.dumps(outp) if isinstance(outp, tuple) else '["{}"]'.format(outp)
            cmds.append(out_str)
        use_shell = True if os.name == 'nt' else False
        custom_env = os.environ.copy()
        custom_env['PYTHONHOME'] = ''
        process = subprocess.Popen(
            cmds, stdout=subprocess.PIPE, shell=use_shell, env=custom_env)
        stdout = process.communicate()
        data_coll_dicts = json.loads(stdout[0])

        # get all of the results relevant for energy use
        condenser = serialize_data(data_coll_dicts[0])
        ground = serialize_data(data_coll_dicts[1])

    # spearate the plant loops into cooling, heating and condenser
    chilled_water, hot_water = [], []
    for i in range(len(condenser) - 1, -1, -1):
        if 'CHILLED WATER' in condenser[i].header.metadata['System']:
            chilled_water.append(condenser.pop(i))
        elif 'HEATING' in condenser[i].header.metadata['System'] or \
                'SHW' in condenser[i].header.metadata['System'] or \
                'HOT WATER' in condenser[i].header.metadata['System']:
            hot_water.append(condenser.pop(i))
    chilled_water = reversed(chilled_water)  # reverse to match other components
    hot_water = reversed(hot_water)  # reverse to match other components
