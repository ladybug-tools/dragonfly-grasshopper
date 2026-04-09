# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Parse the thermal load of cooling, heating, and service hot water demand for
buildings in a District Energy System (DES) simulation.
-
    Args:
        _sql: The path of an SQL result file that has been generated from an
            EnergyPlus simulation with the "DF Export District Energy System"
            component. These can also be the SQL result files output from the
            "DF Run URBANopt" component to understand the building loads that
            will be input to DES models.

    Returns:
        cooling: DataCollections for the building cooling demand in kW.
        heating: DataCollections for the building heating demand use in kW.
        shw: DataCollections for the service hot water demand use in kW.
"""

ghenv.Component.Name = 'DF Read DES Building Load'
ghenv.Component.NickName = 'DESLoadResult'
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
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
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


def get_outputs(output_names):
    # check the size of the SQL file to see if we should use the CLI
    assert os.path.isfile(_sql), 'No sql file found at: {}.'.format(_sql)
    if os.name == 'nt' and os.path.getsize(_sql) < 1e8:
        # small file on windows; use IronPython like usual
        # create the SQL result parsing object
        sql_obj = SQLiteResult(_sql)
        results = []
        for out_name in output_names:
            results.append(sql_obj.data_collections_by_output_name(out_name))
        return results
    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the results via CPython
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'data-by-outputs', _sql]
        for outp in output_names:
            out_str = json.dumps(outp) if isinstance(outp, tuple) else '["{}"]'.format(outp)
            cmds.append(out_str)
        use_shell = True if os.name == 'nt' else False
        custom_env = os.environ.copy()
        custom_env['PYTHONHOME'] = ''
        process = subprocess.Popen(
            cmds, stdout=subprocess.PIPE, shell=use_shell, env=custom_env)
        stdout = process.communicate()
        data_coll_dicts = json.loads(stdout[0])
        return [serialize_data(dat) for dat in data_coll_dicts]


# List of all the output strings that will be requested
demand_output = 'Plant Load Profile Heat Transfer Rate'
cooling_output = 'District Cooling Water Rate'
heating_output = 'District Heating Water Rate'
shw_output = 'Water Heater DistrictHeatingWater Rate'
all_output = [demand_output, cooling_output, heating_output, shw_output]
# list of backup outputs to be used when no district heating/cooling is found
sensible_output = 'Zone Predicted Sensible Load to Setpoint Heat Transfer Rate'
sens_shw_output = 'Water Heater Total Demand Heat Transfer Rate'
backup_output = [sensible_output, sens_shw_output]
# template message to be used when no district objects were found
MSG_TEMPLATE = 'No District {} outputs were found in the SQL.\nZone sensible ' \
    'loads will be used instead but this misses ventilation air loads.\nFor best ' \
    'results, assign {} systems to buildings that use {}.'


if all_required_inputs(ghenv.Component):
    # start by looking for specific district heating/cooling loads
    demand, cooling, heating, shw = get_outputs(all_output)

    # orgnaize the generic demand lists
    for load in demand:
        sys_id = load.header.metadata['System']
        if sys_id.endswith('COOLING LOAD'):
            load.values = tuple(abs(v) for v in load.values)
            cooling.append(load)
        elif sys_id.endswith('HEATING LOAD'):
            heating.append(load)
        elif sys_id.endswith('SHW LOAD'):
            shw.append(load)

    # if district heating/cooling outputs were not found, use sensible loads
    backup_demand, backup_shw = [], []
    if len(demand) == 0 and (len(cooling) == 0 or len(heating) == 0 or len(shw) == 0):
        backup_demand, backup_shw = get_outputs(backup_output)

    # use sensible cooling load if there is no district cooling
    if len(cooling) == 0 and len(backup_demand) != 0:
        cool_vals = [0] * len(backup_demand[0])
        for demand in backup_demand:
            for i, v in enumerate(demand):
                if v < 0:
                    cool_vals[i] += abs(v)
        sens_cool = backup_demand[0].duplicate()
        sens_cool.values = cool_vals
        sens_cool.header.metadata['System'] = 'Building Total'
        cooling.append(sens_cool)
        msg = MSG_TEMPLATE.format('Cooling', 'HVAC', 'District Chilled Water')
        give_warning(ghenv.Component, msg)

    # use sensible heating load if there is no district heating
    if len(heating) == 0 and len(backup_demand) != 0:
        heat_vals = [0] * len(backup_demand[0])
        for demand in backup_demand:
            for i, v in enumerate(demand):
                if v > 0:
                    heat_vals[i] += v
        sens_heat = backup_demand[0].duplicate()
        sens_heat.values = heat_vals
        sens_heat.header.metadata['System'] = 'Building Total'
        heating.append(sens_heat)
        msg = MSG_TEMPLATE.format('Heaating', 'HVAC', 'District Hot Water')
        give_warning(ghenv.Component, msg)

    # use sensible service hot water load if there is no district hot water
    if len(shw) == 0 and len(backup_shw) != 0:
        heat_vals = [0] * len(backup_shw[0])
        sens_shw = backup_shw[0].duplicate()
        for demand in backup_shw[1:]:
            sens_shw += demand
        # sens_heat.header.metadata['System'] = 'Building Total'
        shw.append(sens_shw)
        msg = MSG_TEMPLATE.format('Heaating', 'SHW', 'the default District Hot Water')
        give_warning(ghenv.Component, msg)

    # convert everything to kiloWatts before output
    for load_type in (cooling, heating, shw):
        for load in load_type:
            load.convert_to_unit('kW')
