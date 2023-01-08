"""
Platform for ETA sensor integration in Home Assistant

Help Links:
 Entity Source: https://github.com/home-assistant/core/blob/dev/homeassistant/helpers/entity.py
 SensorEntity derives from Entity https://github.com/home-assistant/core/blob/dev/homeassistant/components/sensor/__init__.py


author hubtub2

"""

from __future__ import annotations
import logging
import os

import requests
import voluptuous as vol
import xmltodict
from lxml import etree
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
    PLATFORM_SCHEMA,
    ENTITY_ID_FORMAT
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.entity import generate_entity_id

# See https://github.com/home-assistant/core/blob/dev/homeassistant/const.py
from homeassistant.const import (CONF_HOST, CONF_PORT)

from .sensors_default import SENSORS_DEFAULT

_LOGGER = logging.getLogger(__name__)
VAR_PATH = "/user/var"
MENU_PATH = "/user/menu"

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

    add_entities([
        EtaSensor(config, hass, sensor.get('name'), sensor.get('uri'), sensor.get('unit'), sensor.get('state_class'),
                  sensor.get('device_class'), sensor.get('factor'))
        for sensor in SENSORS_DEFAULT
    ])

    try:
        from .sensors_custom import SENSORS_CUSTOM
        add_entities([
            EtaSensor(config, hass, sensor.get('name'), sensor.get('uri'), sensor.get('unit'), sensor.get('state_class'),
                      sensor.get('device_class'), sensor.get('factor'))
            for sensor in SENSORS_CUSTOM
        ])
    except ImportError as error:
        _LOGGER.info("ETA Integration - no custom sensors found")


class EtaSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, config, hass, name, uri, unit=None, state_class=SensorStateClass.MEASUREMENT,
                 device_class=SensorDeviceClass.TEMPERATURE, factor=1.0):
        """
        Initialize sensor.
        
        To show all values: http://192.168.178.75:8080/user/menu
        
        There are:
          - entity_id - used to reference id, english, e.g. "eta_outside_temperature"
          - name - Friendly name, e.g "Außentemperatur" in local language
          - unique_id - globally unique id of sensor, e.g. "eta_11.123488_outside_temp", based on serial number
        
        """
        _LOGGER.info("ETA Integration - init sensor")

        self._attr_state_class = state_class
        self._attr_device_class = device_class
        name = name if name else get_entity_name(config, uri)
        id = name.lower().replace(' ', '_')
        self._attr_name = name  # friendly name - local language
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, "eta_" + id, hass=hass)
        # self.entity_description = description
        self._attr_native_unit_of_measurement = unit
        self.uri = VAR_PATH + uri
        self.factor = factor if factor else 1.0
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

        # REST GET
        data = requests.get("http://" + self.host + ":" + str(self.port) + self.uri)
        data = xmltodict.parse(data.text)
        self._attr_native_value = round(int(data['eta']['value']['#text']) * self.factor / int(data['eta']['value']['@scaleFactor']), int(data['eta']['value']['@decPlaces']))
