# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Export Dragonfly Typologies to UrbanOpt for energy simulation.
-

    Args:
        _typologies: ...
    Returns:
        report: ...
        ----------: ...
        json_files: ...
        osm_files: ...
"""

ghenv.Component.Name = "DF Export to UrbanOpt"
ghenv.Component.NickName = 'UrbanOpt'
ghenv.Component.Message = 'VER 0.0.04\nAPR_04_2019'
ghenv.Component.Category = "DragonflyPlus"
ghenv.Component.SubCategory = "01::Urban Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "1"




osm_files = 'C:/Users/USERNAME/ladybug/unnamed/test.osm'