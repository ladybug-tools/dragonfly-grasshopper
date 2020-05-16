# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Deconstruct any Dragonfly geometry object into ALL of its constituent Dragonfly objects.
_
This is useful for editing auto-generated child objects separately from their parent.
For example, if you want to assign all of the ground floors of a given auto-generated
Building to have a Retail ProgramType, this can give you all of such Stories. Then
you can assign a Retail ProgramType to them and combine them with the other Stories
into a new Building.
-

    Args:
        _df_obj: A Dragonfly Building, Story or Room2D to be deconstructed into
            all of its constituent objects. Note that, Room2Ds do not have
            sub-objects assigned to them and the original object will be output.
    
    Returns:
        stories: All Story objects that make up the input _df_obj. This
            includes all Stories that make up input Buildings as well as any
            input orphaned Stories.
        room2ds: All Room2D objects that make up the input _df_obj. This
            includes any all Room2Ds assigned to input Stories or Buildings as
            well as any input orphaned Room2Ds.
"""

ghenv.Component.Name = "DF Deconstruct All Object"
ghenv.Component.NickName = 'DecnstrAllDF'
ghenv.Component.Message = '0.1.2'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def deconstruct_story(story, stories, room2ds):
    """Deconstruct Story object."""
    stories.append(story)
    room2ds.extend(story.room_2ds)

def deconstruct_building(bldg, stories, room2ds):
    """Deconstruct Building object."""
    for story in bldg.all_stories():
        deconstruct_story(story, stories, room2ds)


if all_required_inputs(ghenv.Component):
    # lists to be filled with constituent objects
    all_stories = []
    all_room2ds = []
    
    if isinstance(_df_obj, Building):
        deconstruct_building(_df_obj, all_stories, all_room2ds)
    elif isinstance(_df_obj, Story):
        deconstruct_story(_df_obj, all_stories, all_room2ds)
    elif isinstance(_df_obj, Story):
        all_room2ds.append(_df_obj)
    else:
        raise TypeError(
            'Unrecognized dragonfly object type: {}'.format(type(_df_obj)))
