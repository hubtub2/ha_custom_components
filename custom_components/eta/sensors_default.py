"""
@name is mandatory, if not defined the original localized name of the variable will be used
@uri is required
@unit is mandatory
@factor is mandatory
"""
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.const import TEMP_CELSIUS, POWER_KILO_WATT, MASS_KILOGRAMS, ENERGY_KILO_WATT_HOUR

SENSORS_DEFAULT = [
    {
        "uri": "/120/10601/0/0/12197",
        "unit": TEMP_CELSIUS
    },
    {
        "uri": "/40/10021/0/0/12077",
        "unit": POWER_KILO_WATT
    },
    {
        "uri": "/40/10021/0/0/12006",
        "unit": TEMP_CELSIUS
    },
    {
        "uri": "/40/10021/0/11109/0",
        "unit": TEMP_CELSIUS
    },
    {
        "uri": "/40/10021/0/11110/0",
        "unit": TEMP_CELSIUS
    },
    {
        "uri": "/120/10101/0/11125/2121",
        "unit": TEMP_CELSIUS
    },
    {
        "uri": "/40/10201/0/0/12015",
        "unit": MASS_KILOGRAMS
    },
    {
        "uri": "/40/10021/0/0/12016",
        "unit": MASS_KILOGRAMS
    },
    {
        "name": "Gesamt Energieverbrauch",
        "uri": "/40/10021/0/0/12016",
        "unit": ENERGY_KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "factor": 4.8
    },
]
