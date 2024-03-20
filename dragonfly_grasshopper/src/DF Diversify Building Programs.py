# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Diversify the ProgramTypes assigned to a Building's Room2Ds.
_
This is useful when attempting to account for the fact that not all rooms are
used by occupants according to a strict scheduled regimen. Some rooms will be
used more than expected and others less.
_
This component uses a random number generator and gaussian distribution to
generate loads that vary about the original "mean" programs. Note that the
randomly generated values assigned by this component will be different every
time that this component is run unless and input for seed_ has been specified.
_
In addition to diversifying load values, approximately 2/3 of the schedules
in the resulting Room2Ds will be offset from the mean by the input
schedule_offset (1/3 ahead and another 1/3 behind).
-

    Args:
        _building: A Dragonfly Building, which will have its room programs diversified.
        _occ_stdev_: A number between 0 and 100 for the percent of the occupancy
            people_per_area representing one standard deviation
            of diversification from the mean. (Default 20 percent).
        _lighting_stdev_: A number between 0 and 100 for the percent of the
            lighting watts_per_area representing one standard deviation
            of diversification from the mean. (Default 20 percent).
        _electric_stdev_: A number between 0 and 100 for the percent of the electric
            equipment watts_per_area representing one standard deviation
            of diversification from the mean. (Default 20 percent).
        _gas_stdev_: A number between 0 and 100 for the percent of the gas equipment
            watts_per_area representing one standard deviation of
            diversification from the mean. (Default 20 percent).
        _hot_wtr_stdev_: A number between 0 and 100 for the percent of the
            service hot water flow_per_area representing one standard deviation
            of diversification from the mean. (Default 20 percent).
        _infilt_stdev_: A number between 0 and 100 for the percent of the infiltration
            flow_per_exterior_area representing one standard deviation of
            diversification from the mean. (Default 20 percent).
        _sched_offset_: A positive integer for the number of timesteps at which all
            schedules of the resulting programs will be shifted - roughly 1/3 of
            the programs ahead and another 1/3 behind. (Default: 1).
        _timestep_: An integer for the number of timesteps per hour at which the
            shifting is occurring. This must be a value between 1 and 60, which
            is evenly divisible by 60. 1 indicates that each step is an hour
            while 60 indicates that each step is a minute. (Default: 1).
        seed_: An optional integer to set the seed of the random number generator
            that is diversifying the loads. Setting a value here will ensure
            that the same "random" values are assigned every time that this
            component is run, making comparison of energy simulation results
            easier. If not set, the loads assigned by this component will be
            different every time it is run.

    Returns:
        building: The input Dragonfly Building with its programs diversified. The
            diversified values can be checked by using the "DF Color Room2D
            Attributes" component.
"""

ghenv.Component.Name = 'DF Diversify Building Programs'
ghenv.Component.NickName = 'DiversifyBldg'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import random

try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import ladybug-rhino
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the dragonfly-energy extension
    import dragonfly_energy
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy energy:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default values for any unspecified inputs
    _occ_stdev_ = 20 if _occ_stdev_ is None else _occ_stdev_
    _lighting_stdev_ = 20 if _lighting_stdev_ is None else _lighting_stdev_
    _electric_stdev_ = 20 if _electric_stdev_ is None else _electric_stdev_
    _gas_stdev_ = 20 if _gas_stdev_ is None else _gas_stdev_
    _hot_wtr_stdev_ = 20 if _hot_wtr_stdev_ is None else _hot_wtr_stdev_
    _infilt_stdev_ = 20 if _infilt_stdev_ is None else _infilt_stdev_
    _sched_offset_ = 1 if _sched_offset_ is None else _sched_offset_
    _timestep_ = 1 if _timestep_ is None else _timestep_

    # set the seed if specified
    if seed_ is not None:
        random.seed(seed_)

    # duplicate the initial objects and diversify the programs
    assert isinstance(_building, Building), \
        'Expected Dragonfly Building. Got {}.'.format(type(_building))
    building = _building.duplicate()
    building.properties.energy.diversify(
        _occ_stdev_, _lighting_stdev_, _electric_stdev_, _gas_stdev_,
        _hot_wtr_stdev_, _infilt_stdev_, _sched_offset_, _timestep_)
