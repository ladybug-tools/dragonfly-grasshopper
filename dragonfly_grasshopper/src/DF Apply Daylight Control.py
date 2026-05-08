# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply simple daylight controls to Dragonfly Buildings, Stories or Room2Ds.
_
These controls will dim the lights in the energy simulation according to whether
the illuminance at a sensor location is at a target illuminance setpoint.
-

    Args:
        _df_objs: Dragonfly Buildings, Stories or Room2Ds to which daylight controls
            will be assigned. This can also be an etire dragonfly Model.
        _sensor_points_: An optional list of points that align with the input _df_objs and
            assign the position of the daylight sensor within each Room2D.
            Note that this input should only be used when the input _df_objs
            are Room2Ds since, otherwise, sensors are likely to fall outside
            the room volume and a warning will be issued by this component with
            no daylight controls assigned for any point that lies outside the
            corresponding room. If unspecified, the sensor will be assigned
            to the center of each Room2D that touches the building perimeter.
            Sensors will be at 0.8 meters above the floor.
        _ill_setpoint_: A number for the illuminance setpoint in lux beyond which
            electric lights are dimmed if there is sufficient daylight.
            Some common setpoints are listed below. (Default: 300 lux).
            -
            50 lux - Corridors and hallways.
            150 lux - Computer work spaces (screens provide illumination).
            300 lux - Paper work spaces (reading from surfaces that need illumination).
            500 lux - Retail spaces or museums illuminating merchandise/artifacts.
            1000 lux - Operating rooms and workshops where light is needed for safety.

        _control_fract_: A number between 0 and 1 that represents the fraction of
            the Room lights that are dimmed when the illuminance at the sensor
            position is at the specified illuminance. 1 indicates that all lights are
            dim-able while 0 indicates that no lights are dim-able. Deeper rooms
            should have lower control fractions to account for the face that the
            lights in the back of the space do not dim in response to suitable
            daylight at the front of the room. (Default: 1).
        _min_power_in_: A number between 0 and 1 for the the lowest power the lighting
            system can dim down to, expressed as a fraction of maximum
            input power. (Default: 0.3).
        _min_light_out_: A number between 0 and 1 the lowest lighting output the lighting
            system can dim down to, expressed as a fraction of maximum
            light output. (Default: 0.2).
        off_at_min_: Boolean to note whether lights should switch off completely when
            they get to the minimum power input. (Default: False).

    Returns:
        report: Reports, errors, warnings, etc.
        df_objs: The input Dragonfly objects with daylight controls assigned to them.
"""

ghenv.Component.Name = 'DF Apply Daylight Control'
ghenv.Component.NickName = 'DFDaylightControl'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '3 :: Energy'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the honeybee-energy extension
    from ladybug_geometry.geometry3d import Vector3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.load.daylight import DaylightingControl
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
    from dragonfly.building import Building
    from dragonfly.story import Story
    from dragonfly.room2d import Room2D
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_point3d
    from ladybug_rhino.config import conversion_to_meters, current_tolerance
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list, \
        give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
tol = current_tolerance()


def extract_room2ds(obj):
    """Get all of the Room2Ds assinged to a given dragonfly object."""
    if isinstance(obj, Building):
        return obj.unique_room_2ds
    elif isinstance(obj, Story):
        return obj.room_2ds
    elif isinstance(obj, Room2D):
        return [obj]
    elif isinstance(obj, Model):
        return [room for bldg in obj.buildings for room in bldg.unique_room_2ds]
    else:
        raise ValueError(
            'Expected Dragonfly Room2D, Story, Building, or Model. '
            'Got {}.'.format(type(hb_obj)))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    df_objs = [obj.duplicate() for obj in _df_objs]

    # set default values and perform checks
    dist_from_floor = 0.8 / conversion_to_meters()
    if len(_sensor_points_) != 0:
        assert len(_sensor_points_) == len(df_objs), 'Number of sensor points ({}) ' \
            'must align exactly with the number of _df_objs ({}).'.format(
                len(_sensor_points_), len(hb_objs))
    _ill_setpoint_ = [300] if len(_ill_setpoint_) == 0 else _ill_setpoint_
    _control_fract_ = [1] if len(_control_fract_) == 0 else _control_fract_
    _min_power_in_ = [0.3] if len(_min_power_in_) == 0 else _min_power_in_
    _min_light_out_ = [0.2] if len(_min_light_out_) == 0 else _min_light_out_
    off_at_min_ = [False] if len(off_at_min_) == 0 else off_at_min_

    # loop through the rooms and assign daylight sensors
    unassigned_rooms = []
    for i, df_obj in enumerate(df_objs):
        for room in extract_room2ds(df_obj):
            if len(_sensor_points_) == 0:
                if room.is_perimeter:
                    dl_control = room.properties.energy.add_daylight_control_to_center(
                        dist_from_floor, longest_list(_ill_setpoint_, i),
                        longest_list(_control_fract_, i), longest_list(_min_power_in_, i),
                        longest_list(_min_light_out_, i), longest_list(off_at_min_, i), tol)
                    if dl_control is None:
                        unassigned_rooms.append(room.display_name)
            else:
                sensor_pt = to_point3d(_sensor_points_[i])
                m_vec = Vector3D(0, 0, sensor_pt.z - room.floor_geometry[0].z)
                if m_vec.z < room.floor_to_ceiling_height and \
                        room.floor_geometry.move(m_vec).is_point_on_face(sensor_pt, tol):
                    dl_control = DaylightingControl(
                        sensor_pt, longest_list(_ill_setpoint_, i),
                        longest_list(_control_fract_, i), longest_list(_min_power_in_, i),
                        longest_list(_min_light_out_, i), longest_list(off_at_min_, i))
                    room.properties.energy.daylighting_control = dl_control
                else:
                    unassigned_rooms.append(room.display_name)

    # give a warning about any rooms to which a sensor could not be assinged
    for room in unassigned_rooms:
        msg = 'Sensor point for room "{}" does not lie within the room volume.\n' \
            'No daylight sensors have been added to this room.'.format(room)
        print(msg)
        give_warning(ghenv.Component, msg)
