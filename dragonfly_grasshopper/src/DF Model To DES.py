# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Convert a Dragonfly Model into an URBANopt-compatible geoJSON and DES input files.
_
This component is intended specifically for the case that District Energy
System (DES) simulation is to be performed without using URBANopt to generate
building energy loads through EnergyPlus. Accordingly, ALL Dragonfly Buildings
in the Model must have DES loads assigned directly to them in order for this
component to run correctly.
-

    Args:
        _model: A Dragonfly Model object.
        _des_loop: A District Energy System (DES) ThermalLoop that is associated
            with the dragonfly Model.
        _epw_file: The file path to an EPW that should be associated with the
            output energy model.
        _location_: A ladybug Location object possessing longitude and lattiude data
            used to position geoJSON file on the globe.
        _point_: A Point for where the _location object exists within the space of
            the Rhino scene. This is used to posistion the geoJSON file on the
            globe. (Default: Rhino origin (0, 0, 0)).
        _folder_: An optional folder to be used as the root of the URBANopt project
            folder. If None, the files will be written into a sub-directory
            of the default simulation folder.
        _write: Set to "True" to have the Dragonfly Model translated to a geoJSON
            and other project folder files for District Energy System (DES)
            simulation.

    Returns:
        report: Reports, errors, warnings, etc.
        geojson: The path to a geoJSON file that contains polygons for all of the
            Buildings within the dragonfly model along with any geometry of
            the District Energy System (DES).
        scenario: File path to the URBANopt scenario CSV that points to the building
            loads for DES simulation. This can be plugged into the "DF Write
            Modelica DES" component to create a full Modelica model of the DES.
"""

ghenv.Component.Name = 'DF Model To DES'
ghenv.Component.NickName = 'ToDES'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry2d.pointvector import Point2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_point2d
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _write:
    # check the _model and set default inputs
    assert isinstance(_model, Model), \
        'Expected Dragonfly Model object. Got {}.'.format(type(_model))
    point = to_point2d(_point_) if _point_ is not None else Point2D(0, 0)

    # create the geoJSON and honeybee Model JSONs
    geojson, scenario, sys_params = _model.to.urbanopt_des(
        _model, _des_loop, _epw_file, _location_, point,
        folder=_folder_, tolerance=tolerance)
