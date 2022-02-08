# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

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
        _pv_: A number for the maximum installed kilowatts of roof-mounted photovoltaic
            power. (Default: 1000000000).
        _pv_ground_: A number for the maximum installed kilowatts of ground-mounted
            photovoltaic power. (Default: 1000000000).
        _storage_: A number for the maximum installed kilowatts of electrical
            storage. (Default: 1000000).
        _generator_: A number for the maximum installed kilowatts of generator power.
            Note that generators are only used in outages. (Default: 1000000000).
        _run: Set to "True" to run the geojson and scenario through REopt.
            This will ensure that all result files appear in their respective
            outputs from this component.

    Returns:
        report: Reports, errors, warnings, etc.
        values: A list of numerical values from the REopt analysis, all related to
            the cost and financial outcome of the optimization. These values
            align with the parameters below.
        parameters: A list of text that correspond to the numerical values above.
            Each text item explains what the numerical value means.
        wind: A number for the optimal capacity of wind power that should be installed
            in kW. This will be null unless a non-zero value is specified for
            the input _wind_.
        pv: A number for the optimal capacity of roof-mounted photovlotaic power that
            should be installed in kW.
        pv_ground: A number for the optimal capacity of ground-mounted photovlotaic power
            that should be installed in kW.
        storage: A list of two numbers ordered as follows.
            _
            - A number for the optimal dicharge capacity of battery storage
            that should be installed in kW.
            _
            - A number for the optimal total capacity of battery storage
            that should be installed in kWh.
        generator: A number for the optimal capacity of generator power that should be
            installed in kW. This will be null unless a non-zero value is
            specified for the input _generator_.
        data: A list of hourly continuous data collections containing the detailed
            timeseties results of the REopt analysis.
"""

ghenv.Component.Name = 'DF Run REopt'
ghenv.Component.NickName = 'RunREopt'
ghenv.Component.Message = '1.4.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import json
import datetime

try:
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.header import Header
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.datatype.power import Power
    from ladybug.datatype.fraction import Fraction
    from ladybug.futil import csv_to_matrix
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the dragonfly_energy dependencies
    from dragonfly_energy.reopt import REoptParameter
    from dragonfly_energy.run import run_reopt
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def date_str_to_datetime(date_str):
    """Get a datetime object from a string."""
    return datetime.datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')


def extract_analysis_period(data):
    """Extract an AnalysisPeriod from CSV data."""
    dts = [date_str_to_datetime(data[i][0]) for i in (0, 1, -2)]
    timestep = int(3600/ (dts[1] - dts[0]).total_seconds())
    leap_year = True if dts[0].year % 4 == 0 else False
    a_period = AnalysisPeriod(
        dts[0].month, dts[0].day, 0, dts[-1].month, dts[-1].day, 23,
        timestep=timestep, is_leap_year=leap_year)
    return a_period


if all_required_inputs(ghenv.Component) and _run:
    # generate default REoptParameter if None are input to the component
    if _financial_par_ is None:
        _financial_par_ = REoptParameter()

    # set the ax sizes for the variou energy sources
    _financial_par_.wind_parameter.max_kw = _wind_ if _wind_ is not None else 0
    _financial_par_.pv_parameter.max_kw = _pv_ if _pv_ is not None else 1000000000
    _financial_par_.pv_parameter.max_kw_ground = _pv_ground_ if _pv_ground_ is not None else 1000000000
    _financial_par_.storage_parameter.max_kw = _storage_ if _storage_ is not None else 1000000
    _financial_par_.generator_parameter.max_kw = _generator_ if _generator_ is not None else 1000000000

    # execute the simulation with URBANopt CLI
    re_csv, re_json = run_reopt(_geojson, _scenario, _urdb_label, _financial_par_)

    # parse the JSON results of the simulation if successful
    if os.path.isfile(re_json):
        with open(re_json) as json_file:
            re_data = json.load(json_file)
        values, parameters = [], []
        for key, val in re_data['scenario_report']['distributed_generation'].items():
            if isinstance(val, (float, int)):
                values.append(val)
                parameters.append(key.replace('_', ' ').title())
            elif key == 'wind' and len(val) != 0:
                wind = val[0]['size_kw']
            elif key == 'solar_pv' and len(val) != 0:
                pv = val[0]['size_kw']
                pv_ground = val[1]['size_kw']
            elif key == 'storage' and len(val) != 0:
                storage = [val[0]['size_kw'], val[0]['size_kwh']]
            elif key == 'generator' and len(val) != 0:
                generator = val[0]['size_kw']

    # parse the CSV results of the simulation if successful
    if os.path.isfile(re_csv):
        data = []  # final list of data to be collected
        # parse the data and figure out the timeseries properties
        csv_data = csv_to_matrix(re_csv)
        csv_header = csv_data.pop(0)
        a_period = extract_analysis_period(csv_data)
        for col, col_name in zip(zip(*csv_data), csv_header):
            if col_name.startswith('REopt:'):
                # figure out the type of object to write into the metadata
                base_name = col_name.replace('REopt:', '').split(':')
                end_name, units_init = base_name[-1].split('(')
                units_init = units_init.replace(')', '')
                if units_init == 'kw':
                    units, data_type = 'kW', Power()
                elif units_init == 'pct':
                    units, data_type = 'fraction', Fraction()
                else:
                    continue
                metadata = {'type': ':'.join(base_name[:-1] + [end_name])}
                # create the final data collections
                result_vals = [float(val) for val in col]
                header = Header(data_type, units, a_period, metadata)
                data.append(HourlyContinuousCollection(header, result_vals))
