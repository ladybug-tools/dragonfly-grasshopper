# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run a an URBANopt geoJSON and scenario through Modelica Distric Energy System
(DES) simulation.
_
The geoJSON must have a valid DES Loop assigned to it in order to run correctly
through Modelica DES simulation.
-

    Args:
        _geojson: The path to an URBANopt-compatible geoJSON file. This geoJSON
            file can be obtained form the "DF Model to geoJSON" component.
            The geoJSON must have a valid District Energy System (DES) Loop
            assigned to it in order to run correctly through the DES simulation.
        _scenario: The path to an URBANopt .csv file for the scenario. This CSV
            file can be obtained form the "DF Run URBANopt" component.
        _write: Set to "True" to run the component, install any missing dependencies,
            and write the Modelica files for the Distric Energy System.
        run_: Set to "True" to translate the Modelica files to a Functional Mockup Unit (FMU)
            and then simulate the FMU. This will ensure that all result files appear
            in their respective outputs from this component.

    Returns:
        report: Reports, errors, warnings, etc.
        sys_param: A JSON file containing all of the specifications of the District
            Energy System, including the detailed Building load profiles.
        modelica: A folder where all of the Modelica files of the District Energy
            System (DES) are written.
        results: A folder containing the results of the Modelica simulation if run_ is
            True and the simulation is successful.
"""

ghenv.Component.Name = 'DF Run Modelica DES'
ghenv.Component.NickName = 'RunDES'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import subprocess

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
    from dragonfly_energy.config import folders as df_folders
    from dragonfly_energy.run import run_des_sys_param, run_des_modelica, \
        run_modelica_docker
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.download import download_file_by_name
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

UO_GMT_VERSION = '0.6.0'
UO_TN_VERSION = '0.2.4'
MBL_VERSION = '10.0.0'


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

    # run the command that adds the building loads to the system parameters
    sys_param = run_des_sys_param(_geojson, _scenario)

    # run the command that generates the modelica files
    modelica = run_des_modelica(sys_param, _geojson, _scenario)

    # execute the modelica files in URBANopt
    if run_:
        if df_folders.docker_version_str is not None:
            results = run_modelica_docker(modelica)
        else:
            docker_url  = 'https://www.docker.com/products/docker-desktop/'
            msg = 'No Docker installation was found on this machine.\n' \
                'This is needed to execute Modelica simulations.\n' \
                'Download Docker Desktop from: {}'.format(docker_url)
            print(msg)
            give_warning(ghenv.Component, msg)
