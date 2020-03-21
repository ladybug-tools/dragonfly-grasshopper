# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert a Dragonfly Model into an URBANopt-compatible geoJSON.
-

    Args:
        _model: A Dragonfly Model object.
        _epw_file: Path to an .epw file on this computer as a text string.
        _location: A ladybug Location object possessing longitude and lattiude data
            used to position geoJSON file on the globe.
        _point_: A Point for where the location object exists within the space of
            the Rhino scene. This is used to posistion the geoJSON file on the
            globe. (Default: (0, 0)).
        _cpus_: A positive integer for the number of CPUs to use in the simulation.
            This should be changed based on the machine on which the simulation
            is being run in order to yield the fastest simulation (Default: 2).
        _folder_: Text for the full path to the folder where the OpenStudio
            model files for each building are written. This is also the location
            where the geojson will be written along with all of the urbanopt files
            (under a folder with the same name as the dragonfly model). If None,
            the honeybee default simulation folder is used.
        _write: Set to "True" to have the Dragonfly Model translated to an
            URBANopt-compatible geoJSON.
        run_: Set to "True" to run the geojson and osm files through URBANopt.
            This will ensure that all result files appear in their respective
            outputs from this component. This input can also be the integer "2",
            which will only run the setup of the URBANopt project folder
            (including the scenario and feature files) but will not execute
            the simulations.
    
    Returns:
        report: Reports, errors, warnings, etc.
        geojson: The path to a geoJSON file that contains polygons for all of the
            Buildings within the dragonfly model along with their properties
            (floor area, number of stories, etc.). The polygons will also possess
            detailed_model_filename keys that align with where OpenStudio models
            would be written, assuming the input folder matches that used to
            export OpenStudio models.
        scenario: The path to a CSV file for the URBANopt scenario.
        sql: The file path of the SQL result file that has been generated on this
            computer. This will be None unless run_ is set to True.
        zsz: Path to a .csv file containing detailed zone load information recorded
            over the course of the design days. This will be None unless run_ is
            set to True.
        rdd: The file path of the Result Data Dictionary (.rdd) file that is
            generated after running the file through EnergyPlus.  This file
            contains all possible outputs that can be requested from the EnergyPlus
            model.  Use the Read Result Dictionary component to see what outputs
            can be requested.
        html: The HTML file path of the Summary Reports. Note that this will be None
            unless the input _sim_par_ denotes that an HTML report is requested and
            run_ is set to True.
"""

ghenv.Component.Name = "DF Model To URBANopt"
ghenv.Component.NickName = 'ToURBANopt'
ghenv.Component.Message = '0.3.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '1 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = "1"


try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry2d.pointvector import Point2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the ladybug dependencies
    from ladybug.location import Location
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the dragonfly_energy dependencies
    from dragonfly_energy.run import prepare_urbanopt_folder, run_urbanopt
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_point2d
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import os


if all_required_inputs(ghenv.Component) and _write:
    # set default inputs if not specified
    point = to_point2d(_point_) if _point_ is not None else Point2D(0, 0)
    _cpus_ = 2 if _cpus_ is None else _cpus_

    # check the _model and _location input
    assert isinstance(_model, Model), \
        'Expected Dragonfly Model object. Got {}.'.format(type(_model))
    assert isinstance(_location, Location), \
        'Expected Ladybug Location object. Got {}.'.format(type(_location))

    if run_ is None or run_ < 1:  # only create the geojson without URBANopt
        geojson = _model.to_geojson(_location, point, _folder_, tolerance)
    else:  # create the geosjon and folder using URBANopt SDK
        geojson_dict = _model.to_geojson_dict(_location, point, _folder_, tolerance)
        uo_folder = os.path.join(_folder_, _model.name) if _folder_ is not None \
            else os.path.join(folders.default_simulation_folder, _model.name)
        geojson, scenario = prepare_urbanopt_folder(
            uo_folder, geojson_dict, _epw_file, _cpus_)

        if run_ == 1:
            sql, zsz, rdd, html, err = run_urbanopt(geojson, scenario)
