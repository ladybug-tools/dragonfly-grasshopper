# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Run a an URBANopt geoJSON and scenario through OpenDSS.
_
The geoJSON must have a valid Electrical Network assigned to it in order to
run correctly through OpenDSS.
_
This component also requires the urbanopt-ditto-reader to be installed.
The urbanopt-ditto-reader can be installed by installing Python 3.7 and then
running the following from command line;
_
pip install git+https://github.com/urbanopt/urbanopt-ditto-reader
-

    Args:
        _geojson: The path to an URBANopt-compatible geoJSON file. This geoJSON
            file can be obtained form the "DF Model to geoJSON" component.
            The geoJSON must have a valid Electrical Network assigned to it
            in order to run correctly through OpenDSS.
        _scenario: The path to an URBANopt .csv file for the scenario. This CSV
            file can be obtained form the "DF Run URBANopt" component.
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
ghenv.Component.Message = '1.1.4'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os
import subprocess
import json

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
    # download the files that execute the translation
    uod_url = 'https://github.com/chriswmackey/urbanopt-ditto-reader/raw/consistency/'
    project_folder = os.path.dirname(_geojson)
    deps_folder = os.path.join(project_folder, 'deps_opendss')
    reader = 'urbanopt_ditto_reader.py'
    converter = 'convert.py'
    read = 'read.py'
    download_file_by_name(uod_url + reader, deps_folder, reader, True)
    download_file_by_name(uod_url + converter, deps_folder, converter, True)
    download_file_by_name(
        uod_url + 'reader/' + read, os.path.join(deps_folder, 'reader'), read, True)

    # get the path to the ditto folder
    assert os.name == 'nt', 'Dragonfly OpenDSS workflows are currently windows-only'
    home_folder = os.getenv('HOME') or os.path.expanduser('~')
    python_folder = os.path.join(
        home_folder, 'AppData', 'Local', 'Programs', 'Python', 'Python37', 
        'Lib', 'site-packages')
    ditto_folder = os.path.join(python_folder, 'ditto')
    assert os.path.isdir(ditto_folder), 'Ditto is not currently installed. Use:\n' \
        'pip install git+https://github.com/urbanopt/urbanopt-ditto-reader'

    # write out a config file
    scen_name = os.path.basename(_scenario).replace('.csv', '')
    run_folder = os.path.join(project_folder, 'run', scen_name)
    result_folder = os.path.join(run_folder, 'opendss')
    if not os.path.isdir(result_folder):
        os.mkdir(result_folder)
    config_dict = {
        'urbanopt_scenario': run_folder,
        'equipment_file': os.path.join(project_folder, 'electrical_database.json'),
        'opendss_folder': result_folder,
        'geojson_file': _geojson,
        'ditto_folder': ditto_folder,
        'use_reopt': False
    }
    config_json = os.path.join(deps_folder, 'config.json')
    with open(config_json, 'w') as fp:
        json.dump(config_dict, fp, indent=4)

    # generate the default scenario report
    run_default_report(_geojson, _scenario)

    # execute the Pyhon script to run everything through OpenDSS
    cmds = ['python', os.path.join(deps_folder, converter), config_json]
    process = subprocess.Popen(cmds, stderr=subprocess.PIPE)
    stderr = process.communicate()

    # gather together all of the result files
    bldg_folder = os.path.join(result_folder, 'results', 'Features')
    conn_folder = os.path.join(result_folder, 'results', 'Lines')
    trans_folder = os.path.join(result_folder, 'results', 'Transformers')
    if os.path.isdir(bldg_folder):
        buildings = [os.path.join(bldg_folder, file) for file in os.listdir(bldg_folder)]
        connectors = [os.path.join(conn_folder, file) for file in os.listdir(conn_folder)]
        transformers = [os.path.join(trans_folder, file) for file in os.listdir(trans_folder)]
