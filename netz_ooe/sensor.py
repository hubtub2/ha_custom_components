"""
Platform for Netz OOe sensor integration in Home Assistant

Help Links:
 Entity Source: https://github.com/home-assistant/core/blob/dev/homeassistant/helpers/entity.py
 SensorEntity derives from Entity https://github.com/home-assistant/core/blob/dev/homeassistant/components/sensor/__init__.py


author Peda1996

"""

from __future__ import annotations

from datetime import timedelta

import json
import logging

import requests
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
    PLATFORM_SCHEMA,
    ENTITY_ID_FORMAT
)

from homeassistant.const import UnitOfEnergy, CONF_URL, CONF_NAME

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.entity import generate_entity_id

# See https://github.com/home-assistant/core/blob/dev/homeassistant/const.py
from homeassistant.const import (CONF_USERNAME, CONF_PASSWORD)

# See https://community.home-assistant.io/t/problem-with-scan-interval/139031
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_URL): cv.string,
    vol.Required(CONF_NAME): cv.string
})

# TODO make this configurable
# only fetch the site every 15 minutes
SCAN_INTERVAL = timedelta(hours=1)


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""

    _LOGGER.info("Netz OOE Integration - setup platform")
    add_entities([SmartMeter(
        config, hass
    )])


class SmartMeter(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, config, hass):
        """
        Initialize sensor.

        """
        _LOGGER.info(f"Netz OOE Integration - Init Sensor: {config.get(CONF_NAME)}")

        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_state_class = SensorStateClass.TOTAL

        _id = config.get(CONF_NAME).lower().replace(' ', '_')
        self._attr_name = config.get(CONF_NAME)
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, "netz_ooe_" + _id, hass=hass)

        self.config = config
        self.update_url = config.get(CONF_URL)
        self.username = config.get(CONF_USERNAME)
        self.password = config.get(CONF_PASSWORD)

        self._attr_unique_id = "netz_ooe_" + _id

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        TODO: readme: activate first: https://www.meineta.at/javax.faces.resource/downloads/ETA-RESTful-v1.2.pdf.xhtml?ln=default&v=0
        """

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'client-id': 'netzonline',
            'Origin': 'https://eservice.netzooe.at',
            'Referer': 'https://eservice.netzooe.at/app/login',
        }

        json_data = {
            'j_username': self.username,
            'j_password': self.password
        }

        s = requests.Session()
        s.post('https://eservice.netzooe.at/service/j_security_check', headers=headers, json=json_data)

        r = s.get(self.update_url)
        data = json.loads(r.content.decode("utf8"))

        self._attr_native_value = float(data["contracts"][0]
                                        ["pointOfDelivery"]["lastReadings"]
                                        ["values"][0]["newResult"]
                                        ["readingValue"])
