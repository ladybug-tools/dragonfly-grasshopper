# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a Dragonfly Story from individual Dragonfly Room2D objects.
-

    Args:
        _room_2ds: A list of dragonfly Room2D objects that together form a story
            of a building.
        _flr_to_flr_: A number for the distance from the floor plate of
            this Story to the floor of the story above this one (if it exists).
            If None, this value will be the maximum floor_to_ceiling_height of the
            input _room_2ds.
        _name_:  A name for the Story. If the name is not provided a random
            name will be assigned.
        multiplier_: An integer with that denotes the number of times that this
            Story is repeated over the height of the building. Default: 1.
        _constr_set_: Text for the construction set of the Story, which is used
            to assign all default energy constructions needed to create an energy
            model. Text should refer to a ConstructionSet within the library such
            as that output from the "HB List Construction Sets" component. This
            can also be a custom ConstructionSet object. If nothing is input here,
            the Story will have a generic construction set that is not sensitive
            to the Story's climate or building energy code.
    
    Returns:
        report: Reports, errors, warnings, etc.
        building: Dragonfly Story.
"""

ghenv.Component.Name = "DF Story"
ghenv.Component.NickName = 'Story'
ghenv.Component.Message = '0.1.1'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

# document-wide counter to generate new unique Story names
import scriptcontext
try:
    scriptcontext.sticky["story_count"]
except KeyError:  # first time that the component is running
    scriptcontext.sticky["story_count"] = 1

try:  # import the core dragonfly dependencies
    from dragonfly.story import Story
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the dragonfly-energy extension
    import dragonfly_energy
    from honeybee_energy.lib.constructionsets import construction_set_by_name
except ImportError as e:
    if _constr_set_ is not None:
        raise ValueError('_constr_set_ has been specified but dragonfly-energy '
                         'has failed to import.\n{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    room2ds = [room.duplicate() for room in _room2ds]
    
    # generate a default name
    if _name_ is None:  # get a default Story name
        _name_ = "Story_{}".format(scriptcontext.sticky["story_count"])
        scriptcontext.sticky["story_count"] += 1
    
    # set other defaults
    multiplier_ = multiplier_ if multiplier_ is not None else 1
    
    # create the Story
    story = Story(_name_, room2ds, _flr_to_flr_, multiplier_)
    
    # assign the construction set
    if _constr_set_ is not None:
        if isinstance(_constr_set_, str):
            _constr_set_ = construction_set_by_name(_constr_set_)
        story.properties.energy.construction_set = _constr_set_