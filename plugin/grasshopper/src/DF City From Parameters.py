# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate a Dragonfly City object from numerical parameters like building height and site coverage ratio.
_
The ouput of this component can be plugged into the 'Dragonfly_Run Urban Weather Generator' component to morph a rural/airport weather file to reflect the urban climate.
-

    Args:
        _avg_height: The average height of the buildings in the city in meters.
        _site_coverage:  A number between 0 and 1 that represents the fraction of the city terrain that
            the building footprints occupy.  It describes how close the buildings are to one another in the city.
        _facade_to_site: A number that represents the ratio of vertical urban surface area [walls] to 
            the total terrain area of the city.  This value can be greater than 1.
        _bldg_programs: A list of building programs that are within the urban area. 
            These should come from the "DF Bldg Programs" component.
        _bldg_ages: A list of building ares that are within the urban area, which correspond with the _bldg_programs above.
            These should come from the "DF Bldg Age" component.
        _bldg_ratios: A list of values between 0 and 1 that denote the fraction of the total floor area of the urban area
            occupied each of the _bldg_programs above.  The connected values should sum to 1.
        tree_coverage_: An number from 0 to 1 that defines the fraction of the entire urban area
            (including both pavement and roofs) that is covered by trees.  The default is set to 0.
        grass_coverage_: An number from 0 to 1 that defines the fraction of the entire urban area 
            (including both pavement and roofs) that is covered by grass/vegetation.  The default is set to 0.
        --------------------: ...
        _climate_zone: A text string representing the ASHRAE climate zone. (eg. 5A). This is used to set default
            constructions for the buildings in the city.
        _traffic_par: Traffic parameters from the "DF Traffic Parameters" component.  This input is required
            as anthropogenic heat from traffic can significantly affect urban climate and varies widely between
            commerical, residential, and industrial districts.
        vegetation_par_: An optional set of vegetation parameters from the "DF Vegetation Parameters" component.
            If no vegetation parameters are input here, the Dragonfly will use a vegetation albedo of 0.25 and Dragonfly
            will attempt to determine the months in which vegetation is active by looking at the average monthly temperatures
            in the EPW file.
        pavement_par_: An optional set of pavement parameters from the "DF Pavement Parameters" component.  If no
            paramters are plugged in here, it will be assumed that all pavement is asphalt.
        --------------------: ...
        _run: Set to 'True' to run the component and generate the Dragonfly city from the connected inputs.
    Returns:
        read_me: ...
        ----------------: ...
        DF_city: A Drafongfly city objectthat can be plugged into the "DF Run Urban Weather Generator" component.
"""

ghenv.Component.Name = "DF City From Parameters"
ghenv.Component.NickName = 'CityFromPar'
ghenv.Component.Message = 'VER 0.0.04\nAPR_04_2019'
ghenv.Component.Category = "DragonflyPlus"
ghenv.Component.SubCategory = "02::Urban Weather"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

from itertools import izip

#Dragonfly check.
initCheck = False

if initCheck == True and _run == True:
    assert len(_bldg_programs) == len(_bldg_ages) == len(_bldg_ratios), \
        'The lengths of _bldg_programs, _bldg_ages, and _bldg_ratios lists must match. Got legnths of {} {} {}'.format(
        len(_bldg_programs), len(_bldg_ages), len(_bldg_ratios))
    
    bldg_types = {}
    for prog, age, ratio in izip(_bldg_programs, _bldg_ages, _bldg_ratios):
        bldg_types[prog + ',' + age] = ratio
    
    DF_city = df_City(_avg_height, _site_coverage, _facade_to_site, bldg_types, _climate_zone,
        _traffic_par, tree_coverage_, grass_coverage_, vegetation_par_, pavement_par_)

