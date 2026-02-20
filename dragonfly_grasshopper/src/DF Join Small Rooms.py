# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Join small Room2Ds together within Dragonfly Stories.
_
This is particularly useful after operations like automatic core/perimeter
offsetting, which can create several small Room2Ds from small segments in the
outline boundary around the Story.
-

    Args:
        _df_obj: A Dregonfly Story, Building or Model to have its small Room2Ds
            joined together across the model
        _area_thresh_: A number for the Room2D floor area below which it is considered
            a small room to be joined into adjacent rooms. (Default: 10.0 square meters).
        join_to_large_: A boolean to note whether the small Room2Ds should
            be joined into neighboring large Room2Ds as opposed to simply
            joining the small rooms to one another. (Default: False).

    Returns:
        report: Reports, errors, warnings, etc.
        df_obj: The input Dragonfly objects with Room2Ds that have had small
            Room2Ds joined together.
"""

ghenv.Component.Name = 'DF Join Small Rooms'
ghenv.Component.NickName = 'JoinSmall'
ghenv.Component.Message = '1.10.0'
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
    from ladybug_rhino.config import current_tolerance, conversion_to_meters
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
tolerance = current_tolerance()


if all_required_inputs(ghenv.Component):
    # set the default area threshold
    a_thresh = _area_thresh_ if _area_thresh_ is not None \
        else 10.0 / conversion_to_meters()

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

    # merge small rooms together in the story
    for story in stories:
        story.join_small_room_2ds(a_thresh, join_into_large=join_to_large_,
                                  tolerance=tolerance)
        story.reset_adjacency()
        story.solve_room_2d_adjacency(tolerance=tolerance)
