# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply WindowParameters and/or ShadingParameters to any Dragonfly object (Building,
Story, Room2D).
-

    Args:
        _df_obj: A Dragonfly Building, Story or Room2D which will have the input
            WindowParameters and/or ShadingParameters assigned to it.
        _win_par_: A WindowParameter object that dictates how the window geometries
            will be generated for each of the walls. If None, the window
            parameters will remain unchanged across the input object.
        _shd_par_: A ShadingParameter objects that dictate how the shade geometries
            will be generated for each of the walls. If None, the shading
            parameters will remain unchanged across the input object.
    
    Returns:
        df_obj: The input Dragonfly object with the WindowParameters and/or
            ShadingParameters assigned to it.
"""

ghenv.Component.Name = "DF Apply Facade Parameters"
ghenv.Component.NickName = 'ApplyFacadePar'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    df_obj = [obj.duplicate() for obj in _df_obj]
    
    # add the window parameters
    if _win_par_ is not None:
        for obj in df_obj:
            obj.set_outdoor_window_parameters(_win_par_)
    
    # add the shading parameters
    if _shd_par_ is not None:
        for obj in df_obj:
            obj.set_outdoor_shading_parameters(_shd_par_)
