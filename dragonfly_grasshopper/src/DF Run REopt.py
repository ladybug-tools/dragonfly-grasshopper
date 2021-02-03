# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Run a an URBANopt geoJSON and scenario through REopt using the URBANopt CLI.
_
This component requires the URBANopt CLI to be installed in order to run.
Installation instructions for the URBANopt CLI can be found at:
https://docs.urbanopt.net/installation/installation.html
-

    Args:
        _geojson: The path to an URBANopt-compatible geoJSON file. This geoJSON
            file can be obtained form the "DF Model to geoJSON" component.
        _scenario: The path to an URBANopt .csv file for the scenario. This CSV
            file can be obtained form the "DF Run URBANopt" component.
        _urdb_label: Text string for the Utility Rate Database (URDB) label for the particular
            electrical utility rate for the optimization. The label is the last
            term of the URL of a utility rate detail page (eg. the urdb label
            at https://openei.org/apps/IURDB/rate/view/5b0d83af5457a3f276733305
            is 5b0d83af5457a3f276733305). Utility rates for specific locations
            can be looked up in the REopt Lite tool (https://reopt.nrel.gov/tool)
            and the label can be obtained by clicking on "Rate Details" link
            for a particular selected rate.
        _financial_par_: A REoptParameter object to describe the financial assumptions
            of the REopt analysis. This can be obtained from the "DF REopt
            Financial Parameters" component. If None, some default parameters
            will be generated for a typical analysis. (Default: None).
        _wind_: A number for the maximum installed kilowatts of wind power. (Default: 0).
        _pv_: A number for the maximum installed kilowatts of photovoltaic
            power. (Default: 1000000000).
        _storage_: A number for the maximum installed kilowatts of electrical
            storage. (Default: 1000000).
        _generator_: A number for the maximum installed kilowatts of generator power.
            Note that generators are only used in outages. (Default: 1000000000).
        _run: Set to "True" to run the geojson and scenario through REopt.
            This will ensure that all result files appear in their respective
            outputs from this component.

    Returns:
        report: Reports, errors, warnings, etc.
        scenario: File path to the URBANopt scenario CSV used as input for the
            URBANopt CLI run.
        csv: Path to a CSV file containing scenario optimization results.
        json: Path to a JSON file containing scenario optimization results.
"""

ghenv.Component.Name = 'DF Run REopt'
ghenv.Component.NickName = 'RunREopt'
ghenv.Component.Message = '1.1.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '1'


try:  # import the dragonfly_energy dependencies
    from dragonfly_energy.reopt import REoptParameter
    from dragonfly_energy.run import run_reopt
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # generate default REoptParameter if None are input to the component
    if _financial_par_ is None:
        _financial_par_ = REoptParameter()

    # set the ax sizes for the variou energy sources
    _financial_par_.wind_parameter.max_kw = _wind_ if _wind_ is not None else 0
    _financial_par_.pv_parameter.max_kw = _wind_ if _wind_ is not None else 1000000000
    _financial_par_.storage_parameter.max_kw = _wind_ if _wind_ is not None else 1000000
    _financial_par_.generator_parameter.max_kw = _wind_ if _wind_ is not None else 1000000000

    # execute the simulation with URBANopt CLI
    csv, json = run_reopt(_geojson, _scenario, _urdb_label, _financial_par_)
