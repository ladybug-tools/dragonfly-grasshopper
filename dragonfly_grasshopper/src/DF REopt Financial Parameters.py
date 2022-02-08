# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Customize the financial settings of a REopt analysis.
-

    Args:
        _years_: An integer for the number of years over which cost will
            be optimized. (Default: 25).
        _escalation_: A number between 0 and 1 for the escalation rate over
            the analysis. (Default: 0.023).
        _tax_: A number between 0 and 1 for the rate at which the owner/host
            of the system is taxed. (Default: 0.26).
        _discount_: A number between 0 and 1 for the discount rate for the
            owner/host of the system. (Default: 0.083).
        _wind_cost_: A number for the installation cost of wind power in US dollars
            per kW. (Default: 3013).
        _pv_cost_: A number for the installation cost of photovoltaic power in US
            dollars per kW. (Default: 1600).
        _pv_grnd_cost_: A number for the installation cost of photovoltaic power in US
            dollars per kW. (Default: 2200).
        _storage_cost_: A number for the installation cost of power storage in US
            dollars per kW. (Default: 840).
        _gener_cost_: A number for the installation cost of generators in US dollars
            per kW. (Default: 500).

    Returns:
        financial_par: A REoptParameter object that can be plugged into the 'DF
            Run REopt' component.
"""

ghenv.Component.Name = 'DF REopt Financial Parameters'
ghenv.Component.NickName = 'FinancialPar'
ghenv.Component.Message = '1.4.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the dragonfly_energy dependencies
    from dragonfly_energy.reopt import REoptParameter
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))


financial_par = REoptParameter()

if _years_ is not None:
    financial_par.financial_parameter.analysis_years = _years_
if _escalation_ is not None:
    financial_par.financial_parameter.escalation_rate = _escalation_
if _tax_ is not None:
    financial_par.financial_parameter.tax_rate = _tax_
if _discount_ is not None:
    financial_par.financial_parameter.discount_rate = _discount_
if _wind_cost_ is not None:
    financial_par.wind_parameter.dollars_per_kw = _wind_cost_
if _pv_cost_ is not None:
    financial_par.pv_parameter.dollars_per_kw = _pv_cost_
if _pv_grnd_cost_ is not None:
    financial_par.pv_parameter.dollars_per_kw_ground = _pv_grnd_cost_
if _storage_cost_ is not None:
    financial_par.storage_parameter.dollars_per_kw = _storage_cost_
if _gener_cost_ is not None:
    financial_par.generator_parameter.dollars_per_kw = _gener_cost_
