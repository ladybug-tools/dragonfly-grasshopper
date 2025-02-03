# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Load properties of the Ground Heat Exchangers (GHEs) from the "DF Write Modelica DES"
component. This includes the positions of boreholes in each GHE, the G-function
of each GHE that describes the response of the ground to load, an a range of other
properties output from the sizing simulation performed by GHEDesigner.
-

    Args:
        _sys_param: The system parameters JSON file output by the "DF Write Modelica DES"
            component. This includes the detailed Building load profiles,
            equipment specifications, and borehole field characteristics.
        _des_loop: The GHE Thermal Loop object output by the "DF GHE Thermal Loop",
            which contains the geometry of the district energy system.
        ip_: Boolean to note whether all outputs should be in SI or IP units.
            Setting this to True will result in all values in the report to IP
            and the month_temps will be in F instead of C. (Default: False).

    Returns:
        report: Reports, errors, warnings, etc.
        boreholes: A list of points for the borehole locations within the _site.
        borehole_geo: A list of line segments for each borehole in the ground
            heat exchanger, illustrating both the position and the demth of
            the borehole.
        g_function: A data tree of G-function coefficients that describe the response
            of the ground to the input loads. Each pair of factors represents
            a point on the G-function. Flattening this data tree enables you
            to plug it directly into the "Ironbug Ground Heat Exchanger Vertical"
            component to simulate the ground heat exchanger in EnergyPlus.
        properties: A list of properties for the GHE that can be used to describe it
            in EnergyPlus simulations. The properties that can be plugged directly
            into the parameters of the "Ironbug Ground Heat Exchanger Vertical"
            component. The properties are in the following order:
            _
            * Borehole Length
            * Borehole Radius
            * Design Flow Rate
            * Ground Temperature
            * Ground Conductivity
            * Ground Heat Capacity
            * Grout Conductivity
            * Number of Boreholes
            * Pipe Outer Diameter
            * Pipe Conductivity
            * Pipe Thickness
            * U Tube Distance
        month_temps: A list of ground temperatures in Celsius with one value for each month
            of the period over which the GHEDesigner simulation was run (typically
            20 years). This can be connected to a nativ Grasshopper "Quick Graph"
            component and used to check the drift in the ground temperature
            over long periods of time.
"""

ghenv.Component.Name = 'DF Read GHE Sizing'
ghenv.Component.NickName = 'GHESizing'
ghenv.Component.Message = '1.8.3'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

import os
import re

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry3d import Vector3D, Point3D, LineSegment3D, Face3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    import ladybug.datatype
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import units_system
    from ladybug_rhino.fromgeometry import from_point2d, from_linesegment3d
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

_unit_pattern = re.compile(r'\((.*)\)')


def property_to_ip(name, val):
    """Convert a GHE Property to IP."""
    matches = _unit_pattern.findall(name)
    if len(matches) == 0:
        return name, val
    unit = matches[0]
    base_type = None
    for key in ladybug.datatype.UNITS:
        if unit in ladybug.datatype.UNITS[key]:
            base_type = ladybug.datatype.TYPESDICT[key]()
            break
    if base_type is None:
        return name, val
    values, new_unit = base_type.to_ip([val], unit)
    return name.split('(')[0] + '({})'.format(new_unit), values[0]


if all_required_inputs(ghenv.Component):
    # get the folder where all of the sizing results live
    proj_folder = os.path.dirname(_sys_param)
    ghe_dir = os.path.join(proj_folder, 'run', 'honeybee_scenario', 'ghe_dir')
    assert os.path.isdir(ghe_dir), \
        'No GHE sizing results were found at" {}.'.format(ghe_dir)

    # parse the borehole geometry
    units = units_system()
    boreholes, bore_geo, g_function, properties, month_temps = [], [], [], [], []
    for ghe_id in os.listdir(ghe_dir):
        # find the matching GHE in the loop
        for ghe in _des_loop.ground_heat_exchangers:
            if ghe_id == ghe.identifier:
                matched_ghe = ghe
                break
        else:
            msg = 'No GHE in the connected _des_loop matches with the GHE ' \
                '"{}" in the _sys_param.'.format(ghe_id)
            raise ValueError(msg)
        
        # get the files with all of the information
        bore_file = os.path.join(ghe_dir, ghe_id, 'BoreFieldData.csv')
        summary_file = os.path.join(ghe_dir, ghe_id, 'SimulationSummary.json')
        g_func_file = os.path.join(ghe_dir, ghe_id, 'Gfunction.csv')

        # load the borehole positions
        ghe_bores = matched_ghe.load_boreholes(bore_file, units, ortho_rotation=True)
        ghe_boreholes = [from_point2d(pt) for pt in ghe_bores]
        boreholes.append(ghe_boreholes)

        # load the summary data
        props = matched_ghe.load_energyplus_properties(summary_file)
        properties.append(props)
        zp = zip(matched_ghe.PROPERTY_NAMES, props)
        if ip_:
            zp = [property_to_ip(name, val) for name, val in zp]
        print(ghe_id + '\n' + '\n'.join('  {}: {}'.format(name, val) for name, val in zp))

        # create a line segment for each borehole
        z_val = matched_ghe.geometry.min.z if isinstance(matched_ghe.geometry, Face3D) else 0
        bore_dir = Vector3D(0, 0, -props[0])
        ghe_geos = [LineSegment3D(Point3D(pt.x, pt.y, z_val), bore_dir) for pt in ghe_bores]
        ghe_geos = [from_linesegment3d(pt) for pt in ghe_geos]
        bore_geo.append(ghe_geos)

        # load the g-function and the monthly temperatures
        g_function.append(matched_ghe.load_g_function(g_func_file))
        t_ground = matched_ghe.load_monthly_temperatures(summary_file)
        if ip_:
            t_ground, _ = ladybug.datatype.temperature.Temperature().to_ip(t_ground, 'C')
        month_temps.append(t_ground)

    # convert the boreholes to a data tree
    boreholes = list_to_data_tree(boreholes)
    bore_geo = list_to_data_tree(bore_geo)
    g_function = list_to_data_tree(g_function)
    properties = list_to_data_tree(properties)
    month_temps = list_to_data_tree(month_temps)
