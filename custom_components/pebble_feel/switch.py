from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]

    async_add_entities([
        PebbleEnableSwitch(coordinator, client, entry),
        PebbleModePollingSwitch(coordinator, entry),
    ])


class PebbleEnableSwitch(SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, client, entry):
        self.coordinator = coordinator
        self.client = client
        self.entry = entry
        self._attr_unique_id = f"{entry.data['address']}_enable"
        self._attr_name = "Enable"

    @property
    def is_on(self):
        return bool(self.coordinator.data.enabled) if self.coordinator.data else False

    async def async_turn_on(self, **kwargs):
        await self.client.write_enable(True)
        if self.coordinator.data:
            self.coordinator.data.enabled = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self.client.write_enable(False)
        if self.coordinator.data:
            self.coordinator.data.enabled = False
        self.async_write_ha_state()

    async def async_update(self):
        await self.coordinator.async_request_refresh()


class PebbleModePollingSwitch(SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry):
        self.coordinator = coordinator
        self.entry = entry
        self._attr_unique_id = f"{entry.data['address']}_mode_polling"
        self._attr_name = "Mode Polling"

    @property
    def is_on(self):
        return self.coordinator.mode_polling_enabled

    async def async_turn_on(self, **kwargs):
        self.coordinator.mode_polling_enabled = True
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self.coordinator.mode_polling_enabled = False
        self.async_write_ha_state()
