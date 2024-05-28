# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Parse any CSV file output from an OpenDSS simulation.

-
    Args:
        _dss_csv: The file path of any CSV result file that has been generated from
            an OpenDSS simulation. This can be either a Building CSV with voltage
            information or transformers/connectors with loading information.

    Returns:
        factors: A list of data collections containing the dimensionless fractional values
            from the CSV results. For buildings, these represent the voltage
            at a given timestep divided by the standard outlet voltage (120 V).
            For transformers and connectors, these represent the power along
            the wire or transformer divided by the kVA rating of the object.
        condition: A list of data collections noting the condition of a given object.
            For example, whether the object is over or under voltage (in the
            case of a building) or whether it is overloaded (in the case of
            a transformer or electrical connector).
"""

ghenv.Component.Name = 'DF Read OpenDSS Result'
ghenv.Component.NickName = 'OpenDSSResult'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: Electric Grid'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from dragonfly_energy.opendss.result import OpenDSSResult
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    result_obj = OpenDSSResult(_dss_csv)
    factors = result_obj.factor_data
    condition = result_obj.condition_data
