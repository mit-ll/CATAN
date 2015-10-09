"""
    This a simple script for interacting with our GPS receiver.

    (c) 2015 Massachusetts Institute of Technology
"""
# Native
import serial
import logging
logger = logging.getLogger(__name__)
from datetime import datetime
from dateutil import tz



class GPSReceiver():
    """
        This class impelments all of our interaction with our GPS receiver
    """
    
    def __init__(self, serial_interface="/dev/ttyUSB0"):
        """
            Store our serial location for later
        """
        self.serial_interface = serial_interface
    
    
    def _nmea_to_decimal_(self, nmea_value, cardinal):
        """
            This will take our NMEA formatted string and convert it to decimal
            
            dddmm.mmmmm,[N/S or E/W]
            
            @param nmea_value: NMEA formatted string
            @param cardlinal: Cardinal characater, i.e. N/S or E/W 
        """
        # First split our text into degree and minutes
        deg_minute_split = nmea_value.split(".")
        deg = deg_minute_split[0][:-2]
        min = deg_minute_split[0][-2:]+"."+deg_minute_split[1]
        
        # Calculate decimal form
        decimal = float(deg) + float(min)/60
        
        # Return appropriate sign
        if cardinal == "S" or cardinal == "W":
            decimal *= -1
            
        return decimal   
    
    def get_time(self):
        rtn = None
        ser = None
        try:
            ser = serial.Serial(self.serial_interface, 4800, timeout=1)
            while True:
                line = ser.readline()
                params = line.split(",")
                
                message_type = params[0]
                
                if message_type == "$GPRMC":
                    utc_time = params[1]
                    utc_time = utc_time[:2]+":"+utc_time[2:4]+":"+utc_time[4:]
                    
                    # Warning?
                    nav_warning = params[2] # A = OK, V = warning
                    
                    # Extract latitude
                    latitude = params[3]
                    latitude_cardinal = params[4]
                    lat_decimal = self._nmea_to_decimal_(latitude,
                                                  latitude_cardinal)
                    # Extract longitude
                    longitude = params[5]
                    longitude_cardinal = params[6]
                    long_decimal = self._nmea_to_decimal_(longitude,
                                                  longitude_cardinal)
                    
                    # Speed in knots
                    speed = params[7]
                    # True course (degrees)
                    true_course = params[8]
                    
                    # Date (DD/MM/YY)
                    utc_date = params[9]
                    utc_date = utc_date[:2]+"/"+utc_date[2:4]+"/"+utc_date[4:]
                    
                    # Auto-detect zones:
                    from_zone = tz.tzutc()
                    to_zone = tz.tzlocal()
                    
                    time_str = utc_date+" "+utc_time
                    utc = datetime.strptime(time_str, '%d/%m/%y %H:%M:%S.%f')
                    
                    # Tell the datetime object that it's in UTC time zone since 
                    # datetime objects are 'naive' by default
                    utc = utc.replace(tzinfo=from_zone)
                    
                    # Convert time zone
                    local = utc.astimezone(to_zone)
                
                    # if we have a gps fix, return value
                    if nav_warning == "A":
                        # Set our return value and break                    
                        rtn = local
                        break
                    else:
                        logger.warn("GPS has not acquired lock.")
                        
                        rtn = None
                        break
            ser.close()
            
        except:
            logger.error("Could not communicate with GPS Reciver.")
            import traceback
            traceback.print_exc()
            if ser is not None:
                ser.close()
                
        return rtn

    def get_coordinates(self):
        """
            Read the GPG LINE using the NMEA standard
            
            Ref: http://www.gpsinformation.org/dale/nmea.htm
            
            @return (latitude, longitude, altitude)
        """
        rtn = None
        
        ser = None
        try:
            ser = serial.Serial(self.serial_interface, 4800, timeout=1)
            while True:
                line = ser.readline()
                params = line.split(",")
                
                message_type = params[0]
                
                if message_type == "$GPGGA":
                    utc_time = params[1]
                    utc_time = utc_time[:2]+":"+utc_time[2:4]+":"+utc_time[4:]
                    
                    # Extract latitude
                    latitude = params[2]
                    latitude_cardinal = params[3]
                    lat_decimal = self._nmea_to_decimal_(latitude,
                                                  latitude_cardinal)
                    # Extract longitude
                    longitude = params[4]
                    longitude_cardinal = params[5]
                    long_decimal = self._nmea_to_decimal_(longitude,
                                                  longitude_cardinal)
                    
                    
                    fix_quality = int(params[6])
                    satillite_count = int(params[7])
                    horizontal_dilution = params[8]
                    altitude = float(params[9])
                    altitude_measurement = params[10]
                    height_of_geoid = params[11]+params[12]
                    time_since_dgps_update = params[13]
                    dgps_station_id = params[14].split("*")[0]
                    checksum = params[14].split("*")[1]

                    # if we have a gps fix, return value
                    if fix_quality == 1:
                        # Set our return value and break                    
                        rtn = {"latitude":lat_decimal,
                               "longitude":long_decimal,
                               "altitude":altitude,
                               "satillite_count":satillite_count}
                        break
                    else:
                        logger.warn("GPS has not acquired lock.")
                        
                        rtn = None
                        break
                
                
                    
#                 if message_type == "$GPGSV":
#                     selection_type = params[1]
#                     fix_3d = params[2]
#                     pprns_of_satillites = [x for x in params[3:15]]
#                     dilution_of_precision = params[15]
#                     hdop = params[16]
#                     vdop = params[17]
#                     checksum = params[18]
                
                
            ser.close()
        except:
            logger.error("Could not communicate with GPS Reciver.")
            import traceback
            traceback.print_exc()
            if ser is not None:
                ser.close()
                           
        return rtn