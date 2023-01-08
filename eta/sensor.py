"""
Platform for ETA sensor integration in Home Assistant

Help Links:
 Entity Source: https://github.com/home-assistant/core/blob/dev/homeassistant/helpers/entity.py
 SensorEntity derives from Entity https://github.com/home-assistant/core/blob/dev/homeassistant/components/sensor/__init__.py


author hubtub2

"""

from __future__ import annotations
import requests
import xmltodict
from lxml import etree
import logging
import voluptuous as vol
import xml.etree.ElementTree as ET

_LOGGER = logging.getLogger(__name__)
VAR_PATH = "/user/var"
MENU_PATH = "/user/menu"

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
    PLATFORM_SCHEMA,
    ENTITY_ID_FORMAT
)

from homeassistant.const import FREQUENCY_HERTZ, PRESSURE_BAR, ELECTRIC_POTENTIAL_VOLT, TIME_SECONDS, POWER_WATT, \
    VOLUME_LITERS, ELECTRIC_POTENTIAL_MILLIVOLT, IRRADIATION_WATTS_PER_SQUARE_METER, ELECTRIC_CURRENT_MILLIAMPERE, \
    PRESSURE_PA, PERCENTAGE, AREA_SQUARE_METERS

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.entity import generate_entity_id

# See https://github.com/home-assistant/core/blob/dev/homeassistant/const.py
from homeassistant.const import (CONF_HOST, CONF_PORT, TEMP_CELSIUS, ENERGY_KILO_WATT_HOUR, POWER_KILO_WATT,
                                 MASS_KILOGRAMS)

# See https://community.home-assistant.io/t/problem-with-scan-interval/139031
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PORT): cv.positive_int,
    # vol.Optional(DEFAULT_NAME): cv.string,
    # vol.Optional(CONF_TYPE): cv.string,
    # vol.Optional(CONF_SCAN_INTERVAL): cv.time_period,
})


def get_base_url(
        config: ConfigType,
        context: str = ""
) -> str:
    return "".join(["http://", config.get(CONF_HOST), ":", str(config.get(CONF_PORT)), context])


VAR_PATH = "/user/var"
MENU_PATH = "/user/menu"


def bool_mapper(input):
    return {
        "ein": True,
        "aus": False,
        "eingeschaltet": True,
        "ausgeschaltet": False,
        "ja": True,
        "nein": False,

    }.get(input)


def get_measure(config, uri):
    val = requests.get(get_base_url(config, VAR_PATH) + uri).content.decode("utf8")
    root = ET.fromstring(val)[0]

    # div = pow(0.1, (int(root.attrib.get("decPlaces", "0"))))
    scale = (int(root.attrib.get("scaleFactor", "1")))

    if root.attrib.get('unit', '') != "":
        return float(str(root.text)) / scale, root.attrib.get('unit', '')
    else:
        # check_bool_mapper
        bool_value = bool_mapper(root.attrib.get('strValue', '').lower())
        if bool_value is not None:
            return bool_value, 'bool'


class Setup:

    def __init__(self, config, hass):
        self.config = config
        self.hass = hass
        self.entities = {}

        res = requests.get(get_base_url(self.config, MENU_PATH)).content.decode("utf8")
        self._find_useful_entities(ET.fromstring(res))

    def get_entries(self) -> list:
        return list(self.entities.values())

    @staticmethod
    def _remove_duplicates_from_name(name):
        words = name.split(" ")
        return " ".join(sorted(set(words), key=words.index))

    def _find_useful_entities(self, root, prev=""):
        for child in root:
            self._find_useful_entities(child, prev=prev + " " + child.attrib.get("name", ""))

            new_name = prev + " " + child.attrib.get("name", "")
            if new_name in self.entities:
                continue

            measure = get_measure(self.config, child.attrib['uri'])
            if measure:
                new_name = self._remove_duplicates_from_name(new_name)
                value, unit = measure
                uri = child.attrib['uri']

                self.entities[new_name] = EtaSensor(self.config, self.hass, new_name, uri, unit)


def get_entity_name(
        config: ConfigType,
        uri: str
) -> str:
    ns = {'xsi': 'http://www.eta.co.at/rest/v1'}
    # TODO: exception handling
    data = requests.get(get_base_url(config, MENU_PATH), stream=True)
    data.raw.decode_content = True
    doc = etree.parse(data.raw)
    for o in doc.iterfind('//xsi:object', namespaces=ns):
        if o.attrib.get('uri') == uri:
            return o.attrib.get('name')
    return "unknown"


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""

    _LOGGER.info("ETA Integration - setup platform")

    add_entities(Setup(config, hass).get_entries())


class EtaSensor(SensorEntity):
    """Representation of a Sensor."""

    # _attr_device_class = SensorDeviceClass.TEMPERATURE
    # _attr_state_class = SensorStateClass.MEASUREMENT

    @staticmethod
    def _unit_mapper(unit):
        return {
            "Hz": (FREQUENCY_HERTZ, (None, SensorDeviceClass.FREQUENCY)),
            "kW": (POWER_KILO_WATT, (None, SensorDeviceClass.POWER)),
            "°C": (TEMP_CELSIUS, (None, SensorDeviceClass.TEMPERATURE)),
            "kg": (MASS_KILOGRAMS, (None, SensorDeviceClass.WEIGHT)),
            "bar": (PRESSURE_BAR, (None, SensorDeviceClass.PRESSURE)),
            "A": (ELECTRIC_CURRENT_MILLIAMPERE, (None, SensorDeviceClass.CURRENT)),
            "s": (TIME_SECONDS, (None, SensorDeviceClass.TIMESTAMP)),
            "V": (ELECTRIC_POTENTIAL_VOLT, (None, SensorDeviceClass.VOLTAGE)),
            "m²": (AREA_SQUARE_METERS, (None, SensorDeviceClass.DATA_SIZE)),
            "%": (PERCENTAGE, (None, SensorDeviceClass.POWER_FACTOR)),
            "W": (POWER_WATT, (None, SensorDeviceClass.ENERGY)),
            "l": (VOLUME_LITERS, (None, SensorDeviceClass.WATER)),
            "mV": (ELECTRIC_POTENTIAL_MILLIVOLT, (None, SensorDeviceClass.VOLTAGE)),
            "W/m²": (IRRADIATION_WATTS_PER_SQUARE_METER, (None, SensorDeviceClass.POWER)),
            "Pa": (PRESSURE_PA, (None, SensorDeviceClass.PRESSURE)),
            "bool": (None, (None, SensorDeviceClass.REACTIVE_POWER))
        }.get(unit, (None, None))

    def __init__(self, config, hass, name, uri, unit, state_class=SensorStateClass.MEASUREMENT, factor=1.0):
        """
        Initialize sensor.
        
        To show all values: http://192.168.178.75:8080/user/menu
        
        There are:
          - entity_id - used to reference id, english, e.g. "eta_outside_temperature"
          - name - Friendly name, e.g "Außentemperatur" in local language
          - unique_id - globally unique id of sensor, e.g. "eta_11.123488_outside_temp", based on serial number
        
        """
        _LOGGER.info(f"ETA Integration - Init Sensor: {name}")

        self._attr_state_class = state_class

        id = name.lower().replace(' ', '_')
        self._attr_name = name  # friendly name - local language
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, "eta_" + id, hass=hass)

        hassio_unit, device_class = self._unit_mapper(unit)

        if device_class is not None:
            self._attr_device_class = device_class

        if hassio_unit is not None:
            self._attr_native_unit_of_measurement = hassio_unit
        else:
            if unit != "bool":
                self._attr_name += f" {unit}"

        self.uri = uri
        self.factor = factor
        self.config = config
        self.host = config.get(CONF_HOST)
        self.port = config.get(CONF_PORT)

        # This must be a unique value within this domain. This is done use serial number of device
        serial1 = requests.get(get_base_url(config, VAR_PATH) + "/40/10021/0/0/12489")
        serial2 = requests.get(get_base_url(config, VAR_PATH) + "/40/10021/0/0/12490")

        # Parse
        serial1 = xmltodict.parse(serial1.text)
        serial1 = serial1['eta']['value']['@strValue']
        serial2 = xmltodict.parse(serial2.text)
        serial2 = serial2['eta']['value']['@strValue']

        self._attr_unique_id = "eta" + "_" + serial1 + "." + serial2 + "." + name.replace(" ", "_")

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        TODO: readme: activate first: http://www.holzheizer-forum.de/attachment/28434-eta-restful-v1-1-pdf/
        """
        value, unit = get_measure(self.config, self.uri)
        if value:
            self._attr_native_value = value
