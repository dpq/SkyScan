
import logging
import math
from sensecam_control import onvif_control,onvif_config
import argparse

def deg2rad(deg: float) -> float:
    """Convert degrees to radians

    Arguments:
        deg {float} -- Angle in degrees

    Returns:
        float -- Angle in radians
    """
    return deg * (math.pi/float(180))


def rad2deg(deg: float) -> float:
    """Convert degrees to radians

    Arguments:
        deg {float} -- Angle in degrees

    Returns:
        float -- Angle in radians
    """
    return deg / (math.pi/float(180))



def coordinate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between the two coordinates

    Arguments:
        lat1 {float} -- Start latitude
        lon1 {float} -- Start longitude
        lat2 {float} -- End latitude
        lon2 {float} -- End longitude

    Returns:
        float -- Distance in meters
    """
    R = 6371 # Radius of the earth in km
    dLat = deg2rad(lat2-lat1)
    dLon = deg2rad(lon2-lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c * 1000 #  Distance in m
    return d


def elevation(distance: float, cameraAltitude, airplaneAltitude):

    if distance > 0:
        ratio = ( float(airplaneAltitude) - float(cameraAltitude)) / float(distance)
        a = math.atan(ratio) * (float(180) /math.pi)
        
        
        return a
    else:
        logging.info("🚨 Elevation is less than zero 🚨  ")
        return 0

def cameraPanFromCoordinate(airplanePosition, cameraPosition) -> float:
    """Calculate bearing from lat1/lon2 to lat2/lon2

    Arguments:
        lat1 {float} -- Start latitude
        lon1 {float} -- Start longitude
        lat2 {float} -- End latitude
        lon2 {float} -- End longitude

    Returns:
        float -- bearing in degrees
    """

    lat2 = airplanePosition[0]
    lon2 = airplanePosition[1]
    
    lat1 = cameraPosition[0]
    lon1 = cameraPosition[1]
    
    rlat1 = math.radians(lat1)
    rlat2 = math.radians(lat2)
    rlon1 = math.radians(lon1)
    rlon2 = math.radians(lon2)
    dlon = math.radians(lon2-lon1)

    b = math.atan2(math.sin(dlon)*math.cos(rlat2),math.cos(rlat1)*math.sin(rlat2)-math.sin(rlat1)*math.cos(rlat2)*math.cos(dlon)) # bearing calc
    bd = math.degrees(b)
    br,bn = divmod(bd+360,360) # the bearing remainder and final bearing

    return bn

def main():

    parser = argparse.ArgumentParser(description='An MQTT based camera controller')
    parser.add_argument('--lat', type=float, help="Latitude of camera")
    parser.add_argument('--lon', type=float, help="Longitude of camera")
    parser.add_argument('--alt', type=float, help="altitude of camera in METERS!", default=0)
    parser.add_argument('--mark-lat', type=float, help="Latitude of landmark")
    parser.add_argument('--mark-lon', type=float, help="Longitude of landmark")
    parser.add_argument('--mark-alt', type=float, help="altitude of landmark in METERS!", default=0)
    parser.add_argument('-u', '--axis-username', help="Username for the Axis camera", required=True)
    parser.add_argument('-p', '--axis-password', help="Password for the Axis camera", required=True)
    parser.add_argument('-a', '--axis-ip', help="IP address for the Axis camera", required=True)
    args = parser.parse_args()
    print(args)
    camera = onvif_control.CameraControl(args.axis_ip, args.axis_username, args.axis_password)

    print(camera)
    camera_longitude = args.lon
    camera_latitude = args.lat
    camera_altitude = args.alt # Altitude is in METERS
    landmark_longitude = args.mark_lon
    landmark_latitude = args.mark_lat
    landmark_altitude = args.mark_alt # Altitude is in METERS
    print(landmark_longitude)
    distance2d = coordinate_distance(camera_latitude, camera_longitude, landmark_latitude, landmark_longitude)
    print(distance2d)
    cameraTilt  = elevation(distance2d, cameraAltitude=camera_altitude, airplaneAltitude=landmark_altitude)

    print(cameraTilt)
    cameraPan = cameraPanFromCoordinate(cameraPosition=[camera_latitude, camera_longitude], airplanePosition=[landmark_latitude, landmark_longitude])
    print("about to move")
    camera.absolute_move(cameraPan, cameraTilt, 9999, 99)
    print("All done!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(e, exc_info=True)

                    
