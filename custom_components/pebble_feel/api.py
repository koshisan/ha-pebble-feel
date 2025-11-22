from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection

from homeassistant.components import bluetooth

from .const import (
    WRITE_UUID_ALT,
    PIPE_UUID_MAIN,
    CMD_ENABLE,
    CMD_DISABLE,
    CMD_SET_MODE,
    VALUE_TO_MODE,
)

_LOGGER = logging.getLogger(__name__)


def _twos_complement_checksum(data0_to_6: bytes) -> int:
    total = sum(data0_to_6) & 0xFF
    return ((~total) + 1) & 0xFF


def build_read_frame(address: int) -> bytes:
    """Build ASCII-hex READ frame for given address (0x80 enable, 0x90 mode)."""
    d = bytes([0x55, 0xA1, 0xE0, address, 0x00, 0x00, 0x00])
    chk = _twos_complement_checksum(d)
    frame = d + bytes([chk])
    ascii_hex = frame.hex().upper().encode("ascii")
    return ascii_hex + b"\r\n"


def parse_response_ascii(ascii_payload: bytes) -> Optional[tuple[int, int]]:
    """Parse ASCII hex response. Returns (address, value) or None."""
    try:
        s = ascii_payload.strip().decode("ascii")
        raw = bytes.fromhex(s)
        if len(raw) < 8 or raw[0] != 0x55 or raw[1] != 0xA2 or raw[2] != 0xE0:
            return None
        addr = raw[3]
        value = (raw[4] << 8) | raw[5]
        return addr, value
    except Exception:
        return None


@dataclass
class PebbleState:
    enabled: bool = False
    mode_value: int = 0x0000

    @property
    def mode_name(self) -> Optional[str]:
        return VALUE_TO_MODE.get(self.mode_value)


class PebbleFeelClient:
    """Thin GATT client using Home Assistant's BLE stack (2025-compatible)."""

    def __init__(self, hass, address: str):
        self.hass = hass
        self.address = address
        self._client: Optional[BleakClient] = None
        self._notify_lock = asyncio.Lock()
        self._notify_future: Optional[asyncio.Future] = None

    def _get_ble_device(self) -> BLEDevice | None:
        # 2025 API: go via bluetooth module, not wrappers
        return bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )

    async def _connect(self) -> BleakClient:
        ble_device = self._get_ble_device()
        if not ble_device:
            raise RuntimeError("Pebble Feel BLE device not found / not in range")

        client: BleakClient = await establish_connection(
            BleakClient,
            ble_device,
            self.address,
        )
        self._client = client
        return client

    async def _disconnect(self) -> None:
        if self._client and self._client.is_connected:
            try:
                await self._client.disconnect()
            except Exception:
                pass
        self._client = None

    async def write_enable(self, enable: bool) -> None:
        client = await self._connect()
        try:
            cmd = CMD_ENABLE if enable else CMD_DISABLE
            await client.write_gatt_char(WRITE_UUID_ALT, cmd, response=True)
        finally:
            await self._disconnect()

    async def write_mode(self, mode_name: str, auto_enable: bool = True) -> None:
        client = await self._connect()
        try:
            if auto_enable:
                await client.write_gatt_char(WRITE_UUID_ALT, CMD_ENABLE, response=True)
                await asyncio.sleep(0.2)
            cmd = CMD_SET_MODE[mode_name]
            await client.write_gatt_char(WRITE_UUID_ALT, cmd, response=True)
        finally:
            await self._disconnect()

    async def _notify_handler(self, _sender, data: bytearray) -> None:
        async with self._notify_lock:
            if self._notify_future and not self._notify_future.done():
                self._notify_future.set_result(bytes(data))

    async def read_address(self, address: int, timeout: float = 3.0) -> Optional[int]:
        """Read via MAIN pipe by sending READ command and waiting for notify."""
        client = await self._connect()
        try:
            await client.start_notify(PIPE_UUID_MAIN, self._notify_handler)
            await asyncio.sleep(0.1)

            self._notify_future = asyncio.get_running_loop().create_future()
            frame = build_read_frame(address)
            await client.write_gatt_char(PIPE_UUID_MAIN, frame, response=True)

            raw = await asyncio.wait_for(self._notify_future, timeout=timeout)
            parsed = parse_response_ascii(raw)
            if not parsed:
                return None
            addr, value = parsed
            if addr != address:
                return None
            return value
        except Exception as e:
            _LOGGER.debug("read_address failed: %s", e)
            return None
        finally:
            try:
                await client.stop_notify(PIPE_UUID_MAIN)
            except Exception:
                pass
            await self._disconnect()

    async def read_state(self) -> PebbleState:
        enabled_val = await self.read_address(0x80)
        mode_val = await self.read_address(0x90)

        st = PebbleState()
        if enabled_val is not None:
            st.enabled = (enabled_val & 0x0001) == 1
        if mode_val is not None:
            st.mode_value = mode_val
        return st
