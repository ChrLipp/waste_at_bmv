"""Platform for sensor integration."""
import homeassistant.helpers.config_validation as cv
import logging
import sys
import voluptuous as vol

from datetime import datetime
from homeassistant.const import (CONF_RESOURCES)
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from .waste_data import WasteData

_LOGGER = logging.getLogger(__name__)

SENSOR_PREFIX = 'Waste '
SENSOR_TYPES = {
    'restmuell': ['Restmüll', '', 'mdi:recycle'],
    'gelbersack': ['Gelber Sack', '', 'mdi:recycle'],
    'papier': ['Papier', '', 'mdi:newspaper-variant-outline'],
}

# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
#     vol.Required(CONF_RESOURCES, default=[]):
#         vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
# })

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required("ort", default="", description="Ortschaft lt. bmv.at"): cv.string,
    vol.Required("strasse", default="", description="Strasse lt. bmv.at"): cv.string,
    vol.Required("hausnummer", default="", description="Hausnummer lt. bmv.at"): cv.string
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.debug("Setup waste API retriever")

    entities = []
    ort = config.get("ort")
    strasse = config.get("strasse")
    hausnummer = config.get("hausnummer")
    data = WasteData(ort, strasse, hausnummer)

    _LOGGER.debug(SENSOR_TYPES)
    for key in SENSOR_TYPES:
        _LOGGER.debug(key)
        entities.append(WasteSensor(data, key))

    add_entities(entities)


class WasteSensor(Entity):
    """Represents a waste sensor."""

    def __init__(self, data, sensor_type):
        self.data = data
        self.type = sensor_type
        self._name = SENSOR_PREFIX + SENSOR_TYPES[self.type][0]
        self._unit = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self._state = None
        
        self._attributes = {}
        self._attributes['display_date'] = '?'
        self._attributes['display_text'] = 'Lade Daten ...'
        self._attributes['display_text_long'] = 'Lade Daten ...'
        self._attributes['days'] = -1

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def extra_state_attributes(self):
        """Return attributes for the sensor."""
        return self._attributes

    def update(self):
        """
        Fetch new state data for the sensor and updates the state.
        Only the first element is taken from the returned list.
        """
        self.data.update()

        try:
            # selects the next date
            if self.type == 'restmuell':
                self._state = next(iter(self.data.restmuell), None)
            elif self.type == 'gelbersack':
                self._state = next(iter(self.data.gelberSack), None)
            elif self.type == 'papier':
                self._state = next(iter(self.data.papier), None)

            if self._state is not None:
                weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
                self._attributes['days'] = (self._state - datetime.now().date()).days
                if self._attributes['days'] == 0:
                    printtext = "heute"
                elif self._attributes['days'] == 1:
                    printtext = "morgen"
                elif self._attributes['days'] < 0:
                    self.data.force_update()
                    self.update()
                else:
                    printtext = '{} Tage'.format(self._attributes['days'])
                self._attributes['display_text'] = printtext
                self._attributes['display_text_long'] = self._state.strftime(
                    '{} ({}, %d.%m.)').format(printtext, weekdays[self._state.weekday()])
                self._attributes['display_date'] = self._state.strftime(
                    '{}, %d.%m.').format(weekdays[self._state.weekday()])
        except ValueError:
            self._state = None
