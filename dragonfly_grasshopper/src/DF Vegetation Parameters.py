# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create VegetationParameters representing the behavior of vegetation within an
urban area.
-

    Args:
        _albedo_: A number between 0 and 1 that represents the ratio of reflected
            radiation from vegetated surfaces to incident radiation upon
            them. (Default: 0.25)
        _start_month_: An integer from 1 to 12 that represents the month at which
            vegetation evapostranspiration begins (leaves come out). By
            default, the month will be automatically determined by analyzing
            the epw to see which months have an average monthly temperature
            above 10C.
        _end_month_: An integer from 1 to 12 that represents the month at which
            vegetation evapostranspiration ends (leaves fall off). By
            default, the month will be automatically determined by analyzing
            the epw to see which months have an average monthly temperature
            above 10C.
        _tree_latent_: A number between 0 and 1 that represents
            the the fraction of absorbed solar energy by trees that
            is given off as latent heat (evapotranspiration). Currently,
            this does not affect the moisture balance in the uwg but
            it will affect the temperature. (Default: 0.7).
        _grass_latent_: A number between 0 and 1 that represents
            the the fraction of absorbed solar energy by grass that is
            given off as latent heat (evapotranspiration). Currently,
            this does not affect the moisture balance in the uwg but
            it will affect the temperature. (Default: 0.5).

    Returns:
        veg_par: Vegetation parameters that can be plugged into the "DF UWG Simulation
            Parameter" component to specify the behavior of vegetation in
            the simulation.
"""

ghenv.Component.Name = "DF Vegetation Parameters"
ghenv.Component.NickName = 'VegetationPar'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the dragonfly_uwg dependencies
    from dragonfly_uwg.simulation.vegetation import VegetationParameter
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_uwg:\n\t{}'.format(e))

try:  # import the honeybee dependencies
    from honeybee.altnumber import autocalculate
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))


# process default values
_albedo_ = _albedo_ if _albedo_ is not None else 0.25
_start_month_ = _start_month_ if _start_month_ is not None else autocalculate
_end_month_ = _end_month_ if _end_month_ is not None else autocalculate
_tree_latent_ = _tree_latent_ if _tree_latent_ is not None else 0.7
_grass_latent_ = _grass_latent_ if _grass_latent_ is not None else 0.5

# create the traffic parameters
veg_par = VegetationParameter(
    _albedo_, _start_month_, _end_month_, _tree_latent_, _grass_latent_)
