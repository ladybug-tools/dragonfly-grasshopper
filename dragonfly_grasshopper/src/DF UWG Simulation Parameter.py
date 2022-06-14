# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a simulation parameter object that carries a complete set of Urban Weather
Genreator (UWG) simulation settings and can be plugged into the "DF Run Urban
Weather Generator" component.
-

    Args:
        _run_period_: A Ladybug Analysis Period object to describe the time period over
            which to run the simulation. If None, the simulation will be run for
            the whole year.
        _veg_par_: A VegetationParameter object to specify the behavior of vegetation
            in the urban area. If None, generic vegetation parameters will be
            generated.
        _epw_site_: A ReferenceEPWSite object to specify the properties of the
            reference site where the input rural EPW was recorded. If None,
            generic airport properties will be generated.
        _bnd_layer_: A BoundaryLayerParameter to specify the properties of the urban
            boundary layer. If None, generic boundary layer parameters will
            be generated.

    Returns:
        sim_par: A UWG SimulationParameter object that can be connected to the
            "DF Run Urban Weather Generator" component in order to specify
            UWG simulation settings
"""

ghenv.Component.Name = 'DF UWG Simulation Parameter'
ghenv.Component.NickName = 'UWGSimPar'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the dragonfly uwg dependencies
    from dragonfly_uwg.simulation.runperiod import UWGRunPeriod
    from dragonfly_uwg.simulation.parameter import UWGSimulationParameter
    from dragonfly_uwg.run import run_uwg
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_uwg:\n\t{}'.format(e))


sim_par = UWGSimulationParameter()
if _run_period_:
    sim_par.run_period = UWGRunPeriod.from_analysis_period(_run_period_)
if _veg_par_:
    sim_par.vegetation_parameter = _veg_par_
if _epw_site_:
    sim_par.reference_epw_site = _epw_site_
if _bnd_layer_:
    sim_par.boundary_layer_parameter = _bnd_layer_
