# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Create TrafficParameters representing the traffic within an urban area.
-

    Args:
        _watts_per_area: A number representing the maximum sensible anthropogenic heat
            flux of the urban area in watts per square meter. This is specifcally the
            heat that DOES NOT originate from buildings and mostly includes heat
            from automobiles, street lighting, and human metabolism. If autocalculate,
            it will be estimated frm the average building story count of the model
            hosting the traffic parameters (Default: autocalculate). Values
            for different cities can be found in (Sailor, 2011)[1]. Typical
            values include:

            * 20 W/m2 = A typical downtown area
            * 10 W/m2 = A commercial area in Singapore
            * 8 W/m2 = A typical mixed use part of Toulouse, France
            * 4 W/m2 = A residential area in Singapore

        _weekday_sch_: A list of 24 fractional values that will be multiplied by
            the watts_per_area to produce hourly values for heat on the weekday
            of the simulation. (Default: a typical schedule for a commercial area).
        _saturday_sch_: A list of 24 fractional values that will be multiplied by the
            watts_per_area to produce hourly values for heat on the Saturday
            of the simulation. (Default: a typical schedule for a commercial
            area).
        _sunday_sch_: A list of 24 fractional values that will be
            multiplied by the watts_per_area to produce hourly values for
            heat on the Sunday of the simulation. (Default: a typical schedule
            for a commercial area).

    Returns:
        traffic: Traffic parameters that can be plugged into the "DF Assign Model
            UWG Properties" component to specify the behavior of traffic within
            an urban area.
"""

ghenv.Component.Name = 'DF Traffic Parameters'
ghenv.Component.NickName = 'Traffic'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the dragonfly_uwg dependencies
    from dragonfly_uwg.traffic import TrafficPararameter
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_uwg:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # process default values
    _weekday_sch_ = _weekday_sch_ if len(_weekday_sch_) != 0 else None
    _saturday_sch_ = _saturday_sch_ if len(_saturday_sch_) != 0 else None
    _sunday_sch_ = _sunday_sch_ if len(_sunday_sch_) != 0 else None

    # create the traffic parameters
    traffic = TrafficPararameter(
        _watts_per_area, _weekday_sch_, _saturday_sch_, _sunday_sch_)
