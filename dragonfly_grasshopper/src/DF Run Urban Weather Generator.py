# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Morph a rural or airport EPW to reflect the conditions within an urban street canyon.
The properties of this urban street canyon are specified in the connected _model.
_
For definitions of the inputs of the Urban Weather Generator, please see the UWG
schema documentation (https://www.ladybug.tools/uwg-schema/index.html).
_
For a full list of publications on the Urban Weather Generator, see the MIT Urban
Microclimate Group (http://urbanmicroclimate.scripts.mit.edu/publications.php).
-

    Args:
        _model: A Dragonfly Model to be used to morph the EPW for the urban area.
        _epw_file: Full path to an .epw file. This is the rural or airport file that
            will be morphed to reflect the climate conditions within an urban canyon.
        _run_period_: A Ladybug Analysis Period object to describe the time period over
            which to run the simulation. If None, the simulation will be run for
            the whole year.
        _veg_par_: A VegetationParameter object to specify the behavior of vegetation
            in the urban area. If None, generic vegetation parameters will be
            generated.
        _epw_site_: A ReferenceEPWSite object to specify the properties of the
            reference site where the input rural EPW was recorded. If None,
            generic airport properties will be generated.
        _bnd_layer_: A BoundaryLayerParameter to specify the properties of the urban
            boundary layer. If None, generic boundary layer parameters will
            be generated.
        _folder_: File path for the directory into which the the uwg JSON and morphed
            urban EPW will be written. If None, it will be written into the
            ladybug default_epw_folder within a subfolder bearing the name
            of the dragonfly Model.
        _write: Set to "True" to generate a UWG JSON from the connected _model and
            parameters. This JSON can be edited and simulated by the UWG directly.
        run_: Set to "True" to simulate the uwg_json with the Urban Weather Generator
            (UWG) and morph the input EPW to account for urban heat island. This
            can also be the integer "2", which will run the UWG silently (without
            any batch windows).

    Returns:
        report: Reports, errors, warnings, etc.
        uwg_json: Path to a fully-simulatable JSON file following the UWG schema.
            This contains all of the relevant Dragonfly Model properties and
            input parameters.
        urban_epw: Path to the morphed EPW file output from the UWG, which represents
            urban heat island conditions within the street canyon.
"""

ghenv.Component.Name = 'DF Run Urban Weather Generator'
ghenv.Component.NickName = 'RunUWG'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import json

try:  # import the core ladybug dependencies
    from ladybug.config import folders as lb_folders
    from ladybug.futil import preparedir
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the dragonfly uwg dependencies
    from dragonfly_uwg.simulation.runperiod import UWGRunPeriod
    from dragonfly_uwg.simulation.parameter import UWGSimulationParameter
    from dragonfly_uwg.run import run_uwg
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_uwg:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _write:
    # create the UWGSimulationParameter and assign all properties to it
    sim_par = UWGSimulationParameter()
    if _run_period_:
        sim_par.run_period = UWGRunPeriod.from_analysis_period(_run_period_)
    if _veg_par_:
        sim_par.vegetation_parameter = _veg_par_
    if _epw_site_:
        sim_par.reference_epw_site = _epw_site_
    if _bnd_layer_:
        sim_par.boundary_layer_parameter = _bnd_layer_

    if run_ is not None and run_ > 0:  # write and simulate the UWG JSON
        silent = True if run_ > 1 else False
        uwg_json, urban_epw = run_uwg(_model, _epw_file, sim_par, _folder_, silent)
        if urban_epw is None:
            msg = 'The Urban Weather Generator Failed to run.'
            print(msg)
            give_warning(ghenv.Component, msg)
    else:  # only write the UWG JSON but don't run it
        # get the directory into which the urban epw will be written
        if _folder_ is None:
            _folder_ = os.path.join(lb_folders.default_epw_folder, _model.identifier)
        preparedir(_folder_, remove_content=False)
        # write the model to a UWG dictionary
        uwg_dict = _model.to.uwg(_model, _epw_file, sim_par)
        uwg_json = os.path.join(_folder_, '{}_uwg.json'.format(_model.identifier))
        with open(uwg_json, 'w') as fp:
            json.dump(uwg_dict, fp, indent=4)
