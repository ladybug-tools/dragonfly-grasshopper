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
        _location: A ladybug Location object possessing longitude and lattiude data
            used to position geoJSON file on the globe.
        _point_: A Point for where the location object exists within the space of
            the Rhino scene. This is used to posistion the geoJSON file on the
            globe. (Default: (0, 0)).
        _folder_: Text for the full path to the folder where the OpenStudio
            model files for each building are written. This is also the location
            where the geojson will be written. If None, the honeybee default
            simulation folder is used.
        _write: Set to "True" to have the Dragonfly Model translated to an
            URBANopt-compatible geoJSON.
    
    Returns:
        report: Reports, errors, warnings, etc.
        geojson: The path to a geoJSON file that contains polygons for all of the
            Buildings within the dragonfly model along with their properties
            (floor area, number of stories, etc.). The polygons will also possess
            detailed_model_filename keys that align with where OpenStudio models
            would be written, assuming the input folder matches that used to
            export OpenStudio models.
"""

ghenv.Component.Name = "DF Model To URBANopt"
ghenv.Component.NickName = 'ToURBANopt'
ghenv.Component.Message = '0.1.0'
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
    # set default inputs if not specified
    point = to_point2d(_point_) if _point_ is not None else Point2D(0, 0)
    
    # check the _model and _location input
    assert isinstance(_model, Model), \
        'Expected Dragonfly Model object. Got {}.'.format(type(_model))
    assert isinstance(_location, Location), \
        'Expected Ladybug Location object. Got {}.'.format(type(_location))
    
    # create the geojson
    geojson = _model.to_geojson(_location, point, _folder_, tolerance)
