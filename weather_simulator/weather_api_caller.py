from pyowm import OWM
import json
import pprint
owm = OWM('170e046a76606b649ec4bb6bb99daae4')
mgr = owm.weather_manager()
one_call = mgr.one_call(lat=28.5355, lon=77.3910)
current_data = json.dumps(one_call.current.__dict__)
pprint(current_data)

# print(one_call.current.humidity, one_call.current.temperature('celsius')['temp']) # Eg.: 81
