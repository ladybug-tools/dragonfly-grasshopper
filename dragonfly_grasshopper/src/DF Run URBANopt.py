# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run an URBANopt geoJSON through EnergyPlus using the URBANopt CLI.
_
This component requires the URBANopt CLI to be installed in order to run.
Installation instructions for the URBANopt CLI can be found at:
https://docs.urbanopt.net/installation/installation.html
-

    Args:
        _geojson: The path to an URBANopt-compatible geoJSON file. This geoJSON
            file can be obtained form the "DF Model to geoJSON" component.
        _epw_file: Path to an .epw file on this computer as a text string.
        _sim_par_: A honeybee Energy SimulationParameter object that describes all
            of the settings for the simulation. If None, some default simulation
            parameters will be automatically generated.
        measures_: An optional list of measures to apply to the OpenStudio model
            upon export. Use the "HB Load Measure" component to load a measure
            into Grasshopper and assign input arguments. Measures can be
            downloaded from the NREL Building Components Library (BCL) at
            (https://bcl.nrel.gov/).
        mappers_: An optional list of dragonfly MapperMeasure objects to be included
            in the output osw. MapperMeasures are just like normal OpenStudio
            measures except they can accept a list of values for their arguments
            that align with the buildings in dragonfly Model. Each value in
            the list will be mapped to a different building.
        report_: Boolean to note whether to include the URBANopt default feature reporting
            measure as part of the simulation. If True, the measure will be run
            after all simulations are complete. (Default:True).
        emiss_yr_: An optional integer to set the year for which carbon emissions
            will be computed. Values must be an even number and be between
            2020 and 2050. If unspecified, no carbon emission calculations
            will be included in the simulation. After the simulation is run,
            the hourly carbon emissions can be imported from the output
            sql files by using the "HB Read Custom Result" component and
            plugging in the following output name:
                Future_Hourly_Electricity_Emissions
        _cpus_: A positive integer for the number of CPUs to use in the simulation.
            This number should not exceed the number of CPUs on the machine
            running the simulation and should be lower if other tasks are
            running while the simulation is running. If set to None, it
            should automatically default to one less than the number of CPUs
            currently available on the machine (or 1 if the machine has only
            one processor). (Default: None).
        _run: Set to "True" to run the geojson through URBANopt.
            This will ensure that all result files appear in their respective
            outputs from this component. This input can also be the integer "2",
            which will only run the setup of the URBANopt project folder
            (including the creation of the scenario file) but will not execute
            the simulations.

    Returns:
        report: Reports, errors, warnings, etc.
        scenario: File path to the URBANopt scenario CSV used as input for the
            URBANopt CLI run.
        osm: File paths to the OpenStudio Models (OSM) that were generated in the
            process of running URBANopt.
        idf: File paths to the EnergyPlus Input Data Files (IDF) that were generated
            in the process of running URBANopt.
        sql: List of paths to .sqlite files containing all simulation results.
        zsz: List of paths to .csv files containing detailed zone load information
            recorded over the course of the design days.
        rdd: File paths of the Result Data Dictionary (.rdd) that were generated
            after running the file through EnergyPlus.  This file contains all
            possible outputs that can be requested from the EnergyPlus model. Use the
            "Read Result Dictionary" component to see what outputs can be requested.
        html: File paths of the HTMLs containting all Summary Reports.
"""

ghenv.Component.Name = 'DF Run URBANopt'
ghenv.Component.NickName = 'RunURBANopt'
ghenv.Component.Message = '1.5.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '1'


try:
    from honeybee_energy.simulation.parameter import SimulationParameter
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the dragonfly_energy dependencies
    from dragonfly_energy.run import base_honeybee_osw, prepare_urbanopt_folder, \
        run_urbanopt
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, recommended_processor_count
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import os
import json


if all_required_inputs(ghenv.Component) and _run:
    # check that the EPW and geoJSON files exists
    assert os.path.isfile(_epw_file), \
        'No EPW file was found at: {}'.format(_epw_file)
    assert os.path.isfile(_geojson), \
        'No geoJSON file was found at: {}'.format(_geojson)
    directory = os.path.dirname(_geojson)

    # generate default SimulationParameters if None are input to the component
    if _sim_par_ is None:
        _sim_par_ = SimulationParameter()
        _sim_par_.output.add_zone_energy_use()
        _sim_par_.output.add_hvac_energy_use()

    # assign design days from the DDY next to the EPW if there are None
    if len(_sim_par_.sizing_parameter.design_days) == 0:
        folder, epw_file_name = os.path.split(_epw_file)
        ddy_file = os.path.join(folder, epw_file_name.replace('.epw', '.ddy'))
        if os.path.isfile(ddy_file):
            _sim_par_.sizing_parameter.add_from_ddy_996_004(ddy_file)
        else:
            raise ValueError('No _ddy_file_ has been input and no .ddy file was '
                             'found next to the _epw_file.')

    # write the simulation parameter JSONs
    sim_par_dict = _sim_par_.to_dict()
    sim_par_json = os.path.join(directory, 'simulation_parameter.json')
    with open(sim_par_json, 'w') as fp:
        json.dump(sim_par_dict, fp)

    # write the base OSW to be used to translate all geoJSON features
    measures = None if len(measures_) == 0 or measures_[0] is None else measures_
    mappers = None if len(mappers_) == 0 or mappers_[0] is None else mappers_
    skip_report = not report_ if report_ is not None else False
    base_honeybee_osw(
        directory, sim_par_json=sim_par_json, additional_measures=measures,
        additional_mapper_measures=mappers, epw_file=_epw_file,
        skip_report=skip_report, emissions_year=emiss_yr_)

    # prepare the URBANopt folder and generate the scenario
    _cpus_ = _cpus_ if _cpus_ is not None else recommended_processor_count()
    scenario = prepare_urbanopt_folder(_geojson, _cpus_)

    # execute the simulation with URBANopt CLI
    if _run == 1:
        osm, idf, sql, zsz, rdd, html, err = run_urbanopt(_geojson, scenario, _cpus_)
