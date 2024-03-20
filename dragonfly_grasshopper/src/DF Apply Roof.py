# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Assign Roof geometry to a Dragonfly Story, Building, or Model.
_
This can be used to generate sloped roofs over a Story. The roof geometry will only
affect the Room2Ds that have a True is_top_exposed property and it will only be
utilized in translation to Honeybee when the Story multiplier is 1.
_
Multiple sucessive versions of this component can be used to assign different
roof specifications for different Stories of a Dragonfly Building or Model.
-

    Args:
        _df_obj: A Dregonfly Story or Building to which the roof geometry is assigned.
            When a building is plugged in, only one story will receive the roof
            geometry, which will be the top floor unless an explicit _story_i_
            is specified below. This input can also be an entire Dragonfly Model,
            in which case the relevant Story of the first Building will receive the
            roof geometry, indicating that a Model inputs are really only
            appropriate when the Model contains one Building.
        _roof_geo: A list of Breps representing the geometry of the Roof.
            Together, these Breps should completely cover the Room2Ds of the
            Story to which they are assigned.
        _story_i_: An optional integer to set the index of the Story to which the Roof
            should be assigned. If unspecified, the roof geometry will be added
            to the top floor of any connected Building or Model.

    Returns:
        df_obj: The input Dragonfly objects with the roof geometry assigned to them.
"""

ghenv.Component.Name = 'DF Apply Roof'
ghenv.Component.NickName = 'ApplyRoof'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '7'

try:  # import the core dragonfly dependencies
    from dragonfly.roof import RoofSpecification
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default sotry index
    _story_i_ = _story_i_ if _story_i_ is not None else -1

    # create the RoofSpecification from the input geometry
    face3ds = []
    for geo_obj in _roof_geo:
        face3ds.extend(to_face3d(geo_obj))
    roof = RoofSpecification(face3ds)
    over_count = roof.overlap_count(tolerance)
    if over_count > 0:
        msg = 'The input _roof_geo was found to have {} overlaps in plan.\n' \
            'This is not considered valid and can cause issues.'.format(over_count)
        print(msg)
        give_warning(ghenv.Component, msg)

    # duplicate the input object and assign the roof to it
    df_obj = _df_obj.duplicate()
    if isinstance(df_obj, Story):
        df_obj.roof = roof
    elif isinstance(df_obj, Building):
        df_obj[_story_i_].roof = roof
    elif isinstance(df_obj, Model):
        df_obj.buildings[0][_story_i_].roof = roof
    else:
        msg = 'Expected Dragonfly Story, Building, or Model. Got {}'.format(type(df_obj))
        print(msg)
        raise ValueError(msg)
