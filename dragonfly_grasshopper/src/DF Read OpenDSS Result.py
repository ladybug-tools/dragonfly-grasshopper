# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Parse any CSV file output from an OpenDSS simulation.

-
    Args:
        _dss_csv: The file path of any CSV result file that has been generated from
            an OpenDSS simulation. This can be either a Building CSV with voltage
            information or transformers/connectors with loading information.

    Returns:
        values: A list of data collections containing the numerical results in each CSV.
        condition: A list of data collections noting the condition of a given object.
            For example, whether the object is over or under voltage (in the
            case of a building) or whether it is overloaded (in the case of
            a transformer or electrical connector).
"""

ghenv.Component.Name = 'DF Read OpenDSS Result'
ghenv.Component.NickName = 'OpenDSSResult'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os
import datetime

try:
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.header import Header
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.datatype.generic import GenericType
    from ladybug.datatype.power import Power
    from ladybug.futil import csv_to_matrix
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

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

# data types for the various outputs from OpenDSS
is_over = GenericType('Is Overloaded', 'condition',
                      unit_descr={1: 'Overloaded', 0: 'Normal'})
volt_cond = GenericType('Voltage Condition', 'condition',
                        unit_descr={-1: 'Undervoltage', 0: 'Normal', 1: 'Overvoltage'})
voltage = GenericType('Voltage', 'kV')
power = GenericType('Electric Load', 'kVA')


if all_required_inputs(ghenv.Component):
    values, condition = [], []
    for result_file in _dss_csv:
        # parse the data and figure out the timeseries properties
        data = csv_to_matrix(result_file)
        csv_header = data.pop(0)
        a_period = extract_analysis_period(data)

        # figure out the type of object to write into the metadata
        obj_name = os.path.basename(result_file).replace('.csv', '')
        if obj_name.startswith('Line.'):
            obj_name = obj_name.replace('Line.', '')
            obj_type = 'Electrical Connector'
        elif obj_name.startswith('Transformer.'):
            obj_name = obj_name.replace('Transformer.', '')
            obj_type = 'Transformer'
        else:
            obj_type = 'Building'
        metadata = {'type': obj_type, 'name': obj_name}

        # output the data collection of values
        result_vals = [float(data[i][1]) for i in range(len(data))]
        data_t = voltage if 'voltage' in csv_header[1] else power
        header = Header(data_t, data_t.units[0], a_period, metadata)
        values.append(HourlyContinuousCollection(header, result_vals))

        # output the data collection of values
        if len(data[0]) == 4:  # building voltage results
            cond_vals = []
            for row in data:
                cond = 0 if row[2] == 'False' else 1
                if cond != 1 and row[3] == 'True\n':
                    cond = -1
                cond_vals.append(cond)
            header = Header(volt_cond, volt_cond.units[0], a_period, metadata)
            condition.append(HourlyContinuousCollection(header, cond_vals))
        else:  # transformer or connector load
            cond_vals = []
            for row in data:
                cond = 0 if row[2] == 'False\n' else 1
                cond_vals.append(cond)
            header = Header(is_over, is_over.units[0], a_period, metadata)
            condition.append(HourlyContinuousCollection(header, cond_vals))
