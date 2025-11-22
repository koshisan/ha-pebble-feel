from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, MODES, MODE_TO_VALUE


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]

    async_add_entities([PebbleModeSelect(coordinator, client, entry)])


class PebbleModeSelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_options = MODES

    def __init__(self, coordinator, client, entry):
        self.coordinator = coordinator
        self.client = client
        self.entry = entry
        self._attr_unique_id = f"{entry.data['address']}_mode"
        self._attr_name = "Mode"

    @property
    def current_option(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data.mode_name

    async def async_select_option(self, option: str):
        await self.client.write_mode(option, auto_enable=True)

        # Optimistic local state update
        if self.coordinator.data:
            self.coordinator.data.enabled = True
            self.coordinator.data.mode_value = MODE_TO_VALUE.get(option, self.coordinator.data.mode_value)

        if self.coordinator.mode_polling_enabled:
            await self.coordinator.async_request_refresh()

        self.async_write_ha_state()

    async def async_update(self):
        await self.coordinator.async_request_refresh()
