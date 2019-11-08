# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert a set of Dragonfly Buildings into Honeybee Models.
-

    Args:
        _buildings: A list of Dragonfly Building objects to be converted into
            Honeybee Models.
        context_: Optional Honeybee Shade objects to be added as context Shade
            to all of the output Honeybee Models. Note that this shade does not
            use the input shade_dist_.
        _obj_per_model_: Text to describe how the input Buildings should be divided
            across the output Models. Default: 'Building'. Choose from the
            following options:
                * District - All buildings will be added to a single Honeybee Model.
                    Such a Model can take a long time to simulate so this is only
                    recommended for small numbers of buildings.
                * Building - Each input building will be exported into its own Model.
                    For each Model, the other buildings input to this component will
                    appear as context shade geometry. Thus, each Model is its own
                    simulate-able unit.
        use_multiplier_: If True, the multipliers on each Building's Stories will be
            passed along to the generated Honeybee Room objects, indicating the
            simulation will be run once for each unique room and then results
            will be multiplied. If False, full geometry objects will be written
            for each and every story in the building that and all resulting
            multipliers will be 1. Default: True.
        shade_dist_: An optional number to note the distance beyond which other
            buildings' shade should not be exported into a given Model. This is
            helpful for reducing the simulation run time of each Model when other
            connected buildings are too far away to have a meaningful impact on
            the results. If None, all other buildings will be included as context
            shade in each and every Model. Set to 0 to exclude all neighboring
            buildings from the resulting models. Default: None.
        _north_: A number between 0 and 360 to set the clockwise north
            direction in degrees. This can also be a vector to set the North.
            Default is 0.
        _run: Set to "True" to run the component and create Honeybee Models.
    
    Returns:
        report: Reports, errors, warnings, etc.
        models: Honeybee Model objects derived from the input _buildings. These
            Models are ready to be simulated in either an Energy or Radiance
            simulation or they can be edited further with the Honeybee
            components.
"""

ghenv.Component.Name = "DF Building To Honeybee"
ghenv.Component.NickName = 'BuildingToHoneybee'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "1"


try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_vector2d
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # set default use of multipliers to True
    use_multiplier_ = use_multiplier_ if use_multiplier_ is not None else True
    
    # create the model objects
    if _obj_per_model_ is None or _obj_per_model_.title() == 'Building':
        models = Building.buildings_to_honeybee_self_shade(
            _buildings, shade_dist_, use_multiplier_, tolerance)
    elif _obj_per_model_.title() == 'District':
        models = Building.buildings_to_honeybee(
            _buildings, use_multiplier_, tolerance)
    else:
        raise ValueError('Unrecognized _obj_per_model_ input: '
                         '{}'.format(_obj_per_model_))
    
    # change the model north if there is one input
    if _north_ is not None:
        for model in models:
            try:
                model.north_vector = to_vector2d(_north_)
            except AttributeError:  # north angle instead of vector
                model.north_angle = _north_
    
    # add the context_ shade to all models
    if len(context_) != 0:
        for model in models:
            for shd in context_:
                model.add_shade(shd)

