# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Dragonfly ContextShade.
-

    Args:
        _geo: Rhino Brep geometry.
        _name_: A name for the ContextShade. If the name is not provided a random
            name will be assigned.
        ep_constr_: Optional text for the ContextShade's energy construction to be looked
            up in the construction library. This can also be a custom construction
            object. If no energy construction is input here, a default will be
            assigned.
        ep_trans_sch_: Optional text for the ContextShade's energy transmittance
            schedule to be looked up in the schedule library. This can also be a
            custom schedule object. If no energy schedule is input here, the default
            will be always opaque.
    
    Returns:
        report: Reports, errors, warnings, etc.
        context: Dragonfly ContextShades.
"""

ghenv.Component.Name = 'DF ContextShade'
ghenv.Component.NickName = 'Context'
ghenv.Component.Message = '0.1.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '7'

import uuid

try:  # import the core dragonfly dependencies
    from dragonfly.context import ContextShade
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import shade_construction_by_name
    from honeybee_energy.lib.schedules import schedule_by_name
except ImportError as e:
    if ep_constr_ is not None:
        raise ValueError('ep_constr_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))
    elif ep_trans_sch_ is not None:
        raise ValueError('ep_trans_sch_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the dragonfly-energy extension
    import dragonfly_energy
except ImportError as e:
    if ep_constr_ is not None:
        raise ValueError('ep_constr_ has been specified but dragonfly-energy '
                         'has failed to import.\n{}'.format(e))
    elif ep_trans_sch_ is not None:
        raise ValueError('ep_trans_sch_ has been specified but dragonfly-energy '
                         'has failed to import.\n{}'.format(e))


if all_required_inputs(ghenv.Component):
    context = []  # list of context shades that will be returned
    
    # set default name
    name = _name_ if _name_ is not None else str(uuid.uuid4())
    
    # create the ContextShades
    for i, geo in enumerate(_geo):
        lb_faces = to_face3d(geo)
        df_shd = ContextShade('{}_{}'.format(name, i), lb_faces)
        
        # try to assign the energyplus construction
        if ep_constr_ is not None:
            if isinstance(ep_constr_, str):
                ep_constr_ = shade_construction_by_name(ep_constr_)
            df_shd.properties.energy.construction = ep_constr_
        
        # try to assign the energyplus transmittance schedule
        if ep_trans_sch_ is not None:
            if isinstance(ep_trans_sch_, str):
                ep_trans_sch_ = schedule_by_name(ep_trans_sch_)
            df_shd.properties.energy.transmittance_schedule = ep_trans_sch_
        
        context.append(df_shd)  # collect the final ContextShades