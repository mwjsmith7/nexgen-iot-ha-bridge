# NexGen IoT — Home Assistant Integration

A HACS custom integration that connects your [NexGen IoT](https://nexgen-iot.co.za) devices directly to Home Assistant via the cloud API — no MQTT broker required.

## Features

- **Relay switches** — control gate/door relays and power outputs
- **Trigger buttons** — momentary pulse for gate openers and door bells
- **Door / motion sensors** — binary sensors for open/closed and motion states
- **Environmental sensors** — temperature, humidity, AQI, and CO₂

All entities update every 30 seconds via the NexGen IoT cloud API.

## Installation

### HACS (recommended)

1. Open HACS → **Integrations** → ⋮ → **Custom repositories**
2. Add `https://github.com/nexgen-iot/nexgen-iot-ha-integration` as an **Integration**
3. Install **NexGen IoT** from the HACS store
4. Restart Home Assistant

### Manual

Copy `custom_components/nexgen_iot/` into your HA `config/custom_components/` directory and restart.

## Setup

1. Go to **Settings → Devices & Services → Add Integration** and search for **NexGen IoT**
2. Leave the API URL as default (or enter your self-hosted URL)
3. Note the link code shown on screen
4. Visit [https://portal.nexgen-iot.co.za/ha-link](https://portal.nexgen-iot.co.za/ha-link) and enter the code
5. Click **Submit** in Home Assistant — your devices will appear automatically

## Entities

| Device type | Entities created |
|---|---|
| NexGate Pro / NexDoor Pro | Relay switch(es), Trigger button, Door sensor |
| NexSwitch Dual | 2× Relay switches |
| NexSense T/H | Temperature, Humidity sensors |
| NexSense AQ | Temperature, Humidity, AQI, CO₂ sensors |
| NexDoor Sensor | Door binary sensor |

## Requirements

- Home Assistant 2024.1.0 or newer
- Active NexGen IoT account at [nexgen-iot.co.za](https://nexgen-iot.co.za)

## Support

- Documentation: [nexgen-iot.co.za/home-assistant](https://nexgen-iot.co.za/home-assistant)
- Issues: [GitHub Issues](https://github.com/mwjsmith7/nexgen-iot-ha-bridge/issues)
