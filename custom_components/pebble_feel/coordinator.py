from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PebbleFeelClient, PebbleState
from .const import DEFAULT_POLL_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PebbleCoordinator(DataUpdateCoordinator[PebbleState]):
    """Coordinates optional polling of enable/mode state."""

    def __init__(self, hass, client: PebbleFeelClient, poll_interval: int = DEFAULT_POLL_INTERVAL):
        super().__init__(
            hass,
            _LOGGER,
            name="Pebble Feel",
            update_interval=timedelta(seconds=poll_interval),
        )
        self.client = client
        self.mode_polling_enabled = True

    async def _async_update_data(self) -> PebbleState:
        if not self.mode_polling_enabled:
            return self.data or PebbleState()
        try:
            return await self.client.read_state()
        except Exception as e:
            raise UpdateFailed(str(e)) from e
