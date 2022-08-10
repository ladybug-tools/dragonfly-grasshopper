# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
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
        _run: Set to "True" to run the geojson and scenario through RNM.

    Returns:
        report: Reports, errors, warnings, etc.
        results: Path to a folder that contains all of the RNM output files.
"""

ghenv.Component.Name = 'DF Run RNM'
ghenv.Component.NickName = 'RunRNM'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

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
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # generate the default scenario report
    def_report = os.path.join(os.path.dirname(_geojson), 'run',
                              'honeybee_scenario', 'default_scenario_report.csv')
    if not os.path.isfile(def_report):
        run_default_report(_geojson, _scenario)

    # execute the simulation with URBANopt CLI
    results = run_rnm(_geojson, _scenario)
