# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Deconstruct an OpenDSS Wire, PowerLine, or Transformer Properties into its constituient
attributes and values.
-

    Args:
        _dss_obj: An OpenDSS Wire, PowerLine, or Transformer Properties to be deconstructed.
            This can also be text for a Wire, PowerLine, or Transformer to be
            looked up in the library.

    Returns:
        values: List of values for the attributes that define the OpenDSS object.
        attr_names: List of text that is the same length as the values, which
            notes the attribute name for each value.
"""

ghenv.Component.Name = 'DF Deconstruct OpenDSS'
ghenv.Component.NickName = 'DecnstrDSS'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '4 :: Electric Grid'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the dragonfly_energy dependencies
    from dragonfly_energy.opendss.lib.wires import wire_by_identifier
    from dragonfly_energy.opendss.lib.powerlines import power_line_by_identifier
    from dragonfly_energy.opendss.lib.transformers import transformer_prop_by_identifier
    from dragonfly_energy.opendss.wire import Wire
    from dragonfly_energy.opendss.powerline import PowerLine
    from dragonfly_energy.opendss.transformerprop import TransformerProperties
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

WIRE_PROPS = (
    'display_name', 'ampacity', 'geometrical_mean_radius', 'resistance',
    'diameter', 'voltage_level', 'wire_type', 'concentric_properties')
LINE_PROPS = (
    'display_name', 'wire_count', 'wire_ids', 'heights', 'relative_xs',
    'phases', 'phase_count', 'nominal_voltage')
XFORM_PROPS = (
    'display_name', 'kva', 'resistance', 'reactance', 'phase_count',
    'high_voltage', 'low_voltage', 'is_center_tap', 'connection')


if all_required_inputs(ghenv.Component):
    # check the input
    if isinstance(_dss_obj, str):
        try:
            _dss_obj = transformer_prop_by_identifier(_dss_obj)
        except ValueError:
            try:
                _dss_obj = power_line_by_identifier(_dss_obj)
            except ValueError:
                _dss_obj = wire_by_identifier(_dss_obj)

    # get the attributes and values
    values, attr_names = [], []
    if isinstance(_dss_obj, Wire):
        for atr in WIRE_PROPS:
            values.append(getattr(_dss_obj, atr))
            attr_names.append(atr.replace('_', ' ').title())
    elif isinstance(_dss_obj, PowerLine):
        for atr in LINE_PROPS:
            values.append(str(getattr(_dss_obj, atr)))
            attr_names.append(atr.replace('_', ' ').title())
    elif isinstance(_dss_obj, TransformerProperties):
        for atr in XFORM_PROPS:
            values.append(getattr(_dss_obj, atr))
            attr_names.append(atr.replace('_', ' ').title())
