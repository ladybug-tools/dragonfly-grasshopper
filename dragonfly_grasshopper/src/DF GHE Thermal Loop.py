# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an Ground Heat Exchanger Thermal Loop, which represents all infrastructure
for a District Energy Simulation (DES) simulation.
_
This includes a ground heat exchanger and all thermal connectors needed
to connect these objects to Dragonfly Buildings.
-

    Args:
        _ghe_geo: Horizontal Rhino surfaces representing the footprints of ground heat
            exchangers. These ground heat exchanging fields contain the
            boreholes that supply the loop with thermal capacity. Multiple
            borehole fields can be located along the loop created by the
            _connector_geo.
        _connector_geo: An array of lines or polylines representing the thermal connectors
            within the thermal loop. In order for a given connector to be valid
            within the loop, each end of the connector must touch either another
            connector, a building footprint, or a ground heat exchanger. In
            order for the loop as a whole to be valid, the connectors must form a
            single continuous loop when passed through the buildings and the heat
            exchanger field.
        _clockwise_: A boolean to note whether the direction of flow through the
            loop is clockwise (True) when viewed from above in the GeoJSON or it
            is counterclockwise (False). (Default: False).
        _borehole_: A GHE BoreholeParameter object from the "DF GHE Borehole Parameters"
            component, which customizes properties like borehole min/max depth
            and borehole min/max spacing.
        _soil_: A GHE SoilParameter object from the "DF GHE Soil Parameters" component.
            This can be used to customize the conductivity and density of the
            soil as well as the grout that fills the boreholes.
        _fluid_: A GHE Fluid object from the "DF GHE Fluid Parameters" component.
            This can be used to customize the fuild used (eg. water, glycol)
            as well as the concentration of the fluid. (Default: 100% Water).
        _pipe_: A GHEPipe object from the "DF GHE Pipe Parameters" component.
            This can be used to customize the pipe diameter, conductivty,
            and roughness.
        _design_: A GHEDesign object from the "DF GHE Design" component. This can be
            used to customize the mina and max entering fluid temperatures
            as well as the max boreholes.
        _name_: Text to be used for the name and identifier of the Thermal Loop.
            If no name is provided, it will be "unnamed".

    Returns:
        report: Reports, errors, warnings, etc.
        loop: A Dragonfly Thermal Loop object possessing all infrastructure for a
            District Energy Simulation (DES) simulation. This should be connected
            to the loop_ input of the "DF Model to GeoJSON" component.
"""

ghenv.Component.Name = 'DF GHE Thermal Loop'
ghenv.Component.NickName = 'GHELoop'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import math

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.des.connector import ThermalConnector
    from dragonfly_energy.des.ghe import GroundHeatExchanger
    from dragonfly_energy.des.loop import GHEThermalLoop
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_polyline2d
    from ladybug_rhino.togeometry import to_polygon2d
    from ladybug_rhino.config import angle_tolerance, conversion_to_meters
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set a default name
    name = clean_ep_string(_name_) if _name_ is not None else 'unnamed'

    # create the GHE fields and the Thermal Connectors
    lines = []
    for geo in _connector_geo:
        lines.append(to_polyline2d(geo))
    connectors = []
    for i, lin in enumerate(lines):
        connectors.append(ThermalConnector('{}_ThermalConnector_{}'.format(name, i), lin))
    ghes, total_area = [], 0
    for i, geo in enumerate(_ghe_geo):
        gp = to_polygon2d(geo)
        total_area += gp.area * conversion_to_meters()
        if not gp.is_rectangle(math.radians(angle_tolerance)):
            msg = 'The ground heat exchanger with index {} is not a perfect rectangle ' \
                'but it will be approximated as such in the DES simulation.'.format(i)
            print(msg)
            give_warning(ghenv.Component, msg)
        ghes.append(GroundHeatExchanger('{}_GHE_{}'.format(name, i), gp))

    # create the loop
    des_loop = GHEThermalLoop(name, ghes, connectors, _clockwise_,
                              _soil_, _fluid_, _pipe_, _borehole_, _design_)
    if _name_ is not None:
        des_loop.display_name = _name_

    # give a warning about RAM if the size of the borehole field is too large
    borehole_count = int(total_area / (des_loop.borehole_parameters.min_spacing ** 2))
    MAX_BOREHOLES = 8000
    if borehole_count > MAX_BOREHOLES:
        msg = 'The inputs suggest that there may be as many as {} boreholes in the ' \
            'GHE field\nand this can cause the GHE sizing routine to use ' \
            'more than 10GB of memory.\nA smaller _ghe_geo or a larger '\
            '_bore_spacing_ is recommended such that fewer\nthan {} boreholes are ' \
            'generated.'.format(borehole_count, MAX_BOREHOLES)
        print(msg)
        give_warning(ghenv.Component, msg)
