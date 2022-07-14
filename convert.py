# importing modules
import geopy.geocoders
from geopy.geocoders import Nominatim

def converting(coords):

    # calling the nominatim tool
    geoLoc = Nominatim(user_agent="GetLoc")

    # passing the coordinates
    # locname = geoLoc.reverse("26.7674446, 81.109758")
    location = geoLoc.reverse(coords)

    return location

    # printing the address/location name
    # print(locname.address)