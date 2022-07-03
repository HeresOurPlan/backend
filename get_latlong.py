import certifi
import ssl
import geopy.geocoders
from geopy.geocoders import Nominatim

def get_location(address):
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx

    #address we need to geocode
    loc = 'Singapore Yung Sheng Rd 610184'
    
    #making an instance of Nominatim class
    geolocator = Nominatim(user_agent="my_request", scheme='http')
 
    #applying geocode method to get the location
    location = geolocator.geocode(address)
    return (location.latitude, location.longitude)
 
#printing address and coordinates
# print(location.address)
# print((location.latitude, location.longitude))