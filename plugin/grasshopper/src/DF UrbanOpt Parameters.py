# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Parameters for export to UrbanOpt.
-

    Args:
        _osm_per_object: ...
    Returns:
        transl_par: ...
"""

ghenv.Component.Name = "DF UrbanOpt Parameters"
ghenv.Component.NickName = 'UrbanOptPar'
ghenv.Component.Message = 'VER 0.0.04\nAPR_04_2019'
ghenv.Component.Category = "DragonflyPlus"
ghenv.Component.SubCategory = "01::Urban Energy"
ghenv.Component.AdditionalHelpFromDocStrings = "2"


transl_par = _osm_per_object_