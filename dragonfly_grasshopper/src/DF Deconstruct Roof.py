# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct any Dragonfly Story, Building or Model to get the Roof geometry.
_
This is useful for checking the roof geometry assigned to sotries and possbily
editing it so that it can be re-assigned with "DF Apply Roof" component.
-

    Args:
        _df_obj: A Dragonfly Model, Building, Story for which the roof geometry will
            be extracted.

    Returns:
        stories: The unique Story objects that make up the input _df_obj. This
            is typically a data tree with branches coordinated with the
            roof_geo below.
        roof_geo: A list of Breps representing the geometry of the Roof.
            This is often a data tree with one branch for each story, which
            is coordinated with the stories above.
"""

ghenv.Component.Name = "DF Deconstruct Roof"
ghenv.Component.NickName = 'DecnstrRoof'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.fromgeometry import from_face3d
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def deconstruct_story(story, stories, roofs):
    """Deconstruct Story object."""
    stories.append([story])
    if story.roof is not None:
        roofs.append([from_face3d(geo) for geo in story.roof])
    else:
        roofs.append([])

def deconstruct_building(bldg, stories, roofs):
    """Deconstruct Building object."""
    for story in bldg.unique_stories:
        deconstruct_story(story, stories, roofs)


if all_required_inputs(ghenv.Component):
    # lists of to be filled with constituent objects
    stories = []
    roof_geo = []

    # get the roof geometry
    if isinstance(_df_obj, Model):
        for bldg in _df_obj.buildings:
            deconstruct_building(bldg, stories, roof_geo)
    elif isinstance(_df_obj, Building):
        deconstruct_building(_df_obj, stories, roof_geo)
    elif isinstance(_df_obj, Story):
        deconstruct_story(_df_obj, stories, roof_geo)
    else:
        raise TypeError(
            'Unrecognized dragonfly object type: {}'.format(type(_df_obj)))

    # translate lists to data trees
    stories = list_to_data_tree(stories)
    roof_geo = list_to_data_tree(roof_geo)
