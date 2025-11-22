# ha-pebble-feel

Home Assistant custom integration for the **Pebble Feel** wearable thermostat.

Features:

- **Enable switch**: power on/off (register `0x80`)
- **Mode select**: 7 hot/cool modes (register `0x90`)
- **Mode polling switch**: enable/disable background polling
- **Optional polling**: reads enable + mode and updates HA state

## Installation (HACS)

1. In HACS → Integrations → top right menu → **Custom repositories**
2. Add this repo URL, category **Integration**
3. Install **Pebble Feel**
4. Restart Home Assistant
5. Add integration: Settings → Devices & services → Add integration → **Pebble Feel**

## Manual installation

Copy `custom_components/pebble_feel` into your HA `config/custom_components/` folder and restart.

## Pairing / first setup

Pebble Feel requires bonding.  
During the first setup, put the device into pairing mode (press its button as per manufacturer instructions), then add the integration in Home Assistant.  
HA will store the bonding keys and reconnect without further button presses.

## Entities

- `switch.<name>_enable`
- `select.<name>_mode`
- `switch.<name>_mode_polling`

## Modes

- `cool_low`, `cool_mid`, `cool_high`, `cool_rapid`
- `hot_low`, `hot_mid`, `hot_high`

## Notes

Protocol based on manufacturer \"Pebble Feel Bluetooth Specification\".

## License

MIT
