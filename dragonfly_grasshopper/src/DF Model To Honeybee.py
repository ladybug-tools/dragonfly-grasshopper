# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Convert a Dragonfly Model into a series of Honeybee Models.
-

    Args:
        _model: A Dragonfly Model object.
        _obj_per_model_: Text to describe how the input Buildings should be divided
            across the output Models. Default: 'Building'. Choose from the
            following options:
                * District - All buildings will be added to a single Honeybee Model.
                    Such a Model can take a long time to simulate so this is only
                    recommended for small numbers of buildings.
                * Building - Each building will be exported into its own Model.
                    For each Model, the other buildings input to this component will
                    appear as context shade geometry.
                * Story - Each Story of each Building will be exported into its
                    own Model. For each Honeybee Model, the other input Buildings
                    will appear as context shade geometry as will all of the other
                    stories of the same building.
        use_multiplier_: If True, the multipliers on each Building's Stories will be
            passed along to the generated Honeybee Room objects, indicating the
            simulation will be run once for each unique room and then results
            will be multiplied. If False, full geometry objects will be written
            for each and every story in the building such that all resulting
            multipliers will be 1. (Default: True).
        no_plenum_: Boolean to indicate whether ceiling/floor plenum depths
            assigned to Room2Ds should be ignored during translation. This
            results in each Room2D translating to a single Honeybee Room at
            the full floor-to-ceiling height instead of a base Room with (a)
            plenum Room(s). (Default: False).
        ceil_adjacency_: Boolean to note whether adjacencies should be solved between
            interior stories when Room2Ds perfectly match one another in
            their floor plate. This ensures that Surface boundary conditions
            are used instead of Adiabatic ones. Note that this input
            has no effect when the _obj_per_model_ is Story. (Default: False).
        merge_method_: An optional text string to describe how the Room2Ds should
            be merged into individual Rooms during the translation. Specifying a
            value here can be an effective way to reduce the number of Room
            volumes in the resulting 3D Honeybee Model and, ultimately, yield
            a faster simulation time in the destination engine with fewer results
            to manage. Note that Room2Ds will only be merged if they form a
            continuous volume. Otherwise, there will be multiple Rooms per
            zone or story, each with an integer added at the end of their
            identifiers and names. Choose from the following options:
                * None - No merging of Room2Ds will occur
                * Zones - Room2Ds in the same zone will be merged
                * PlenumZones - Only plenums in the same zone will be merged
                * Stories - Rooms in the same story will be merged
                * PlenumStories - Only plenums in the same story will be merged
        shade_dist_: An optional number to note the distance beyond which other
            buildings' shade should not be exported into a given Model. This is
            helpful for reducing the simulation run time of each Model when other
            connected buildings are too far away to have a meaningful impact on
            the results. If None, all other buildings will be included as context
            shade in each and every Model. Set to 0 to exclude all neighboring
            buildings from the resulting models. Default: None.
        _run: Set to "True" to have the Dragonfly Model translated to a series
            of Honeybee Models.

    Returns:
        report: Reports, errors, warnings, etc.
        hb_models: Honeybee Model objects derived from the input _models. These
            Models are ready to be simulated in either an Energy or Radiance
            simulation or they can be edited further with the Honeybee
            components.
"""

ghenv.Component.Name = 'DF Model To Honeybee'
ghenv.Component.NickName = 'ToHoneybee'
ghenv.Component.Message = '1.9.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '2 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '3'


try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_vector2d
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # set default inputs if not specified
    use_multiplier_ = use_multiplier_ if use_multiplier_ is not None else True
    no_plenum_ = no_plenum_ if no_plenum_ is not None else False
    _obj_per_model_ = 'Building' if _obj_per_model_ is None else _obj_per_model_
    ceil_adjacency_ = ceil_adjacency_ if ceil_adjacency_ is not None else False

    # check the _model input
    assert isinstance(_model, Model), \
        'Expected Dragonfly Model object. Got {}.'.format(type(_model))

    # create the model objects
    hb_models = _model.to_honeybee(
        object_per_model=_obj_per_model_,
        shade_distance=shade_dist_,
        use_multiplier=use_multiplier_,
        exclude_plenums=no_plenum_,
        cap=True,
        solve_ceiling_adjacencies=ceil_adjacency_,
        merge_method=merge_method_,
        tolerance=tolerance
    )
