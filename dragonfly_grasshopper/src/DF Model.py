# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a Dragonfly Model, which can be translated to Honeybee model and sent
for simulation.
-

    Args:
        _buildings: A list of Dragonfly Building objects to be added to the Model.
            Note that at least one Building is necessary to make a simulate-able
            energy model.
        context_: Optional Dragonfly ContextShade objects to be added to the Model.
        _north_: A number between 0 and 360 to set the clockwise north
            direction in degrees. This can also be a vector to set the North.
            Default is 0.
        _name_: Text to be used for the name and identifier of the Model. If no
            name is provided, it will be "unnamed".
    
    Returns:
        report: Reports, errors, warnings, etc.
        model: A Dragonfly Model object possessing all of the input geometry
            objects.
"""

ghenv.Component.Name = "DF Model"
ghenv.Component.NickName = 'Model'
ghenv.Component.Message = '0.2.1'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_vector2d
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.config import units_system, tolerance, angle_tolerance
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set a default name
    name = clean_string(_name_) if _name_ is not None else 'unnamed'
    units = units_system()

    # create the model
    model = Model(name, _buildings, context_, units=units, tolerance=tolerance,
                  angle_tolerance=angle_tolerance)

    # set the north if it is not defaulted
    if _north_ is not None:
        try:
            model.north_vector = to_vector2d(_north_)
        except AttributeError:  # north angle instead of vector
            model.north_angle = _north_

