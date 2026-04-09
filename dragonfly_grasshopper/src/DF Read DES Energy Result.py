# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Parse the typical energy use results for a District Energy System (DES).
-
    Args:
        _sql: The path of an SQL result file that has been generated from an
            EnergyPlus simulation with the "DF Export District Energy System"
            component.

    Returns:
        cooling: DataCollections for the cooling energy use in kWh.
        heating: DataCollections for the heating energy use in kWh.
        shw: DataCollections for the service hot water energy use in kWh.
        pumps: DataCollections for the water pump electric energy in kWh for all
            plant loops.
        heat_rejection: DataCollections for the fan electric energy of heat rejection
            systems in kWh.
"""

ghenv.Component.Name = 'DF Read DES Energy Result'
ghenv.Component.NickName = 'DESEnergyResult'
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
cooling_outputs = (
    'Heat Pump Electricity Energy',
    'Chiller Electricity Energy'
)
heating_outputs = (
    'Boiler Electricity Energy',
    'Boiler NaturalGas Energy',
    'Hot_Water_Loop_Central_Air_Source_Heat_Pump Electricity Consumption',
    'Water Heater NaturalGas Energy',
    'Water Heater Electricity Energy'
)
heat_rejection_outputs = (
    'Fan Electricity Energy',
    'Cooling Tower Fan Electricity Energy'
)
pump_electric_outputs = 'Pump Electricity Energy'
all_output = [cooling_outputs, heating_outputs, pump_electric_outputs, heat_rejection_outputs]


if all_required_inputs(ghenv.Component):
    # check the size of the SQL file to see if we should use the CLI
    assert os.path.isfile(_sql), 'No sql file found at: {}.'.format(_sql)
    if os.name == 'nt' and os.path.getsize(_sql) < 1e8:
        # small file on windows; use IronPython like usual
        # create the SQL result parsing object
        sql_obj = SQLiteResult(_sql)

        # get all of the results relevant for energy use
        cooling = sql_obj.data_collections_by_output_name(cooling_outputs)
        heating = sql_obj.data_collections_by_output_name(heating_outputs)
        pumps = sql_obj.data_collections_by_output_name(pump_electric_outputs)
        heat_rejection = sql_obj.data_collections_by_output_name(heat_rejection_outputs)

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
        cooling = serialize_data(data_coll_dicts[0])
        heating = serialize_data(data_coll_dicts[1])
        pumps = serialize_data(data_coll_dicts[2])
        heat_rejection = serialize_data(data_coll_dicts[3])

    # spearate supplemental heating into its correct list
    supplement_heat = []
    for i in range(len(heating) - 1, -1, -1):
        if 'SUPPLEMENTAL' in heating[i].header.metadata['System']:
            supplement_heat.append(heating.pop(i))

    # spearate any heating heat pump values into their correct lists
    shw = []
    for i in range(len(cooling) - 1, -1, -1):
        sys_id = cooling[i].header.metadata['System']
        if sys_id.endswith('HEATING HEAT PUMP'):
            heating.append(cooling.pop(i))
        elif sys_id.endswith('SHW HEAT PUMP'):
            shw.append(cooling.pop(i))
    heating = reversed(heating)  # reverse to match the cooling list
    shw = reversed(shw)  # reverse to match the cooling list
