# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create Dragonfly skylight parameters with instructions for generating skylights
according to a ratio with the base Roof surface.
-

    Args:
        _ratio: A number between 0 and 0.75 for the ratio between the skylight
            area and the total Roof face area.
        spacing_: A number for the spacing between the centers of each grid cell.
            This should be less than half of the dimension of the Roof geometry
            if multiple, evenly-spaced skylights are desired. If None, a spacing
            of one half the smaller dimension of the parent Roof will be automatically
            assumed. (Default: None).

    Returns:
        skylight: Skylight Parameters that can be applied to a Dragonfly object
            using the "DF Apply Facade Parameters" component.
"""

ghenv.Component.Name = "DF Gridded Skylight Parameters"
ghenv.Component.NickName = 'GridSkyPar'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "6"

try:  # import the core dragonfly dependencies
    from dragonfly.skylightparameter import GriddedSkylightRatio
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    if _ratio != 0:
        skylight = GriddedSkylightRatio(_ratio, spacing_)