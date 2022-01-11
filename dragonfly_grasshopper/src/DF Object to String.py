# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Serialize any dragonfly object to a JSON text string. You can use "DF String to Object"
component to load the objects from the file back.
-
This includes any Model, Building, Story, Room2D, WindowParameter, or ShadingParameter.
-
It also includes any honeybee energy Material, Construction, ConstructionSet,
Schedule, Load, ProgramType, or Simulation object.
-

    Args:
        _df_obj: A Dragonfly object to be serialized to a string.
    
    Returns:
        df_str: A text string that completely describes the honeybee object.
            This can be serialized back into a honeybee object using the "HB
            String to Object" coponent.
"""

ghenv.Component.Name = 'DF Object to String'
ghenv.Component.NickName = 'ObjToStr'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '2 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import json


if all_required_inputs(ghenv.Component):
    df_str = json.dumps(_df_obj.to_dict(), indent=4)
