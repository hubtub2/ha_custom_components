# this is a sample file
# to use more sensors you have to do the following steps
# 1. copy this file or create a new one name "sensors_custom.py"
# 2. fill in your sensors data into the json structure
# 3. (transfer the new file to your home assistant server into the "eta/" folder

"""
@name is optional, if not defined the original localized name of the variable will be used
@uri is required
@unit is optional
@device_class is optional
@state_class is optional
@factor is optional
"""
from homeassistant.const import TIME_SECONDS

SENSORS_CUSTOM = [
  {
    "uri": "/40/10021/0/0/12018",  # Zähler Zündungen
  },
  {
    "uri": "/40/10021/0/0/13642",  # Zähler Sicherheitspumpenlauf
  },
  {
    "uri": "/40/10021/0/0/13643",  # Laufzeit Sicherheitspumpenlauf
    "unit": TIME_SECONDS
  },
]
