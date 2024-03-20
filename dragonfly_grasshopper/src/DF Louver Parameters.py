# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create Dragonfly shading parameters with instructions for a series of louvered
Shades over a Wll.
-

    Args:
        _depth: A number for the depth to extrude the louvers.
        _shade_count_: A positive integer for the number of louvers to generate.
            Note that this input should be None if there is an input for
            _dist_between_. Default: 1.
        _dist_between_: A number for the approximate distance between each louver.
            Note that this input should be None if there is an input for
            _shade_count_.
        _facade_offset_: A number for the distance to louvers from the Wall.
            Default is 0 for no offset.
        _angle_: A number for the for an angle to rotate the louvers in degrees.
            Default is 0 for no rotation.
        vertical_: Optional boolean to note whether the lovers are vertical.
            If False, the louvers will be horizontal. Default False.
        flip_start_: Boolean to note whether the side the louvers start from
            should be flipped. Default is False to have contours on top or right.
            Setting to True will start contours on the bottom or left.
    
    Returns:
        shd_par: Shading Parameters that can be applied to a Dragonfly object
            using the "DF Apply Facade Parameters" component.
"""

ghenv.Component.Name = "DF Louver Parameters"
ghenv.Component.NickName = 'LouverPar'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "6"

try:
    from ladybug_geometry.geometry2d.pointvector import Vector2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.shadingparameter import LouversByDistance, LouversByCount
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set defaults for any blank inputs
    _facade_offset_ = _facade_offset_ if _facade_offset_ is not None else 0.0
    _angle_ = _angle_ if _angle_ is not None else 0.0
    flip_start_ = flip_start_ if flip_start_ is not None else False
    
    # process the defaults for _shade_count_ vs _dist_between
    if _shade_count_ is not None and _dist_between_ is not None:
        raise ValueError('Inputs for _shade_count_ and _dist_between_ are both set.'
                         '\nThis component accepts either method but not both.')
    elif _shade_count_ is None and _dist_between_ is None:
        _shade_count_ = 1
    
    # process the vertical_ input into a direction vector
    vertical_ = Vector2D(1, 0) if vertical_ else Vector2D(0, 1)
    
    if _shade_count_ is not None:
        shd_par = LouversByCount(_shade_count_, _depth, _facade_offset_,
                                 _angle_, vertical_, flip_start_)
    else:
        shd_par = LouversByDistance(_dist_between_, _depth, _facade_offset_,
                                    _angle_, vertical_, flip_start_)