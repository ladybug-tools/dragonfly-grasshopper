# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Edit the properties of a Dragonfly Building that affect simulation with to the Urban
Weather Generator (UWG).
-

    Args:
        _building: A Dragonfly Building which is to have its Urban Weather Generator (UWG)
            properties assigned.
        program_: Text for the name of the building program. Must be one of the
            options below. (Default: LargeOffice).

            * LargeOffice
            * MediumOffice
            * SmallOffice
            * MidriseApartment
            * Retail
            * StripMall
            * PrimarySchool
            * SecondarySchool
            * SmallHotel
            * LargeHotel
            * Hospital
            * Outpatient
            * Warehouse
            * SuperMarket
            * FullServiceRestaurant
            * QuickServiceRestaurant

        vintage_: Text for the vintage of the building. This will be used to set
            default constructions. Must be one of the options below or one of
            the options from the "HB Building Vintages" component, which will
            be mapped to one of the options below. (Default: New).

            * New
            * 1980_Present
            * Pre1980

        fr_canyon_: A number from 0 to 1 that represents the fraction of the building's
            waste heat from air conditioning that gets rejected into the urban
            canyon. (Default: 0.5).
        shgc_: A number from 0 to 1 that represents the SHGC of the building's windows.
            This is used to evaluate the amount of solar heat reflected into the
            street canyon. By default, it will be set by the building vintage
             and the Model climate zone.
        wall_alb_: A number from 0 to 1 that represents the exterior wall albedo
            of the building. By default, it will be set by the building program
            and the DoE commercial reference buildings.
        roof_alb_: A number from 0 to 1 that represents the exterior roof albedo of
            the building. By default, it will be set by the vintage, meaning 0.7
            for New and 0.2 for 1980_Present and Pre1980.
        roof_veg_: A number from 0 to 1 that represents the fraction of the building's
            roofs covered in vegetation. (Default: 0).

    Returns:
        report: ...
        building: The input Dragonfly Building with its UWG properties re-assigned based
            on the input.
"""

ghenv.Component.Name = 'DF Assign Building UWG Properties'
ghenv.Component.NickName = 'BuildingUWG'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the dragonfly dependencies
    from dragonfly.building import Building
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# dictionary to map vintages to acceptable UWG ones
VINTAGE_MAP = {
    'New': 'New',
    '1980_Present': '1980_Present',
    'Pre1980': 'Pre1980',
    '2013': '1980_Present',
    '2010': '1980_Present',
    '2007': '1980_Present',
    '2004': '1980_Present',
    '1980_2004': '1980_Present',
    'pre_1980': 'Pre1980'
}


if all_required_inputs(ghenv.Component):
    # check and duplicate the input
    assert isinstance(_building, Building), \
        'Expected Dragonfly Building. Got {}.'.format(type(_building))
    building = _building.duplicate()

    # assign all of the properties to the building
    if program_ is not None:
        building.properties.uwg.program = program_
    if vintage_ is not None:
        building.properties.uwg.vintage = VINTAGE_MAP[vintage_]
    if fr_canyon_ is not None:
        building.properties.uwg.fract_heat_to_canyon = fr_canyon_
    if shgc_ is not None:
        building.properties.uwg.shgc = shgc_
    if wall_alb_ is not None:
        building.properties.uwg.wall_albedo = wall_alb_
    if roof_alb_ is not None:
        building.properties.uwg.roof_albedo = roof_alb_
    if roof_veg_ is not None:
        building.properties.uwg.roof_veg_fraction = roof_veg_
