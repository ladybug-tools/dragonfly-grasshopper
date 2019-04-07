# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate boundary layer parameters that can be plugged into the "DF Run Urban Weather Generator" component.  This component is mostly for climatologists, meteorologists and urban weather experts and probably does not have to be used for most simulations.
-

    Args:
        _day_height_: A number that represents the height in meters of the urban boundary layer during the daytime. This is the height to which the urban meterorological conditions are stable and representative of the overall urban area. Typically, this boundary layer height increases with the height of the buildings.  The default is set to 1000 meters.
        _night_height_: A number that represents the height in meters of the urban boundary layer during the nighttime. This is the height to which the urban meterorological conditions are stable and representative of the overall urban area. Typically, this boundary layer height increases with the height of the buildings.  The default is set to 80 meters.
        _inversion_height_: A number that represents the height at which the vertical profile of potential temperature becomes stable. It is the height at which the profile of air temperature becomes stable. Can be determined by flying helium balloons equipped with temperature sensors and recording the air temperatures at different heights.  The default is set to 150 meters.
        _circulation_coeff_: A number that represents the circulation coefficient.  The default is 1.2 per Bueno, Bruno (2012).
        _exchange_coeff_: A number that represents the exchange coefficient.  The default is 1.0 per Bueno, Bruno (2014).
    Returns:
        bnd_layer_par: A list of refernce EPW site parameters that can be plugged into the "DF Run Urban Weather Generator" component.
"""

ghenv.Component.Name = "DF Boundary Layer Parameters"
ghenv.Component.NickName = 'BndLayerPar'
ghenv.Component.Message = 'VER 0.0.04\nAPR_04_2019'
ghenv.Component.Category = "DragonflyPlus"
ghenv.Component.SubCategory = "02::Urban Weather"
ghenv.Component.AdditionalHelpFromDocStrings = "4"


#Dragonfly check.
init_check = False

if init_check == True:
    bnd_layer_par = df_BndLayerPar(_day_height_, _night_height_, _inversion_height_, 
        _circulation_coeff_, _exchange_coeff_)
