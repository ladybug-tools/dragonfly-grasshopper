# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an Ground Heat Exchanger Loop for a District Energy Simulation (DES) simulation.
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
        _pipe_: A GHE Pipe object from the "DF GHE Pipe Parameters" component.
            This can be used to customize the pipe diameter, conductivty,
            and roughness.
        _horiz_pipe_: A HorizontalPipe object to specify the properties of the
            horizontal pipes contained within ThermalConnectors. This can be
            used to customize the pipe insulation, pressure loss, etc.
        _design_: A GHEDesign object from the "DF GHE Design" component. This can be
            used to customize the mina and max entering fluid temperatures
            as well as the max boreholes.
        _name_: Text to be used for the name and identifier of the Thermal Loop.
            If no name is provided, it will be "unnamed".
        _ghe_names_: An optional list of names that align with the input _ghe_geo and
            note the name to be used for each ground heat exchanger in the
            DES loop. If no names are provided, they will be derived from
            the DES Loop name above.
        _connect_names_: An optional list of names that align with the input _connector_geo
            and note the name to be used for each thermal connector in the
            DES loop. If no names are provided, they will be derived from
            the DES Loop name above.

    Returns:
        report: Reports, errors, warnings, etc.
        loop: A Dragonfly Thermal Loop object possessing all infrastructure for a
            District Energy Simulation (DES) simulation. This should be connected
            to the loop_ input of the "DF Model to GeoJSON" component.
"""

ghenv.Component.Name = 'DF GHE Thermal Loop'
ghenv.Component.NickName = 'GHELoop'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

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
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.config import angle_tolerance, conversion_to_meters
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set a default name
    name = clean_ep_string(_name_) if _name_ is not None else 'unnamed'

    # create the Thermal Connectors
    connectors = []
    for i, geo in enumerate(_connector_geo):
        lin = to_polyline2d(geo)
        try:
            conn_name = _connect_names_[i]
            conn_id = clean_ep_string(conn_name)
        except IndexError:
            conn_name, conn_id = None, '{}_ThermalConnector_{}'.format(name, i)
        conn_obj = ThermalConnector(conn_id, lin)
        if conn_name is not None:
            conn_obj.display_name = conn_name
        connectors.append(conn_obj)

    # create the GHE fields
    ghes, total_area = [], 0
    for i, geo in enumerate(_ghe_geo):
        faces = to_face3d(geo)
        gp = faces[0]
        total_area += gp.area * conversion_to_meters()
        try:
            ghe_name = _ghe_names_[i]
            ghe_id = clean_ep_string(ghe_name)
        except IndexError:
            ghe_name, ghe_id = None, '{}_GHE_{}'.format(name, i)
        ghe_obj = GroundHeatExchanger(ghe_id, gp)
        if ghe_name is not None:
            ghe_obj.display_name = ghe_name
        ghes.append(ghe_obj)

    # create the loop
    des_loop = GHEThermalLoop(
        name, ghes, connectors, _clockwise_,
        _soil_, _fluid_, _pipe_, _borehole_, _design_, _horiz_pipe_)
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
