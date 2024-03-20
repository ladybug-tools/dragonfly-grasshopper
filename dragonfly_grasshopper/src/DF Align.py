# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Move Room2D vertices within a given distance of a line to be on that line.
_
This is particularly useful for cleaning up models with extra unwanted
corrugations in them around columns and other "room bounding" elements.
_
Note that, when there are small Room2Ds next to the input lines, this component
may completely remove the small Room2D if it becomes degenerate.
-

    Args:
        _df_obj: A Dregonfly Story, Building or Model to be aligned to the input lines.
            For Buildings and Models, all Room2Ds across the object will be aligned.
        _lines: A list of straignt lines to which the Room2D vertices will be aligned.
        _distance_: The maximum distance between a vertex and a line where the vertex
            will be moved to lie on the line. Vertices beyond this distance will
            be left as they are. The default is 0.5 meters.

    Returns:
        df_obj: The input Dragonfly objects with Room2Ds that have been aligned to
            the input lines.
"""

ghenv.Component.Name = 'DF Align'
ghenv.Component.NickName = 'Align'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance, conversion_to_meters
    from ladybug_rhino.togeometry import to_linesegment2d
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default alignment distance
    dist = _distance_ if _distance_ is not None else 0.5 / conversion_to_meters()

    # translate the lines and 
    line_rays = [to_linesegment2d(line) for line in _lines]

    # duplicate the input object and gather all of the stories
    df_obj = _df_obj.duplicate()
    if isinstance(df_obj, Story):
        stories = [df_obj]
    elif isinstance(df_obj, Building):
        stories = df_obj.unique_stories
    elif isinstance(df_obj, Model):
        stories = df_obj.stories
    else:
        msg = 'Expected Dragonfly Story, Building, or Model. Got {}'.format(type(df_obj))
        print(msg)
        raise ValueError(msg)

    # align all of the stories to the lines
    del_rooms = []
    for story in stories:
        for line in line_rays:
            story.align(line, dist, tolerance)
        del_rooms.extend(
            story.remove_room_2d_duplicate_vertices(tolerance, delete_degenerate=True))
        del_rooms.extend(story.delete_degenerate_room_2ds())
        story.rebuild_detailed_windows(tolerance)

    # give a warning about any degenerate rooms that were deleted
    if len(del_rooms) != 0:
        del_ids = [r.display_name for r in del_rooms]
        msg = 'The following Room2Ds were degenerate after the operation and ' \
            'were deleted:\n{}'.format('\n'.join(del_ids))
        print(msg)
        give_warning(ghenv.Component, msg)
