# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run a GHE Designer simulation to size a ground heat exchanger (GHE) and produce a
G-function that can be used in EnergyPlus/IronBug simulations.
_
The GHE sizing requires a data collection of hourly ground loads, a planar site
geometry indicating where boreholes can be placed, and geometric constraints
about the spacing and depth of the boreholes.
_
This component uses the GHEDesigner Python package to perform the GHE sizing
calculation. GHEDesigner is similar in principle to tools like GLHEPRO but is
currently limited to vertical borehole exchangers (it cannot model horizontal
exchangers). Also, it requires the input of ground heat extraction/rejection loads.
So it currently requires you to account for the COP of heat pumps as a manual
pre-step before using building heating/cooling loads as an input.
_
More information on GHEDesigner can be found in the documentation here:
https://ghedesigner.readthedocs.io/en/latest/background.html
-

    Args:
        _load: An annual data collection of hourly loads on the ground in Watts.
            These are the heat extraction and heat rejection loads of the
            ground heat exchanger and should already account for factors
            like additional heat added or removed by the heat pump compressors.
            Positive values indicate heat extraction, negative values indicate
            heat rejection.
        _site: A list of horizontal Rhino surfaces representing a footprint of the site
            to be populated with boreholes. These surfaces can have holes in them
            and these holes will be excluded from borehole placement.
        _borehole_: A GHE BoreholeParameter object from the "DF GHE Borehole Parameters"
            component, which customizes properties like borehole min/max depth
            and borehole min/max spacing.
        _soil_: A GHE SoilParameter object from the "DF GHE Soil Parameters" component.
            This can be used to customize the conductivity and density of the
            soil as well as the grout that fills the borehole.
        _fluid_: A GHE Fluid object from the "DF GHE Fluid Parameters" component.
            This can be used to customize the fuild used (eg. water, glycol)
            as well as the concentration of the fluid. (Default: 100% Water).
        _pipe_: A GHEPipe object from the "DF GHE Pipe Parameters" component.
            This can be used to customize the pipe diameter, conductivty,
            and roughness.
        _design_: A GHEDesign object from the "DF GHE Design" component. This can be
            used to customize the mina and max entering fluid temperatures
            as well as the max boreholes.
        _write: Set to "True" to run the component, install any missing dependencies,
            and write the input JSON for GHEDesigner.
        run_: Set to "True" to run GHEDesigner once the JSON is written. This will
            ensure that all result files appear in their respective outputs
            from this component.

    Returns:
        report: Reports, errors, warnings, etc.
        input_json: Path to the JSON file that was used to specify inputs for the GHEDesigner.
        boreholes: A list of points for the borehole locations within the _site.
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

ghenv.Component.Name = 'DF GHE Designer'
ghenv.Component.NickName = 'GHEDesigner'
ghenv.Component.Message = '1.9.1'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '5 :: District Thermal'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os
import subprocess
import json

try:
    from ladybug_geometry.geometry2d import Point2D
    from ladybug_geometry.geometry3d import Vector3D, Point3D, LineSegment3D
    from ladybug_geometry.bounding import bounding_box
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug.config import folders as lb_folders
    from ladybug.futil import nukedir
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from dragonfly_energy.des.ghe import GroundHeatExchanger
    from dragonfly_energy.des.loop import GHEThermalLoop
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters, tolerance
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.fromgeometry import from_point2d, from_linesegment3d
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning, \
        list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

GHE_DESIGNER_VERSION = '2.0'


if all_required_inputs(ghenv.Component) and _write:
    # set up the custom python environment
    custom_env = os.environ.copy()
    custom_env['PYTHONHOME'] = ''
    shell = True if os.name == 'nt' else False

    # set global values
    ext = '.exe' if os.name == 'nt' else ''
    executor_path = os.path.join(
        lb_folders.ladybug_tools_folder, 'grasshopper',
        'ladybug_grasshopper_dotnet', 'Ladybug.Executor.exe')

    # check to see if GHEDesigner is installed
    ghe_des = '{}/ghedesigner{}'.format(folders.python_scripts_path, ext)
    ghe_des_pack = '{}/GHEDesigner-{}.dist-info'.format(
        folders.python_package_path, GHE_DESIGNER_VERSION)
    if not os.path.isfile(ghe_des) or not os.path.isdir(ghe_des_pack):
        install_cmd = 'pip install ghedesigner=={}'.format(GHE_DESIGNER_VERSION)
        if os.name == 'nt' and os.path.isfile(executor_path) and \
                'Program Files' in executor_path:
            pip_cmd = [
                executor_path, folders.python_exe_path, '-m {}'.format(install_cmd)
            ]
        else:
            pip_cmd = '"{py_exe}" -m {uo_cmd}'.format(
                py_exe=folders.python_exe_path, uo_cmd=install_cmd)
        process = subprocess.Popen(
            pip_cmd, stderr=subprocess.PIPE, shell=shell, env=custom_env)
        stderr = process.communicate()

    # process the site geometry into Face3D
    site_faces = []
    for brep in _site:
        site_faces.extend(to_face3d(brep))
    conv_factor = conversion_to_meters()
    for i, face in enumerate(site_faces):
        site_faces[i] = face.scale(conv_factor)
    # GHEDesigner treats negative values as invalid
    # ensure coordinate values are positive
    min_pt, max_pt = bounding_box(site_faces)
    move_vec_2d = Point2D(0, 0) - Point2D(min_pt.x, min_pt.y)
    move_vec_3d = Point3D(move_vec_2d.x, move_vec_2d.y, 0)
    for i, face in enumerate(site_faces):
        site_faces[i] = face.move(move_vec_3d)

    # create the input dict for GHEDesigner
    ghe_dict = GHEThermalLoop.ghe_designer_dict(
        _load, site_faces, _soil_, _fluid_, _pipe_, _borehole_, _design_, tolerance)

    # write the dict to a JSON in the simulation folder
    sim_folder = os.path.join(folders.default_simulation_folder, 'GHEDesigner')
    nukedir(sim_folder)
    if not os.path.isdir(sim_folder):
        os.makedirs(sim_folder)
    input_json = os.path.join(sim_folder, 'ghe_input.json')
    with open(input_json, 'w') as inf:
        json.dump(ghe_dict, inf, indent=4)

    # execute GHEDesigner
    if run_:
        # execute the command to run everything through GHEDesigner
        command = '"{ghe_des}" "{input_json}" "{sim_folder}"'.format(
            ghe_des=ghe_des, input_json=input_json, sim_folder=sim_folder)
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=shell, env=custom_env)
        result = process.communicate()
        # parse the result files
        bore_file = input_json = os.path.join(sim_folder, 'BoreFieldData.csv')
        g_func_file = input_json = os.path.join(sim_folder, 'Gfunction.csv')
        summary_file = input_json = os.path.join(sim_folder, 'SimulationSummary.json')
        # if the simulation failed, give a warning
        if not os.path.isfile(bore_file):
            give_warning(ghenv.Component, result[0])
            print(result[0])
            print(result[1])
        else:  # parse the result files
            # load the borehole positions
            with open(bore_file, 'r') as bf:
                borehole_data = bf.readlines()
            move_vec_rev = move_vec_2d.reverse()
            borehole_pts = []
            for pt in borehole_data[1:]:
                bore_pt = Point2D(*(float(c) for c in pt.split(',')))
                borehole_pts.append(bore_pt.move(move_vec_rev))
            boreholes = [from_point2d(pt) for pt in borehole_pts]

            # load the summary data
            properties = GroundHeatExchanger.load_energyplus_properties(summary_file)
            zp = zip(GroundHeatExchanger.PROPERTY_NAMES, properties)
            print('\n'.join('{}: {}'.format(name, val) for name, val in zp))

            # create a line segment for each borehole
            bore_dir = Vector3D(0, 0, -properties[0])
            ghe_geos = [LineSegment3D(Point3D(pt.x, pt.y, min_pt.z), bore_dir)
                        for pt in borehole_pts]
            bore_geo = [from_linesegment3d(pt) for pt in ghe_geos]

            # load the g-function and the monthly temperatures
            g_function = GroundHeatExchanger.load_g_function(g_func_file)
            g_function = list_to_data_tree(g_function)
            month_temps = GroundHeatExchanger.load_monthly_temperatures(summary_file)
