# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
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
        autosize_: A boolean to note whether undersized transformers should be
            automatically resized to meet demand over the course of
            the simulation. (Default: False).
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
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: Electric Grid'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import subprocess
import json

try:
    from ladybug.futil import nukedir
    from ladybug.config import folders as lb_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

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

UO_DITTO_VERSION = '0.5.1'
DITTO_VERSION = '0.2.3'
TRAITLETS_VERSION = '5.9.0'


if all_required_inputs(ghenv.Component) and _run:
    # set up the custom python environment
    custom_env = os.environ.copy()
    custom_env['PYTHONHOME'] = ''
    ext = '.exe' if os.name == 'nt' else ''
    shell = True if os.name == 'nt' else False
    executor_path = os.path.join(
        lb_folders.ladybug_tools_folder, 'grasshopper',
        'ladybug_grasshopper_dotnet', 'Ladybug.Executor.exe')

    # check to see if the urbanopt-ditto-reader is installed
    uo_ditto = '{}/ditto_reader_cli{}'.format(folders.python_scripts_path, ext)
    uo_ditto_pack = '{}/urbanopt_ditto_reader-{}.dist-info'.format(
        folders.python_package_path, UO_DITTO_VERSION)
    if not os.path.isfile(uo_ditto) or not os.path.isdir(uo_ditto_pack):
        if os.name == 'nt' and os.path.isfile(executor_path) and \
                'Program Files' in executor_path:
            pip_cmd = [
                executor_path, folders.python_exe_path,
                '-m pip install urbanopt-ditto-reader=={}'.format(UO_DITTO_VERSION)
            ]
        else:
            pip_cmd = '"{py_exe}" -m pip install urbanopt-ditto-reader=={uo_ver}'.format(
                py_exe=folders.python_exe_path, uo_ver=UO_DITTO_VERSION)
        process = subprocess.Popen(
            pip_cmd, stderr=subprocess.PIPE, shell=shell, env=custom_env)
        stderr = process.communicate()

    # make sure that a compatible version of ditto is installed
    ditto_pack = '{}/ditto.py-{}.dist-info'.format(folders.python_package_path, DITTO_VERSION)
    if not os.path.isdir(uo_ditto_pack):
        if os.name == 'nt' and os.path.isfile(executor_path) and \
                'Program Files' in executor_path:
            pip_cmd = [
                executor_path, folders.python_exe_path,
                '-m pip install ditto.py=={}'.format(DITTO_VERSION)
            ]
        else:
            pip_cmd = '"{py_exe}" -m pip install ditto.py=={d_ver}'.format(
                py_exe=folders.python_exe_path, d_ver=DITTO_VERSION)
        process = subprocess.Popen(
            pip_cmd, stderr=subprocess.PIPE, shell=shell, env=custom_env)
        stderr = process.communicate()

    # install the old version of traitlets because Ditto didn't specify versions
    traitlets_pack = '{}/traitlets-{}.dist-info'.format(
        folders.python_package_path, TRAITLETS_VERSION)
    if not os.path.isdir(traitlets_pack):
        if os.name == 'nt' and os.path.isfile(executor_path) and \
                'Program Files' in executor_path:
            pip_cmd = [
                executor_path, folders.python_exe_path,
                '-m pip install traitlets=={}'.format(TRAITLETS_VERSION)
            ]
        else:
            pip_cmd = '"{py_exe}" -m pip install traitlets=={tr_ver}'.format(
                py_exe=folders.python_exe_path, tr_ver=TRAITLETS_VERSION)
        process = subprocess.Popen(
        pip_cmd, stderr=subprocess.PIPE, shell=shell, env=custom_env)
        stderr = process.communicate()

    # generate the default scenario report
    def_report = os.path.join(os.path.dirname(_geojson), 'run',
                              'honeybee_scenario', 'default_scenario_report.csv')
    if not os.path.isfile(def_report):
        run_default_report(_geojson, _scenario)

    # delete any existing files in the result folder
    scen_name = os.path.basename(_scenario).replace('.csv', '')
    run_folder = os.path.join(os.path.dirname(_geojson), 'run', scen_name)
    result_folder = os.path.join(run_folder, 'opendss')
    nukedir(result_folder)

    # prepare the opendss-running command
    command = '"{uo_ditto}" run-opendss -f "{feature_file}" ' \
        '-s "{scenario_file}"'.format(
            uo_ditto=uo_ditto, feature_file=_geojson, scenario_file=_scenario)

    # check if this is an RNM simulation
    rnm_results = os.path.join(
        os.path.dirname(_geojson), 'run', 'honeybee_scenario', 'rnm-us',
        'results', 'GeoJSON', 'Distribution_system.json')
    if os.path.isfile(rnm_results):
        command = '{} --rnm'.format(command)
    else:  # include the equipment file written by dragonfly-energy
        command = '{} -e "{}"'.format(
            command, os.path.join(os.path.dirname(_geojson), 'electrical_database.json'))

    # add the other options into the command
    # try to sense the timestep from the simulation parameter file
    timestep = 6  # assume the default timestep in case no file is found
    sim_par_json = os.path.join(os.path.dirname(_geojson), 'simulation_parameter.json')
    if os.path.isfile(sim_par_json):
        with open(sim_par_json, 'r') as spj:
            sim_par = json.load(spj)
        if 'timestep' in sim_par:
            timestep = sim_par['timestep']
    command = '{} --timestep {}'.format(command, int(60 / timestep))
    if _run_period_ is not None:
        # first, format the run period dates for the command
        st_dt = '2006/{}'.format(_run_period_.st_time.strftime('%m/%d'))
        end_dt = '2006/{}'.format(_run_period_.end_time.add_hour(24).strftime('%m/%d'))
        command = '{} -a "{}" -n "{}"'.format(command, st_dt, end_dt)
        
        # using the simulation timestep, specify the correct start and end time
        if timestep == 1:
            command = '{} -b 01:00:00 -d 00:00:00'.format(command)
        else:
            st_min = str(int(60 / timestep))
            st_min = '0{}'.format(st_min) if len(st_min) == 1 else st_min
            command = '{} -b 00:{}:00 -d 00:00:00'.format(command, st_min)
    if autosize_:
        command = '{} --upgrade'.format(command)

    # execute the command to run everything through OpenDSS
    shell = False if os.name == 'nt' else True
    process = subprocess.Popen(
        command, stderr=subprocess.PIPE, shell=shell, env=custom_env)
    stderr = process.communicate()

    # gather together all of the result files
    bldg_folder = os.path.join(result_folder, 'results', 'Features')
    conn_folder = os.path.join(result_folder, 'results', 'Lines')
    trans_folder = os.path.join(result_folder, 'results', 'Transformers')
    if os.path.isdir(bldg_folder):
        buildings = [os.path.join(bldg_folder, file) for file in os.listdir(bldg_folder)]
        connectors = [os.path.join(conn_folder, file) for file in os.listdir(conn_folder)]
        transformers = [os.path.join(trans_folder, file) for file in os.listdir(trans_folder)]
    else:
        msg = 'Failed to run the OpenDSS simulation.\nMake sure that your ' \
            'GeoJSON has an Electrical Network object in it\nor, if the GeoJSON has '\
            'a Road Network object in it, the "Run RNM" component\ncan be used to ' \
            'generate an Electrical Network that can be simulated in OpenDSS.\n{}'.format(
                stderr[1])
        raise ValueError(msg)
