# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Define the window opening properties for all apertures of a Dragonfly Building,
Story or Room2D.
-

    Args:
        _df_objs: Dragonfly Buildings, Stories or Room2Ds to which window ventilation
            opening properties will be assigned. Note that this component
            assigns such properties to all Outdoor Apertures on the rooms.
        _vent_cntrl: A Ventilation Control object from the "HB Ventilation Control"
            component, which dictates the opening behaviour of the Room's apertures.
        _fract_area_oper_: A number between 0.0 and 1.0 for the fraction of the
            window area that is operable. (Default: 0.5, typical of sliding windows).
        _fract_height_oper_: A number between 0.0 and 1.0 for the fraction
            of the distance from the bottom of the window to the top that is
            operable. (Default: 1.0, typical of windows that slide horizontally).
        _discharge_coeff_: A number between 0.0 and 1.0 that will be multipled
            by the area of the window in the stack (buoyancy-driven) part of the
            equation to account for additional friction from window geometry,
            insect screens, etc. (Default: 0.45, for unobstructed windows with
            insect screens). This value should be lowered if windows are of an
            awning or casement type and not allowed to fully open. Some common
            values for this coefficient include the following.
            -
                * 0.0 - Completely discount stack ventilation from the calculation.
                * 0.45 - For unobstructed windows with an insect screen.
                * 0.65 - For unobstructed windows with NO insect screen.
        _wind_cross_vent_: Boolean to indicate if there is an opening of roughly
            equal area on the opposite side of the Room such that wind-driven
            cross ventilation will be induced. If False, the assumption is that
            the operable area is primarily on one side of the Room and there is
            no wind-driven ventilation. (Default: False)

    Returns:
        df_objs: The input Dragonfly object with their window-opening properties edited.
"""

ghenv.Component.Name = 'DF Window Opening'
ghenv.Component.NickName = 'DFWindowOpen'
ghenv.Component.Message = '1.3.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    from honeybee_energy.ventcool.opening import VentilationOpening
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
    from dragonfly.story import Story
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the dragonfly-energy extension
    import dragonfly_energy
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def extract_room2ds(obj):
    """Get all of the Room2Ds assinged to a given dragonfly object."""
    if isinstance(obj, Building):
        return obj.unique_room_2ds
    elif isinstance(obj, Story):
        return obj.room_2ds
    return [obj]  # assume that the object is already a Room2D


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    df_objs = [obj.duplicate() for obj in _df_objs]

    # create the base ventilation opening
    f_area = 0.5 if _fract_area_oper_ is None else _fract_area_oper_
    f_height = 1.0 if _fract_height_oper_ is None else _fract_height_oper_
    discharge = 0.45 if _discharge_coeff_ is None else _discharge_coeff_
    cross_vent = False if _wind_cross_vent_ is None else _wind_cross_vent_
    vent_open = VentilationOpening(f_area, f_height, discharge, cross_vent)

    for obj in df_objs:
        for room in extract_room2ds(obj):
            room.properties.energy.window_vent_control = _vent_cntrl
            room.properties.energy.window_vent_opening = vent_open