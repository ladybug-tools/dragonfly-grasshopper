# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Color a Dragonfly ElectricalNewtwork in the Rhino scene with OpenDSS simulation
results.
-

    Args:
        _data: A list of data collections of the same data type, which will be used
            to color the network with simulation results. These should come
            from the "DF Read OpenDSS Result" component.
        _network: A Dragonfly Electrical Newtork object to be colored with results
            in the Rhino scene.
        sim_step_: An optional integer (greater than or equal to 0) to select
            a specific step of the data collections for which result values will be
            generated. If None, the geometry will be colored with the maximum
            of resutls in the _data, essentially describing the peak
            condition. (Default: None).
        period_: A Ladybug analysis period to be applied to all of the input _data.
        legend_par_: An optional LegendParameter object to change the display
            of the colored output. (Default: None).

    Returns:
        vis_geo: Meshes and line segments colored according to the results.
        legend: Geometry representing the legend for colored objects.
        title: A text object for the global title.
        values: A list of values that align with the input substation, transformers
            and electrical connectors. These note the value assigned
            to each object.
        colors: A list of colors that align with the input substation, transformers
            and electrical connectors. These note the color of each object in
            the Rhino scene.
"""

ghenv.Component.Name = 'DF Color Network Results'
ghenv.Component.NickName = 'ColorNetResults'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry2d import Polygon2D, Polyline2D, LineSegment2D
    from ladybug_geometry.geometry3d import Face3D, Point3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly_energy.opendss.colorobj import ColorNetworkResults
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3ds_to_colored_mesh, \
        from_polyline2d, from_linesegment2d
    from ladybug_rhino.colorize import ColoredPolyline, ColoredLine
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.grasshopper import all_required_inputs, schedule_solution
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # apply analysis period to the data if connected
    if period_ is not None:
        _data = [coll.filter_by_analysis_period(period_) for coll in _data]

    # create the ColorNetwork visualization object and output geometry
    sim_step = 'max' if sim_step_ is None else sim_step_
    color_obj = ColorNetworkResults(_data, _network, legend_par_, sim_step)
    graphic = color_obj.graphic_container
    vis_geo = []
    for geo_obj, col in zip(color_obj.matched_geometries, graphic.value_colors):
        if isinstance(geo_obj, Polygon2D):
            face_obj = Face3D([Point3D(pt.x, pt.y, 0) for pt in geo_obj.vertices])
            vis_geo.append(from_face3ds_to_colored_mesh([face_obj], col))
        elif isinstance(geo_obj, Polyline2D):
            col_line = ColoredPolyline(from_polyline2d(geo_obj))
            col_line.color = color_to_color(col)
            col_line.thickness = 3
            vis_geo.append(col_line)
        elif isinstance(geo_obj, LineSegment2D):
            col_line = ColoredLine(from_linesegment2d(geo_obj))
            col_line.color = color_to_color(col)
            col_line.thickness = 3
            vis_geo.append(col_line)
    legend = legend_objects(graphic.legend)
    title = text_objects(color_obj.title_text, graphic.lower_title_location,
                         graphic.legend_parameters.text_height,
                         graphic.legend_parameters.font)
    values = color_obj.matched_values
    colors = [color_to_color(col) for col in graphic.value_colors]
    schedule_solution(ghenv.Component, 2)