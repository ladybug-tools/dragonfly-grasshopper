# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Convert a Dragonfly Model into an URBANopt-compatible geoJSON with linked Honeybee
Model JSONs. Honeybee Model JSONs will be referenced using the "detailed_model_filename"
key in the geoJSON.
-

    Args:
        _model: A Dragonfly Model object.
        _location: A ladybug Location object possessing longitude and lattiude data
            used to position geoJSON file on the globe.
        _point_: A Point for where the _location object exists within the space of
            the Rhino scene. This is used to posistion the geoJSON file on the
            globe. (Default: Rhino origin (0, 0, 0)).
        use_multiplier_: If True, the multipliers on each Building's Stories will be
            passed along to the generated Honeybee Room objects, indicating the
            simulation will be run once for each unique room and then results
            will be multiplied. If False, full geometry objects will be written
            for each and every story in the building such that all resulting
            multipliers will be 1. Default: True.
        add_plenum_: Boolean to indicate whether ceiling/floor plenums should
            be auto-generated for the Rooms. The height of ceiling plenums
            will be autocalculated as the difference between the Room2D
            ceiling height and Story ceiling height. The height of the floor
            plenum will be autocalculated as the difference between the Room2D
            floor height and Story floor height. (Default: False).
        ceil_adjacency_: Boolean to note whether adjacencies should be solved between
            interior stories when Room2Ds perfectly match one another in
            their floor plate. This ensures that Surface boundary conditions
            are used instead of Adiabatic ones. (Default: False).
        shade_dist_: An optional number to note the distance beyond which other
            buildings' shade should not be exported into a given Model. This is
            helpful for reducing the simulation run time of each Model when other
            connected buildings are too far away to have a meaningful impact on
            the results. If None, all other buildings will be included as context
            shade in each and every Model. Set to 0 to exclude all neighboring
            buildings from the resulting models. Default: None.
        elec_network_: An optional OpenDSS ElectricalNetwork that's associated
            with the input Dragonfly Model and will be written into the
            geoJSON. An input here is required to perform an OpenDSS
            simulation after running URBANopt.
        ground_pv_:  An optional list of REopt GroundMountPV objects representing
            ground-mounted photovoltaic fields to be included in a REopt
            simulation after running URBANopt.
        _folder_: Text for the full path to the folder where the geojson will be
            written along with all of the Honeybee Model JSONs. If None, the
            honeybee default simulation folder is used.
        _write: Set to "True" to have the Dragonfly Model translated to an
            URBANopt-compatible geoJSON. This input can also be the integer "2",
            which will only create the geojson file but not create any honeybee
            Model json files that are linked to it (note that a geojson produced
            this way is not compatible with URBANopt).

    Returns:
        report: Reports, errors, warnings, etc.
        geojson: The path to a geoJSON file that contains polygons for all of the
            Buildings within the dragonfly model along with their properties
            (floor area, number of stories, etc.). The polygons will also possess
            detailed_model_filename keys that align with where the Honeybee Model
            JSONs are written.
        hb_jsons: A list of file paths to honeybee Model JSONS that correspond to
            the detailed_model_filename keys in the geojson.
        hb_models: A list of honeybee Model objects that were generated in process
            of writing the URBANopt files. These can be visulazed using the
            components in the Honeybee 1 :: Visualize tab in order to verify
            that properties have been translated as expected.
"""

ghenv.Component.Name = 'DF Model To geoJSON'
ghenv.Component.NickName = 'ToGeoJSON'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '2 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry2d.pointvector import Point2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the ladybug dependencies
    from ladybug.location import Location
    from ladybug.futil import nukedir
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the ladybug dependencies
    from honeybee.config import folders
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

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
    # check the _model and _location input
    assert isinstance(_model, Model), \
        'Expected Dragonfly Model object. Got {}.'.format(type(_model))
    assert isinstance(_location, Location), \
        'Expected Ladybug Location object. Got {}.'.format(type(_location))

    # set default inputs if not specified
    point = to_point2d(_point_) if _point_ is not None else Point2D(0, 0)
    use_multiplier_ = use_multiplier_ if use_multiplier_ is not None else True
    add_plenum_ = add_plenum_ if add_plenum_ is not None else False
    ceil_adjacency_ = ceil_adjacency_ if ceil_adjacency_ is not None else False

    if _write == 2:
        geojson = _model.to_geojson(_location, point, _folder_, tolerance)
    else:
        # create the geoJSON and honeybee Model JSONs
        geojson, hb_jsons, hb_models = _model.to.urbanopt(
            _model, _location, point, shade_dist_, use_multiplier_,
            add_plenum_, ceil_adjacency_,
            electrical_network=elec_network_, ground_pv=ground_pv_,
            folder=_folder_, tolerance=tolerance)
