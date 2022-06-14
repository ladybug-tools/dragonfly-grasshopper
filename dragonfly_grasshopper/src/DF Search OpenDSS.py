# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Search for available TransformerProperties, PowerLines, and Wires within the
dragonfly OpenDSS standards library (aka. the URBANopt extended cataolog).
-

    Args:
        keywords_: Optional keywords to be used to narrow down the output list of
            objects. If nothing is input here, all available objects
            will be output.
        join_words_: If False or None, this component will automatically split
            any strings of multiple keywords (spearated by spaces) into separate
            keywords for searching. This results in a greater liklihood of
            finding an item in the search but it may not be appropropriate for
            all cases. You may want to set it to True when you are searching for
            a specific phrase that includes spaces. (Default: False).

    Returns:
        transformers: A list of all transformer properties within the dragonfly OpenDSS
            standards library (filtered by keywords_ if they are input).
        power_lines: A list of all power lines within the dragonfly OpenDSS standards
            library (filtered by keywords_ if they are input).
        wires: A list of all wires within the dragonfly OpenDSS standards
            library (filtered by keywords_ if they are input).
"""

ghenv.Component.Name = "DF Search OpenDSS"
ghenv.Component.NickName = 'SearchOpenDSS'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the honeybee-core dependencies
    from honeybee.search import filter_array_by_keywords
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from dragonfly_energy.opendss.lib.transformers import TRANSFORMER_PROPERTIES
    from dragonfly_energy.opendss.lib.powerlines import POWER_LINES
    from dragonfly_energy.opendss.lib.wires import WIRES
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


if len(keywords_) == 0:
    transformers = sorted(TRANSFORMER_PROPERTIES)
    power_lines = sorted(POWER_LINES)
    wires = sorted(WIRES)
else:
    split_words = True if join_words_ is None else not join_words_
    transformers = sorted(filter_array_by_keywords(TRANSFORMER_PROPERTIES, keywords_, split_words))
    power_lines = sorted(filter_array_by_keywords(POWER_LINES, keywords_, split_words))
    wires = sorted(filter_array_by_keywords(WIRES, keywords_, split_words))
