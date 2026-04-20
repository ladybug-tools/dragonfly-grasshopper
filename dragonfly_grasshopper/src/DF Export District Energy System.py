# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Epxport an URBANopt GeoJSON with an assigned Distric Energy System (DES)
to an OSM file (OpenStudio Model), which can then be translated to an IDF file
and then simualted through EnergyPlus.
_
This component also exports a Modelica model of the DES, can be opened and
edited in any of the standard Modelica interfaces (eg. Dymola, OMEdit) or it
can be simulated with OpenModelica inside a Docker image using the "DF Run
Modelica" component.
_
The DES models exported by this component have no building geometry in them and
are purely models of the DES plant loops. Buildings are replaced by load
profile objects with cooling, heating, and service hot water loads pulled
from the input scenario.
_
The Modelica model uses the modules of the Modelica Buildings Library (MBL).
More information on the MBL can be found here:
https://simulationresearch.lbl.gov/modelica/
-

    Args:
        _geojson: The path to an URBANopt-compatible geoJSON file. This geoJSON
            file can be obtained form the "DF Model to geoJSON" component.
            Note that the geoJSON must have a valid District Energy System
            (DES) Loop assigned to it in order to run correctly with this
            component.
        _scenario: The path to an URBANopt .csv file for the scenario. This CSV
            file can be obtained form the "DF Run URBANopt" component.
        _sim_par_: Optional parameters from the "HB Simulation Parameter" component,
            which describes all of the setting for the simulation. If unspecified,
            default simulation parameters will be used.
        _write: Set to "True" to install any missing dependencies, perform autosizing
            of the DES, and export the DES to OSM/IDF files as well as a
            Modelica model.
        run_: Set to "True" to simulate the IDF of the DES in EnergyPlus after it is written.
            This will ensure that all result files appear in their respective
            outputs from this component.

    Returns:
        report: Reports, errors, warnings, etc.
        sys_param: A JSON file containing all of the specifications of the District
            Energy System, including the detailed Building load profiles,
            equipment specifications, borehole field characteristics
            (if applicable), etc.
        osm: The file path to the OpenStudio Model (OSM) that has been generated
            on this computer.
        idf: The file path of the EnergyPlus Input Data File (IDF) that has been
            generated on this computer.
        sql: The file path of the SQL result file that has been generated on this
            computer. This will be None unless run_ is set to True.
        rdd: The file path of the Result Data Dictionary (.rdd) file that is
            generated after running the file through EnergyPlus.  This file
            contains all possible outputs that can be requested from the EnergyPlus
            model. Use the "HB Read Result Dictionary" component to see what outputs
            can be requested.
        html: The HTML file path containing all requested Summary Reports.
        modelica: A folder where all of the Modelica files of the District Energy
            System (DES) are written.
"""

ghenv.Component.Name = 'DF Export District Energy System'
ghenv.Component.NickName = 'ExportDES'
ghenv.Component.Message = '1.10.2'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import subprocess
import json

try:
    from ladybug.futil import nukedir
    from ladybug.config import folders as lb_folders
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.run import output_energyplus_files
    from honeybee_energy.result.err import Err
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the dragonfly_energy dependencies
    from dragonfly_energy.config import folders as df_folders
    from dragonfly_energy.run import check_des_compatibility, set_building_district_loads, \
        run_des_sys_param, run_des_modelica
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.download import download_file_by_name
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

UO_GMT_VERSION = '.'.join(str(i) for i in df_folders.UO_GMT_VERSION)
UO_TN_VERSION = '.'.join(str(i) for i in df_folders.UO_TN_VERSION)
MBL_VERSION = '.'.join(str(i) for i in df_folders.MBL_VERSION)


if all_required_inputs(ghenv.Component) and _write:
    # set up the custom python environment
    custom_env = os.environ.copy()
    custom_env['PYTHONHOME'] = ''

    # set global values
    ext = '.exe' if os.name == 'nt' else ''
    executor_path = os.path.join(
        lb_folders.ladybug_tools_folder, 'grasshopper',
        'ladybug_grasshopper_dotnet', 'Ladybug.Executor.exe')

    # check to see if the geojson-modelica-translator is installed
    uo_gmt = '{}/uo_des{}'.format(folders.python_scripts_path, ext)
    uo_gmt_pack = '{}/geojson_modelica_translator-{}.dist-info'.format(
        folders.python_package_path, UO_GMT_VERSION)
    if not os.path.isfile(uo_gmt) or not os.path.isdir(uo_gmt_pack):
        install_cmd = 'pip install geojson-modelica-translator=={}'.format(UO_GMT_VERSION)
        if os.name == 'nt' and os.path.isfile(executor_path) and \
                'Program Files' in executor_path:
            pip_cmd = [
                executor_path, folders.python_exe_path, '-m {}'.format(install_cmd)
            ]
        else:
            pip_cmd = '"{py_exe}" -m {uo_cmd}'.format(
                py_exe=folders.python_exe_path, uo_cmd=install_cmd)
        shell = True if os.name == 'nt' else False
        process = subprocess.Popen(
            pip_cmd, stderr=subprocess.PIPE, shell=shell, env=custom_env)
        stderr = process.communicate()

    # check to see if the ThermalNetwork package is installed
    uo_tn = '{}/thermalnetwork{}'.format(folders.python_scripts_path, ext)
    uo_tn_pack = '{}/ThermalNetwork-{}.dist-info'.format(
        folders.python_package_path, UO_TN_VERSION)
    if not os.path.isfile(uo_tn) or not os.path.isdir(uo_tn_pack):
        install_cmd = 'pip install thermalnetwork=={}'.format(UO_TN_VERSION)
        if os.name == 'nt' and os.path.isfile(executor_path) and \
                'Program Files' in executor_path:
            pip_cmd = [
                executor_path, folders.python_exe_path, '-m {}'.format(install_cmd)
            ]
        else:
            pip_cmd = '"{py_exe}" -m {uo_cmd}'.format(
                py_exe=folders.python_exe_path, uo_cmd=install_cmd)
        shell = True if os.name == 'nt' else False
        process = subprocess.Popen(
            pip_cmd, stderr=subprocess.PIPE, shell=shell, env=custom_env)
        stderr = process.communicate()

    # check to see if the Modelica Buildings Library is installed
    install_directory = os.path.join(lb_folders.ladybug_tools_folder, 'resources')
    final_dir = os.path.join(install_directory, 'mbl')
    version_file = os.path.join(final_dir, 'version.txt')
    already_installed = False
    if os.path.isdir(final_dir) and os.path.isfile(version_file):
        with open(version_file, 'r') as vf:
            install_version = vf.read()
        if install_version == MBL_VERSION:
            already_installed = True
        else:
            nukedir(final_dir, True)
    if not already_installed:
        install_cmd = 'dragonfly_energy install mbl --version {}'.format(MBL_VERSION)
        if os.name == 'nt' and os.path.isfile(executor_path) and \
                'Program Files' in executor_path:
            pip_cmd = [
                executor_path, folders.python_exe_path, '-m {}'.format(install_cmd)
            ]
        else:
            pip_cmd = '"{py_exe}" -m {uo_cmd}'.format(
                py_exe=folders.python_exe_path, uo_cmd=install_cmd)
        shell = True if os.name == 'nt' else False
        process = subprocess.Popen(
            pip_cmd, stderr=subprocess.PIPE, shell=shell, env=custom_env)
        stderr = process.communicate()

    # check the various files in the project folder
    check_des_compatibility(_geojson)
    proj_dir = os.path.dirname(_geojson)
    scn_name = os.path.basename(_scenario).replace('.csv', '')
    des_dir = os.path.join(proj_dir, 'run', scn_name, 'des_modelica')
    sys_param = os.path.join(proj_dir, 'system_params.json')

    # add the building loads to the system parameters and autosize any GHEs
    if not os.path.isdir(des_dir):
        # set the building loads to district chilled/hot water
        if os.name == 'nt':
            warnings = set_building_district_loads(_geojson, _scenario)
        else:  # on Mac, the SQLite module does not work
            cmds = [folders.python_exe_path, '-m', 'dragonfly_energy', 'translate',
                    'building-district-loads', _geojson, _scenario]
            process = subprocess.Popen(cmds, stdout=subprocess.PIPE, env=custom_env)
            stdout = process.communicate()
            warnings = json.loads(stdout[0])
        for warn in warnings:
            give_warning(ghenv.Component, warn)
        # size the GHE
        sys_param = run_des_sys_param(_geojson, _scenario)

    # run the command that generates the modelica model
    modelica = run_des_modelica(sys_param, _geojson, _scenario)

    # translate the system to OSM/IDF and optionally simualte it
    ep_dir = os.path.join(proj_dir, 'run', 'honeybee_scenario', 'des_energyplus')
    nukedir(ep_dir, True)
    if not os.path.isdir(ep_dir):
        os.makedirs(ep_dir)
    osm = os.path.join(ep_dir, 'in.osm')
    idf = os.path.join(ep_dir, 'in.idf')
    # put together the arguments for the command to be run
    if run_:  # use the simulate command
        cmds = [
            '"{}"'.format(folders.python_exe_path), '-m', 'dragonfly_openstudio',
            'simulate', 'system', '"{}"'.format(sys_param),
            '--geojson', '"{}"'.format(_geojson),
            '--folder', '"{}"'.format(ep_dir)
        ]
    else:  # use the translate command
        cmds = [
            '"{}"'.format(folders.python_exe_path), '-m', 'dragonfly_openstudio',
            'translate', 'system-to-osm', '"{}"'.format(sys_param),
            '--geojson', '"{}"'.format(_geojson),
            '--osm-file', '"{}"'.format(osm), '--idf-file', '"{}"'.format(idf)
        ]
    if _sim_par_ is not None:
        sim_par_json = os.path.join(ep_dir, 'simulation_parameter.json')
        with open(sim_par_json, 'w') as fp:
            json.dump(_sim_par_.to_dict(), fp)
        cmds.append('--sim-par-json')
        cmds.append('"{}"'.format(sim_par_json))

    # execute the command
    cmds = ' '.join(cmds)
    if os.name == 'nt':
        shell = False if run_ == 1 else True
    else:
        shell = True
    process = subprocess.Popen(cmds, shell=shell, env=custom_env)
    result = process.communicate()  # freeze the canvas while running

    # get the output files and error log
    if run_:
        if not os.path.isfile(idf):
            print(cmds)
            raise ValueError('Failed to translate Model to EnergyPlus.')
        sql, zsz, rdd, html, err = output_energyplus_files(os.path.dirname(idf))
        # parse the error log and report any warnings
        if err is not None and os.path.getsize(err) < 500000000:
            err_obj = Err(err)
            err_content = err_obj.file_contents
            clean_contents = []
            for line in err_content.split('\n'):
                if 'Heat Transfer Pipe' not in line:  # remove recurring warning
                    clean_contents.append(line)
            print('\n'.join(clean_contents))
            for warn in err_obj.severe_errors:
                give_warning(ghenv.Component, warn)
            for error in err_obj.fatal_errors:
                raise Exception(error)
