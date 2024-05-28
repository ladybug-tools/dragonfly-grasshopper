# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a GHEDesignParameter object that can be used to customize the criteria used
to design a Ground Heat Exchanger (GHE).
_
The output of this component can be used with either the "DF GHE Designer"
component or the "DF GHE Thermal Loop" component.
-

    Args:
        _flow_rate_: A number for the volumetric design flow rate through each borehole
            of the ground heat exchanger in L/s. (Default: 0.2 L/s).
        _max_eft_: A number for the maximum heat pump entering fluid temperature
            in Celsius. (Default: 35C).
        _min_eft_: A number for the minimum heat pump entering fluid temperature
            in Celsius. (Default: 5C).
        _month_count_: An integer for the number of months over which the simulation
            will be run in order to ensure stable ground temperature
            conditions. (Default: 240).

    Returns:
        design: A GHEDesignParameter object that can be plugged into the "DF GHE Designer"
            component in order to customize the criteria used to design a GHE.
            It can also be plugged into the "DF GHE Thermal Loop" component to
            perform a similar role in a District Energy Simulation (DES) of a
            loop with a ground heat exchanger.
"""

ghenv.Component.Name = 'DF GHE Design Parameter'
ghenv.Component.NickName = 'GHEDesign'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from dragonfly_energy.des.ghe import GHEDesignParameter
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))


flow_rate = _flow_rate_ if _flow_rate_ is not None else 0.2
max_eft = _max_eft_ if _max_eft_ is not None else 35
min_eft = _min_eft_ if _min_eft_ is not None else 5
month_count = _month_count_ if _month_count_ is not None else 240


design = GHEDesignParameter(
    flow_rate=flow_rate, max_eft=max_eft, min_eft=min_eft, month_count=month_count)
