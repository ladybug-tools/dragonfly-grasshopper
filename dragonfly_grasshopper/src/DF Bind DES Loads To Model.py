# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Bind the cooling, heating and hot water loads derived from an URBANopt simulation
to the Buildings of a dragonfly Model.
_
Doing so avoids the need to re-run the URBANopt/EnergyPlus simulation of the
building loads as different District Energy Systems (DES) are assigned and run.
For this workflow, the model and any customized des_loop can be re-exported using
the "DF Model To DES" component and then the plant can be simulated with the
"DF Export District Energy System" component.
_
Binding the loads also means that the cooling, heating and hot water values are
saved within the dragonfly Model if it is written to a DFJSON and opened in another
software interface.
-

    Args:
        _model: A Dragonfly Model which has been simulated with the "DF Run URBANopt"
            component and is to have the resulting heating and cooling loads
            bound to it for simulation of a District Energy System (DES).
        _scenario: The path to the URBANopt .csv file for the scenario. This CSV
            file can be obtained form the "DF Run URBANopt" component.

    Returns:
        model: The input Dragonfly Model with DES loads assigned to it. The Model
             and any customized des_loop can be exported using the "DF Model To DES"
             component and then the plant can be simulated with the "DF Export
             District Energy System" component.
"""

ghenv.Component.Name = 'DF Bind DES Loads To Model'
ghenv.Component.NickName = 'BindDESLoads'
ghenv.Component.Message = '1.10.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os
import subprocess
import json

try:
    from ladybug.datacollection import HourlyContinuousCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import ladybug-rhino
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the input model
    assert isinstance(_model, Model), 'Expected Dragonfly Model. ' \
        'Got {}.'.format(type(_model))
    model = _model.duplicate()

    # get the building loads
    if os.name == 'nt':  # we are on windows; use IronPython like usual
        warnings = model.properties.energy.bind_des_loads_to_buildings(_scenario)

    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the results via CPython
        cmds = [folders.python_exe_path, '-m', 'dragonfly_energy', 'translate',
                'building-district-loads', _scenario, '--loads-to-log']
        custom_env = os.environ.copy()
        custom_env['PYTHONHOME'] = ''
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, env=custom_env)
        stdout = process.communicate()
        res_dict = json.loads(stdout[0])
        warnings = res_dict['warnings']
        building_loads = res_dict['building_loads']
        for building in model.buildings:
            try:
                bldg_dict = building_loads[building.identifier]
                building.properties.energy.des_cooling_load = \
                    -HourlyContinuousCollection.from_dict(bldg_dict['cooling'])
                building.properties.energy.des_heating_load = \
                    HourlyContinuousCollection.from_dict(bldg_dict['heating'])
                building.properties.energy.des_hot_water_load = \
                    HourlyContinuousCollection.from_dict(bldg_dict['shw'])
            except KeyError:
                pass  # not a building where loads were found

    # output any warnings
    for warn in warnings:
        give_warning(ghenv.Component, warn)
