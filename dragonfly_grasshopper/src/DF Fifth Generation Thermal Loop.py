# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an Fifth Generation Loop for a District Energy Simulation (DES) simulation.
_
This includes all thermal connectors needed to connect Dragonfly Buildings in a loop.
-

    Args:
        _connector_geo: An array of lines or polylines representing the thermal connectors
            within the thermal loop. In order for a given connector to be
            valid within the loop, each end of the connector must touch either
            another connector or a building footprint. In order for the loop
            as a whole to be valid, the connectors must form a single continuous
            loop when passed through the building footprints.
        _clockwise_: A boolean to note whether the direction of flow through the
            loop is clockwise (True) when viewed from above or it is
            counterclockwise (False). (Default: False).
        _soil_: A GHE SoilParameter object from the "DF GHE Soil Parameters" component.
            This can be used to customize the conductivity and density of the
            soil surrounding the horizontal pipes of the DES loop.
        _horiz_pipe_: A HorizontalPipe object to specify the properties of the
            horizontal pipes contained within ThermalConnectors. This can be
            used to customize the pipe insulation, pressure loss, etc.
        _heat_rejection_: Text for the equipment used to cool the ambient loop when
            it overheats. Note that choosing None will usually cause a simulation
            failure unless a sufficiently large building with constant heatiing
            demand exists on the loop.
            Choose from the options below. (Default: CoolingTower).
            * CoolingTower
            * FluidCooler
            * EvaporativeFluidCooler
            * DistrictCooling
            * None
        _supplement_heat_: Text for the equipment used to heat the ambient loop
            when it requires supplemental heating. Note that choosing None will
            usually cause a simulation failure unless a sufficiently large
            building with constant cooling needs exists on the loop.
            Choose from the options below. (Default: Electricity).
            * Electricity
            * NaturalGas
            * DistrictHeating
            * None
        _name_: Text to be used for the name and identifier of the Thermal Loop.
            If no name is provided, it will be "unnamed".

    Returns:
        report: Reports, errors, warnings, etc.
        loop: A Dragonfly Thermal Loop object possessing all properties for a
            District Energy Simulation (DES) simulation. This should be connected
            to the loop_ input of the "DF Model to GeoJSON" component.
"""

ghenv.Component.Name = 'DF Fifth Generation Thermal Loop'
ghenv.Component.NickName = 'Gen5Loop'
ghenv.Component.Message = '1.10.2'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core dragonfly_energy dependencies
    from dragonfly_energy.des.connector import ThermalConnector
    from dragonfly_energy.des.loop import FifthGenThermalLoop
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_polyline2d
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
        conn_id = '{}_ThermalConnector_{}'.format(name, i)
        conn_obj = ThermalConnector(conn_id, lin)
        connectors.append(conn_obj)

    # create the loop
    heat_rejection = _heat_rejection_ \
        if _heat_rejection_ is not None else 'CoolingTower'
    supplement_heat = _supplement_heat_ \
        if _supplement_heat_ is not None else 'Electricity'
    des_loop = FifthGenThermalLoop(
        name, connectors, _clockwise_, _soil_, _horiz_pipe_,
        heat_rejection, supplement_heat
    )
    if _name_ is not None:
        des_loop.display_name = _name_
