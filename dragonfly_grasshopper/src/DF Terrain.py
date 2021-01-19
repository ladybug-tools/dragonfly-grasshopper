# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a Terrain object representing the land on which an urban area sits.
_
This includes both the geometry and the properties of the pavement within
the urban area.
-

    Args:
        _terrain_geo: An array of Breps or meshes that together
            represent the terrian. This should include the entire area of the
            site, including that beneath building footprints.
        _albedo_: A number between 0 and 1 that represents the albedo (reflectivity) of
            the pavement. (Default: 0.1, typical of fresh asphalt).
        _thickness_: A number that represents the thickness of the pavement material
            in meters. (Default: 0.5 meters).
        _conductivity_: A number representing the conductivity of the pavement
            material in W/m-K. (Default: 1 W/m-K, typical of asphalt).
        _vol_heat_cap_: A number representing the volumetric heat capacity of the
            pavement material in J/m3-K. This is the number of joules
            needed to raise one cubic meter of the material by 1 degree
            Kelvin. (Default: 1.6e6 J/m3-K, typical of asphalt).

    Returns:
        terrain: A Terrain object that can be plugged into the "DF Assign Model
            UWG Properties" component to specify the terrain of an urban area.

"""

ghenv.Component.Name = 'DF Terrain'
ghenv.Component.NickName = 'Terrain'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the dragonfly_uwg dependencies
    from dragonfly_uwg.terrain import Terrain
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_uwg:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # process the input geometry
    geo = [face for rh_geo in _terrain_geo for face in to_face3d(rh_geo)]
    
    # assign default values for the pvement properties
    _albedo_ = _albedo_ if _albedo_ is not None else 0.1
    _thickness_ = _thickness_ if _thickness_ is not None else 0.5
    _conductivity_ = _conductivity_ if _conductivity_ is not None else 1.0
    _vol_heat_cap_ = _vol_heat_cap_ if _vol_heat_cap_ is not None else 1.6e6

    # create the terrain
    terrain = Terrain(geo, _albedo_, _thickness_, _conductivity_, _vol_heat_cap_)
