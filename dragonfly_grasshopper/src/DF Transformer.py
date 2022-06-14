# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an OpenDSS Transformer from its footprint geometry (horizontal Rhino surfaces).
-

    Args:
        _geo: A horizontal Rhino surface representing a footprint to be converted
            into a Transformer.
        _properties: Text for the properties of the Transformer to be looked up in the
            TransformerProperties library (the output from the "DF OpenDSS Libraries"
            component). This can also be a custom TransformerProperties object.
        _name_: Text to set the base name for the Transformer, which will also be
            incorporated into unique Transformer identifier. If the name is not
            provided, a random one will be assigned.

    Returns:
        transformer: A Dragonfly Transformer object that can be used within an
            Electrical Network.
"""

ghenv.Component.Name = 'DF Transformer'
ghenv.Component.NickName = 'Transformer'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.opendss.lib.transformers import transformer_prop_by_identifier
    from dragonfly_energy.opendss.transformer import Transformer
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:  # import ladybug-rhino
    from ladybug_rhino.togeometry import to_polygon2d
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list, \
        document_counter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    transformer = []  # list of transformers that will be returned
    polygons = [to_polygon2d(geo) for geo in _geo]  # convert to lb geo
    for i, geo in enumerate(polygons):
        # get the name for the Transformer
        if len(_name_) == 0:  # make a default Transformer name
            display_name = 'Transformer_{}'.format(document_counter('transformer_count'))
        else:
            display_name = '{}_{}'.format(longest_list(_name_, i), i + 1) \
                if len(_name_) != len(polygons) else longest_list(_name_, i)
        name = clean_and_id_string(display_name)

        # get the properties for the transformer
        props = longest_list(_properties, i)
        if isinstance(props, str):
            props = transformer_prop_by_identifier(props)

        # create the Transformer
        trans = Transformer(name, geo, props)
        trans.display_name = display_name
        transformer.append(trans)
