# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Color Dragonfly Room2Ds in the Rhino scene using their attributes.
_
This can be used as a means to check that correct properties are assigned to
different Room2Ds.
-

    Args:
        _df_obj: A Dragonfly Model, Building, Story or Room2D to be colored
            with their attributes in the Rhino scene.
        _attribute: Text for the name of the Room2D attribute with which the Room2Ds
            should be colored. The "DF Room2D Attributes" component lists
            all of the attributes of the Room2D.
        legend_par_: An optional LegendParameter object to change the display
            of the colored Room2Ds. (Default: None).

    Returns:
        mesh: Meshes of the Room2D floors colored according to their attributes.
        legend: Geometry representing the legend for colored meshes.
        wire_frame: A list of lines representing the outlines of the rooms.
        values: A list of values that align with the input Room2Ds noting the
            attribute assigned to each Room2D.
        colors: A list of colors that align with the input Room2Ds, noting the color
            of each Room2D in the Rhino scene. This can be used in conjunction
            with the native Grasshopper "Custom Preview" component and other
            dragonfly visualization components (like "DF Visulaize All") to
            create custom visualizations in the Rhino scene.
"""

ghenv.Component.Name = 'DF Color Room2D Attributes'
ghenv.Component.NickName = 'ColorRoom2DAttr'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the core dragonfly dependencies
    from dragonfly.colorobj import ColorRoom2D
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3ds_to_colored_mesh, \
        from_face3d_to_wireframe
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # extract any rooms from input Models
    rooms = []
    for df_obj in _df_obj:
        if isinstance(df_obj, Model):
            for bldg in df_obj.buildings:
                rooms.extend(bldg.all_room_2ds())
        elif isinstance(df_obj, Building):
            rooms.extend(df_obj.all_room_2ds())
        elif isinstance(df_obj, Story):
            rooms.extend(df_obj.room_2ds)
        elif isinstance(df_obj, Room2D):
            rooms.extend([df_obj])

    # create the ColorRoom visualization object and output geometry
    color_obj = ColorRoom2D(rooms, _attribute, legend_par_)
    graphic = color_obj.graphic_container
    mesh = [from_face3ds_to_colored_mesh([flrs], col) for flrs, col in
            zip(color_obj.floor_faces, graphic.value_colors)]
    wire_frame = []
    for room in rooms:
        wire_frame.extend(from_face3d_to_wireframe(room.floor_geometry))
    legend = legend_objects(graphic.legend)
    values = color_obj.attributes_original
    colors = [color_to_color(col) for col in graphic.value_colors]