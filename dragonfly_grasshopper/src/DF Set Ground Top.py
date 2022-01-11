# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Set Room2Ds or Stories to have their floor in contact with the ground or
their roofs in contact with the outdoors.
-

    Args:
        _df_obj: Dragonfly Stories or Room2Ds which will have its floor set to be
            in contact with the ground or its roof to be in contact with the
            outdoors.
        grnd_contact_: A boolean noting whether the input objects have floors
            in contact with the ground.
        top_exposed_: A boolean noting whether the input objects have ceilings
            exposed to the outdoors.
    
    Returns:
        report: Reports, errors, warnings, etc.
        df_obj: The input Dragonfly object with its ground_contact or top_exposed
            properties edited.
"""

ghenv.Component.Name = 'DF Set Ground Top'
ghenv.Component.NickName = 'SetGrndTop'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the core dragonfly dependencies
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    df_obj = [obj.duplicate() for obj in _df_obj]

    # set the ground contact
    if grnd_contact_ is not None:
        for obj in df_obj:
            if isinstance(obj, Room2D):
                obj.is_ground_contact = grnd_contact_
            elif isinstance(obj, Story):
                obj.set_ground_contact(grnd_contact_)
            else:
                raise TypeError('_df_obj must be a Room2D or a Story. '
                                'Got {}.'.format(type(obj)))

    # set the top exposure
    if top_exposed_ is not None:
        for obj in df_obj:
            if isinstance(obj, Room2D):
                obj.is_top_exposed = top_exposed_
            elif isinstance(obj, Story):
                obj.set_top_exposed(top_exposed_)
            else:
                raise TypeError('_df_obj must be a Room2D or a Story. '
                                'Got {}.'.format(type(obj)))
