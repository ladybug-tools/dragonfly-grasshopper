# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run a an URBANopt geoJSON and scenario through OpenDSS.
_
The geoJSON must have a valid Electrical Network assigned to it in order to
run correctly through OpenDSS.
-

    Args:
        _geojson: The path to an URBANopt-compatible geoJSON file. This geoJSON
            file can be obtained form the "DF Model to geoJSON" component.
            The geoJSON must have a valid Electrical Network assigned to it
            in order to run correctly through OpenDSS.
        _scenario: The path to an URBANopt .csv file for the scenario. This CSV
            file can be obtained form the "DF Run URBANopt" component.
        _run_period_: A ladybyg AnalysisPeriod object to describe the time period
            over which to run the simulation. The default is to run the simulation
            for the whole EnergyPlus run period.
        _run: Set to "True" to run the geojson and scenario through OpenDSS.

    Returns:
        report: Reports, errors, warnings, etc.
        buildings: A list of CSV files containing the voltage and over/under voltage
            results of the simulation at each timestep. There is one CSV per
            building in the dragonfly model. These can be imported with the
            "DF Read OpenDSS Result" component.
        connectors: A list of CSV result files containing the power line loading and
            overloading results of the simulation at each timestep.
            There is one CSV per electrical connector in the network. These can
            be imported with the "DF Read OpenDSS Result" component.
        transformers: A list of CSV result files containing the transformer loading and
            overloading results of the simulation at each timestep.
            There is one CSV per transformer in the network. These can be
            imported with the "DF Read OpenDSS Result" component.
"""

ghenv.Component.Name = 'DF Run OpenDSS'
ghenv.Component.NickName = 'RunOpenDSS'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os
import subprocess
import json

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the dragonfly_energy dependencies
    from dragonfly_energy.run import run_default_report
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.download import download_file_by_name
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # check to see if the urbanopt-ditto-reader is installed
    shell = False if os.name == 'nt' else True
    ext = '.exe' if os.name == 'nt' else ''
    uo_ditto = '{}/ditto_reader_cli{}'.format(folders.python_scripts_path, ext)
    if not os.path.isfile(uo_ditto):  # run the pip install command
        pip_cmd = '"{py_exe}" -m pip install urbanopt-ditto-reader==0.3.8'.format(
            py_exe=folders.python_exe_path)
        process = subprocess.Popen(pip_cmd, stderr=subprocess.PIPE, shell=shell)
        stderr = process.communicate()

    # generate the default scenario report
    run_default_report(_geojson, _scenario)

    # prepare the opendss-running command
    command = '"{uo_ditto}" run-opendss -f "{feature_file}" ' \
        '-s "{scenario_file}" -e "{equipment_file}"'.format(
            uo_ditto=uo_ditto, feature_file=_geojson, scenario_file=_scenario,
            equipment_file=os.path.join(os.path.dirname(_geojson), 'electrical_database.json')
        )
    if _run_period_ is not None:
        st_dt = '2006/{}'.format(_run_period_.st_time.strftime('%m/%d %H:%M:%S'))
        end_dt = '2006/{}'.format(_run_period_.end_time.strftime('%m/%d %H:%M:%S'))
        command = '{} -b "{}" -n "{}"'.format(command, st_dt, end_dt)

    # execute the command to run everything through OpenDSS
    process = subprocess.Popen(command, stderr=subprocess.PIPE, shell=shell)
    stderr = process.communicate()

    # gather together all of the result files
    scen_name = os.path.basename(_scenario).replace('.csv', '')
    run_folder = os.path.join(os.path.dirname(_geojson), 'run', scen_name)
    result_folder = os.path.join(run_folder, 'opendss')
    bldg_folder = os.path.join(result_folder, 'results', 'Features')
    conn_folder = os.path.join(result_folder, 'results', 'Lines')
    trans_folder = os.path.join(result_folder, 'results', 'Transformers')
    if os.path.isdir(bldg_folder):
        buildings = [os.path.join(bldg_folder, file) for file in os.listdir(bldg_folder)]
        connectors = [os.path.join(conn_folder, file) for file in os.listdir(conn_folder)]
        transformers = [os.path.join(trans_folder, file) for file in os.listdir(trans_folder)]
