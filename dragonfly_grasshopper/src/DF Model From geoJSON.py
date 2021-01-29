# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a Dragonfly Model from a geoJSON file.
-

    Args:
        _geojson: Text for the full path to a geojson file to be loaded as a
            Dragonfly Model.
        _point_: An optional Point for where the bottom-left corner of the bounding
            rectangle around all of the geoJSON building footprints exists
            within the Rhino scene. (Default: (0, 0), the Rhino origin).
        all_to_bldg_: Boolean to indicate if all polygon and multi-polygon geometries
            in the geojson file should be considered Buildings. If False or
            unspecified, this component will only generate Dragonfly Buildings
            from geometries that are defined as a 'Building' in the 'type'
            field of the 'properties' field of each geoJSON feature. Note that
            this 'type' field is not a universal convention of all geoJSONs.
            However, all Dragonfly-expored geoJSONs will have it and all
            URBANopt-compatible geoJSONs will also have it.
        other_geo_: Boolean to indicate whether geometry that is not identified as
            a dragonfly Building should be imported. For large geoJSONs,
            this can potentially increase the component runtime a lot but
            this geometry may be useful for constructing other important
            features like context or electical networks.
        _import: Set to "True" to import the geoJSON as a Dragonfly Model.

    Returns:
        report: Reports, errors, warnings, etc.
        model: A Dragonfly Model object derived from the input geoJSON.
        other_geo: Other non-building line segment and polygon data contained
            within the geoJSON. Will be None unless other_geo_ is set to True.
        location: A ladybug Location object possessing longitude and lattiude data
            used to position geoJSON file on the globe.
        point: A Point for where the _location object exists within the space of
            the Rhino scene. This is can be used to re-position the geoJSON
            file on the globe when re-exporting the Dragonfly Model to geoJSON.
"""

ghenv.Component.Name = 'DF Model From geoJSON'
ghenv.Component.NickName = 'FromGeoJSON'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '2 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import json

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry2d.pointvector import Point2D
    from ladybug_geometry.geometry2d.line import LineSegment2D
    from ladybug_geometry.geometry2d.polyline import Polyline2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.projection import meters_to_long_lat_factors, \
        origin_long_lat_from_location, lon_lat_to_polygon
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_point2d
    from ladybug_rhino.fromgeometry import from_point2d, from_linesegment2d, \
        from_polyline2d
    from ladybug_rhino.config import tolerance, angle_tolerance, units_system, \
        conversion_to_meters
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _import:
    # set default inputs if not specified
    pt = to_point2d(_point_) if _point_ is not None else Point2D(0, 0)
    all_to_bldg = bool(all_to_bldg_)  # handle case of None
    model_units, con_fac = units_system(), 1 / conversion_to_meters()

    # convert the geoJSON to a dragonfly Model
    model, location = Model.from_geojson(
        _geojson,
        point=pt,
        all_polygons_to_buildings=all_to_bldg,
        units=model_units,
        tolerance=tolerance,
        angle_tolerance=angle_tolerance)
    point = from_point2d(pt)

    # if other geometry has been requested, then import it
    if other_geo_:
        # parse the geoJSON into a dictionary and get lat/lon converters
        with open(_geojson, 'r') as fp:
            data = json.load(fp)
        origin_lon_lat = origin_long_lat_from_location(location, pt)
        _convert_facs = meters_to_long_lat_factors(origin_lon_lat)
        convert_facs = 1 / _convert_facs[0], 1 / _convert_facs[1]

        # get all of the non-building geometry features
        geo_types = ('LineString', 'Polygon')
        geo_data = [geo for geo in data['features'] if 'geometry' in geo
                    and geo['geometry']['type'] in geo_types]
        if not all_to_bldg:  # exclude anything with a Building key
            geo_data = [geo for geo in geo_data if 'type' not in geo['properties']
                        or geo['properties']['type'] != 'Building']

        # convert all of the geoJSON data into Rhino geometry
        other_geo = []
        for geo_dat in geo_data:
            if geo_dat['geometry']['type'] == 'LineString':
                coords = lon_lat_to_polygon(geo_dat['geometry']['coordinates'],
                                            origin_lon_lat, convert_facs)
                pts = tuple(Point2D.from_array(pt) for pt in coords)
                line = LineSegment2D.from_end_points(pts[0], pts[1]) \
                    if len(pts) == 2 else Polyline2D(pts)
                if con_fac != 1:
                    line = line.scale(con_fac, pt)
                if len(pts) == 2:
                    other_geo.append(from_linesegment2d(line))
                else:
                    other_geo.append(from_polyline2d(line))
            else:  # is's a polygon
                coords = lon_lat_to_polygon(geo_dat['geometry']['coordinates'][0],
                                            origin_lon_lat, convert_facs)
                pts = tuple(Point2D.from_array(pt) for pt in coords)
                poly = Polyline2D(pts)
                if con_fac != 1:
                    poly = poly.scale(con_fac, pt)
                other_geo.append(from_polyline2d(poly))
