# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Write Ladybug DesignDays to a standard .ddy file.
-

    Args:
        _location: A Ladybug Location object describing the location data in the
            weather file.
        _design_days: A list of DesignDay objects representing the design days
            contained within the ddy file.
        _folder_: An optional folder to save the .ddy file.
        _name_: An optional name for this .ddy file.
        _run: Set to "True" to run the component and write the .ddy file.

    Returns:
        ddy_file: A .ddy file path that has been written to your system.
"""

ghenv.Component.Name = 'DF Write DDY'
ghenv.Component.NickName = 'WriteDDY'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '6 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import os

try:
    from ladybug.config import folders
    from ladybug.ddy import DDY
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # default folder and file name
    _folder_ = folders.default_epw_folder if _folder_ is None else _folder_
    if _name_ is None:
        _name_ = 'unnamed.ddy'
    if not _name_.lower().endswith('.ddy'):
        _name_ = _name_ + '.ddy'
    ddy_file = os.path.join(_folder_, _name_)

    # write the DDY file
    ddy_obj = DDY(_location, _design_days)
    ddy_obj.save(ddy_file)