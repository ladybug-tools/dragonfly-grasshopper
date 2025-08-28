# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run a Modelica District Energy System (DES) through an annual simulation using
OpenModelica inside a Docker image (via Docker Desktop).
_
Docker Dekstop can be downloaded at the following link:
https://www.docker.com/products/docker-desktop/
-

    Args:
        _modelica: A folder where all of the Modelica files of the District Energy
            System (DES) are written. These Modelica files can be created using
            the "DF Write Modelica DES" component.
        run_: Set to "True" to translate the Modelica files to a Functional Mockup
            Unit (FMU) and then simulate an annual simulation of the FMU
            with OpenModelica.

    Returns:
        report: Reports, errors, warnings, etc.
        results: A folder containing the results of the Modelica simulation.
"""

ghenv.Component.Name = 'DF Run Modelica'
ghenv.Component.NickName = 'RunModelica'
ghenv.Component.Message = '1.9.1'
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
    from dragonfly_energy.run import run_modelica_docker
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.download import download_file_by_name
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

UO_GMT_VERSION = '0.11.0'


if all_required_inputs(ghenv.Component) and _run:
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

    # execute the modelica files in URBANopt
    if df_folders.docker_version_str is not None:
        results = run_modelica_docker(_modelica)
    else:
        docker_url  = 'https://www.docker.com/products/docker-desktop/'
        msg = 'No Docker installation was found on this machine.\n' \
            'This is needed to execute Modelica simulations.\n' \
            'Download Docker Desktop from: {}'.format(docker_url)
        print(msg)
        give_warning(ghenv.Component, msg)
