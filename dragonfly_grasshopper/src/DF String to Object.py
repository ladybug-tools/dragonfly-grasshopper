# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Serialize any dragonfly JSON text string back to a dragonfly object.
-
This includes any Model, Building, Story, Room2D, WindowParameter, or ShadingParameter.
-
It also includes any dragonfly energy Material, Construction, ConstructionSet,
Schedule, Load, ProgramType, or Simulation object.
-

    Args:
        _df_str: A text string that completely describes the dragonfly object.
    
    Returns:
        df_obj: A Dragonfly object serialized from the input string.
"""

ghenv.Component.Name = 'DF String to Object'
ghenv.Component.NickName = 'StrToObj'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '2 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:  # import the core dragonfly dependencies
    import dragonfly.dictutil as df_dict_util
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the core honeybee_energy dependencies
    import honeybee_energy.dictutil as energy_dict_util
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import json


if all_required_inputs(ghenv.Component):
    df_dict = json.loads(_df_str)
    df_obj = df_dict_util.dict_to_object(df_dict, False)  # re-serialize as a core object
    if df_obj is None:  # try to re-serialize it as an energy object
        df_obj = energy_dict_util.dict_to_object(df_dict, False)
