# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run a an URBANopt geoJSON and scenario through RNM.
_
The geoJSON must have a valid Road Network assigned to it in order to run
correctly through RNM.
-

    Args:
        _geojson: The path to an URBANopt-compatible geoJSON file. This geoJSON
            file can be obtained form the "DF Model to geoJSON" component.
            The geoJSON must have a valid Road Network assigned to it
            in order to run correctly through RNM.
        _scenario: The path to an URBANopt .csv file for the scenario. This CSV
            file can be obtained form the "DF Run URBANopt" component.
        _ug_ratio_: A number between 0 and 1 for the ratio of overall cables that are
            underground vs. overhead in the analysis. (Default: 0.9).
        include_hv_: A boolean to note whether high voltage consumers should be
            included in the analysis. (Default: False).
        nodes_per_bldg_: A positive integer for the maximum number of low voltage
            nodes to represent a single building. (Default: 1).
        _run: Set to "True" to run the geojson and scenario through RNM.

    Returns:
        report: Reports, errors, warnings, etc.
        network: The ElectricalNetwork object output from the RNM simulation. The
            properties of this object can be visualized with the "DF Color
            Network Attributes" component. However, the network can not be
            used for OpenDSS simulation (the dss_files below should be used
            for this purpose).
        dss_results: Path to the folder containing all of the OpenDSS files.
"""

ghenv.Component.Name = 'DF Run RNM'
ghenv.Component.NickName = 'RunRNM'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: Electric Grid'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os

try:
    from ladybug.config import folders as lb_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the dragonfly_energy dependencies
    from dragonfly_energy.run import run_default_report, run_rnm
    from dragonfly_energy.opendss.network import ElectricalNetwork
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.config import units_system
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # set default values
    ug_ratio = 0.9 if _ug_ratio_ is None else _ug_ratio_
    lv_only = True if include_hv_ is None else not include_hv_
    nodes_per_bldg = 1 if nodes_per_bldg_ is None else nodes_per_bldg_

    # generate the default scenario report
    def_report = os.path.join(os.path.dirname(_geojson), 'run',
                              'honeybee_scenario', 'default_scenario_report.csv')
    if not os.path.isfile(def_report):
        run_default_report(_geojson, _scenario)

    # execute the simulation with URBANopt CLI
    results = run_rnm(_geojson, _scenario, ug_ratio, lv_only, nodes_per_bldg)

    # add the kVA to the output GeoJSON file
    if results is not None:
        dss_results = os.path.join(results, 'OpenDSS')
        geo_file = os.path.join(results, 'GeoJSON', 'Distribution_system.json')
        network = ElectricalNetwork.from_rnm_geojson(geo_file, units=units_system())
