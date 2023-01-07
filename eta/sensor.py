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

from homeassistant.const import UnitOfFrequency, UnitOfPower, UnitOfTemperature, UnitOfMass, UnitOfPressure, \
    UnitOfElectricCurrent, UnitOfTime, UnitOfElectricPotential, AREA_SQUARE_METERS, PERCENTAGE, UnitOfVolume, \
    UnitOfIrradiance, FREQUENCY_HERTZ, PRESSURE_BAR, ELECTRIC_POTENTIAL_VOLT, TIME_SECONDS, POWER_WATT, VOLUME_LITERS, \
    ELECTRIC_POTENTIAL_MILLIVOLT, IRRADIATION_WATTS_PER_SQUARE_METER

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


def get_measure(config, uri):
    val = requests.get(get_base_url(config, VAR_PATH) + uri).content.decode("utf8")
    root = ET.fromstring(val)[0]

    div = pow(0.1, (int(root.attrib.get("decPlaces", "0"))))
    scale = (int(root.attrib.get("scaleFactor", "1")))

    if root.attrib.get('unit', '') != "":
        return float(str(root.text)) * div / scale, root.attrib.get('unit', '')


class Setup:

    def __init__(self, config, hass):
        self.config = config
        self.hass = hass
        self.entities = []

        res = requests.get(get_base_url(self.config, MENU_PATH)).content.decode("utf8")
        self._find_useful_entities(ET.fromstring(res))

    @staticmethod
    def _remove_duplicates_from_name(name):
        words = name.split(" ")
        return " ".join(sorted(set(words), key=words.index))

    def _find_useful_entities(self, root, prev=""):
        for child in root:
            measure = get_measure(self.config, child.attrib['uri'])
            if measure:
                new_name = prev + " " + child.attrib.get("name", "")
                new_name = self._remove_duplicates_from_name(new_name)
                value, unit = measure
                uri = child.attrib['uri']

                self.entities.append(
                    EtaSensor(self.config, self.hass, new_name,
                              uri,
                              unit)
                )

            self._find_useful_entities(child, prev=prev + " " + child.attrib.get("name", ""))


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

    _LOGGER.warning("ETA Integration - setup platform")

    add_entities(Setup(config, hass).entities)


class EtaSensor(SensorEntity):
    """Representation of a Sensor."""

    # _attr_device_class = SensorDeviceClass.TEMPERATURE
    # _attr_state_class = SensorStateClass.MEASUREMENT

    @staticmethod
    def _unit_mapper(unit):
        return {
            "Hz": FREQUENCY_HERTZ,
            "kW": POWER_KILO_WATT,
            "°C": TEMP_CELSIUS,
            "kg": MASS_KILOGRAMS,
            "bar": PRESSURE_BAR,
            "A": UnitOfElectricCurrent,
            "s": TIME_SECONDS,
            "V": ELECTRIC_POTENTIAL_VOLT,
            "m²": AREA_SQUARE_METERS,
            "%": PERCENTAGE,
            "W": POWER_WATT,
            "l": VOLUME_LITERS,
            "mV": ELECTRIC_POTENTIAL_MILLIVOLT,
            "W/m²": IRRADIATION_WATTS_PER_SQUARE_METER,
            "Pa": UnitOfPressure
        }.get(unit, None)

    def __init__(self, config, hass, name, uri, unit, state_class=SensorStateClass.MEASUREMENT,
                 device_class=SensorDeviceClass.TEMPERATURE, factor=1.0):
        """
        Initialize sensor.
        
        To show all values: http://192.168.178.75:8080/user/menu
        
        There are:
          - entity_id - used to reference id, english, e.g. "eta_outside_temperature"
          - name - Friendly name, e.g "Außentemperatur" in local language
          - unique_id - globally unique id of sensor, e.g. "eta_11.123488_outside_temp", based on serial number
        
        """
        _LOGGER.warning(f"ETA Integration - New Sensor: {name}")

        self._attr_state_class = state_class
        self._attr_device_class = device_class

        id = name.lower().replace(' ', '_')
        self._attr_name = name  # friendly name - local language
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, "eta_" + id, hass=hass)

        hassio_unit = self._unit_mapper(unit)
        if hassio_unit is not None:
            self._attr_native_unit_of_measurement = hassio_unit
        else:
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
        self._attr_native_value = value
