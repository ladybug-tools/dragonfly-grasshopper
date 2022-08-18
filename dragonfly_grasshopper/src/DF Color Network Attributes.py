# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Color a Dragonfly ElectricalNewtwork in the Rhino scene using its attributes.
_
This can be used as a means to check that correct properties are assigned to
different Transformers and ElectricalConnectors.
-

    Args:
        _network: A Dragonfly Electrical Newtork object to be colored with its
            attributes in the Rhino scene.
        _attribute: Text for the name of the equipment attribute with which the Newtork
            should be colored. The "DF Network Attributes" component lists
            all of the attributes of the equipment of an ElectricalNetwork.
        legend_par_: An optional LegendParameter object to change the display
            of the colored output. (Default: None).

    Returns:
        vis_geo: Meshes and line segments colored according to their attributes.
        legend: Geometry representing the legend for colored objects.
        values: A list of values that align with the input substation, transformers
            and electrical connectors. These note the attribute assigned
            to each object.
        colors: A list of colors that align with the input substation, transformers
            and electrical connectors. These note the color of each object in
            the Rhino scene.
"""

ghenv.Component.Name = 'DF Color Network Attributes'
ghenv.Component.NickName = 'ColorNetAttr'
ghenv.Component.Message = '1.5.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry2d import Polygon2D, Polyline2D, LineSegment2D
    from ladybug_geometry.geometry3d import Face3D, Point3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly_energy.opendss.colorobj import ColorNetwork
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3ds_to_colored_mesh, \
        from_polyline2d, from_linesegment2d
    from ladybug_rhino.colorize import ColoredPolyline, ColoredLine
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.grasshopper import all_required_inputs, schedule_solution
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # create the ColorNetwork visualization object and output geometry
    color_obj = ColorNetwork(_network, _attribute, legend_par_)
    graphic = color_obj.graphic_container
    vis_geo = []
    for geo_obj, col in zip(color_obj.geometries, graphic.value_colors):
        if isinstance(geo_obj, Polygon2D):
            face_obj = Face3D([Point3D(pt.x, pt.y, 0.1) for pt in geo_obj.vertices])
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
    values = color_obj.attributes_original
    colors = [color_to_color(col) for col in graphic.value_colors]
    schedule_solution(ghenv.Component, 2)