# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Create a Dragonfly Model from a Honeybee Model.
-

    Args:
        _hb_models: A Honeybee Model or list of Honeybee Models to be converted
            to a Dragonfly Model.
        all_3d_to_2d_: Boolean to note whether 3D Rooms should be converted
            into the Room2D format even when this means some loss or
            simplification of geometry (True). If False (the default), only
            the Honeybee Rooms that meet the criteria for translation to
            Room2D without loss of geometry will be converted and the other
            3D Rooms that don't meet this criteria will be stored under the
            Dragonfly Building.room_3ds property in their original Honeybee
            format. (Default: False).
        incl_shades_: Boolean to note whether orphaned shades should be included
            as dragonfly ContextShades. (Default: False).
        _run: Set to "True" to have the Dragonfly Model translated to a series
            of Honeybee Models.

    Returns:
        df_model: A list of dragonfly objects that have been re-serialized from
            the input file.
"""

ghenv.Component.Name = 'DF Model From Honeybee'
ghenv.Component.NickName = 'FromHoneybee'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '2 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.building import Building
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _load:
    method = 'AllRoom2D' if all_3d_to_2d_ else 'ExtrudedOnly'
    if incl_shades_:
        df_model = Model.from_honeybee(_hb_models[0], conversion_method=method)
        for h_model in _hb_models[1:]:
            df_model.add_model(Model.from_honeybee(h_model, conversion_method=method))
    else:
        bldgs = [Building.from_honeybee(h_model, conversion_method=method)
                 for h_model in _hb_models]
        base = _hb_models[0]
        df_model = Model(
            base.identifier, bldgs, units=base.units, tolerance=base.tolerance,
            angle_tolerance=base.angle_tolerance)
