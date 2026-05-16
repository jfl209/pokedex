# Pi Zero 2 W Mainboard — KiCad Project

## Overview

Custom PCB that the Pi Zero 2 W plugs into via GPIO header. Integrates:
- USB-C charging (MCP73871 power-path manager)
- 3.7V→5.2V boost (TPS61090)
- Soft-latch power control via TPS61090 EN pin
- 1.54" 240×240 TFT display connector (ST7789, SPI)
- MAX98357A I2S DAC + Class D amp with speaker connector
- ATtiny1614 keyboard controller (on-board, SOIC-14)
- 48 switches + 48 diodes (charlieplex matrix, directly on PCB)

Board dimensions: 76 × 114 mm (3" × 4.5"), 2-layer, 1.6mm thickness.

## Power Architecture

Based on the **Adafruit PowerBoost 1000C** (open-source hardware).
Copy the MCP73871 and TPS61090 subcircuits with all component values
from the PowerBoost 1000C schematic (Eagle files on GitHub).

### Changes from PowerBoost 1000C

| What | PowerBoost 1000C | This board |
|------|-----------------|------------|
| USB input | Micro-USB | USB-C with 5.1kΩ CC pulldowns |
| USB output | USB-A jack + iOS resistors | Removed (not needed) |
| Power LED | Blue LED on 5V output | Removed (saves ~5mA) |
| EN pin | Pulled high to VS (always on) | Driven by POWER_CTRL net (soft-latch) |
| Low battery | Red LED on LBO | Keep LED, optionally route to Pi GPIO |

### Soft-Latch Power Control

No P-FET or external latch circuit needed! The TPS61090's EN pin does it all:

- R5 (100kΩ) pulls EN to GND → boost OFF by default
- ATtiny1614 PB3 drives POWER_CTRL HIGH → boost ON (Pi boots)
- Pi GPIO 26 also drives POWER_CTRL HIGH (wired-OR with ATtiny)
- Pi shutdown releases GPIO 26, ATtiny releases PB3 → EN goes LOW → power off
- Quiescent draw in off state: ~20µA (TPS61090 disabled)

### ATtiny1614 Always-On Power

The ATtiny1614 (on the keyboard PCB) connects directly to VLIPO (raw battery)
through J1 pin 1. It draws ~1µA in power-down sleep mode, waking on
pin-change interrupt when the ON key is pressed.

## Net Names

| Net | Description | Source |
|-----|-------------|--------|
| VBUS | USB-C 5V input | J6 USB-C connector |
| VLIPO | Raw battery (3.0–4.2V) | J2 LiPo JST connector |
| VBAT_OUT | MCP73871 OUT (load-shared) | U1 pin 19 |
| 5V_BOOST | TPS61090 output (5.2V) | U2 pin 1 → Pi pin 2 |
| POWER_CTRL | Soft-latch enable | ATtiny PB3 + Pi GPIO 26 → U2 EN |
| +3V3 | Pi 3.3V rail (from Pi's regulator) | Pi pin 1 |
| SDA | I2C data | Pi GPIO 2 (pin 3) ↔ ATtiny PA1 |
| SCL | I2C clock | Pi GPIO 3 (pin 5) ↔ ATtiny PA2 |

## GPIO Assignment (Pi Zero 2 W)

| GPIO | Pin | Function | Peripheral |
|------|-----|----------|-----------|
| 2 | 3 | I2C SDA | Keyboard (ATtiny1614) |
| 3 | 5 | I2C SCL | Keyboard (ATtiny1614) |
| 4 | 7 | SD_MODE | MAX98357A shutdown |
| 8 | 24 | SPI0 CE0 | Display TFT CS |
| 10 | 19 | SPI0 MOSI | Display data |
| 11 | 23 | SPI0 SCLK | Display clock |
| 18 | 12 | I2S BCLK | MAX98357A bit clock |
| 19 | 35 | I2S LRCLK | MAX98357A word clock |
| 21 | 40 | I2S DIN | MAX98357A data in |
| 25 | 22 | DC | Display data/command |
| 26 | 37 | KEEP_ALIVE | POWER_CTRL (soft-latch) |

## Connector Pinouts

### J1 — Keyboard (5-pin, to keyboard PCB)
| Pin | Signal | Notes |
|-----|--------|-------|
| 1 | VLIPO | ATtiny always-on power (3.0–4.2V) |
| 2 | SDA | I2C data (Pi has 1.8kΩ pull-up) |
| 3 | SCL | I2C clock (Pi has 1.8kΩ pull-up) |
| 4 | GND | Ground |
| 5 | POWER_CTRL | ATtiny PB3 output to TPS61090 EN |

### J2 — LiPo Battery (JST-PH 2-pin)
| Pin | Signal |
|-----|--------|
| 1 | VLIPO (+) |
| 2 | GND (−) |

### J4 — Display (7-pin header)
| Pin | Signal | Pi GPIO |
|-----|--------|---------|
| 1 | 3.3V | Pin 1 |
| 2 | GND | Pin 6 |
| 3 | SPI_SCLK | GPIO 11 |
| 4 | SPI_MOSI | GPIO 10 |
| 5 | SPI_CE0 | GPIO 8 |
| 6 | DC | GPIO 25 |
| 7 | RST | GPIO 24 (or tie to 3.3V via RC) |

### J5 — Speaker (JST-PH 2-pin)
| Pin | Signal |
|-----|--------|
| 1 | OUTP |
| 2 | OUTN |

## BOM (Key Components)

| Ref | Part | Package | Value/Part # | Notes |
|-----|------|---------|-------------|-------|
| U1 | MCP73871-2CCI/ML | QFN-20 4×4mm | — | Copy from PowerBoost |
| U2 | TPS61090RSAR | PVQFN-16 | — | Copy from PowerBoost |
| U3 | MAX98357AETE | TQFN-16 3×3mm | — | I2S DAC + amp |
| J6 | USB-C receptacle | GCT USB4085 | — | Mid-mount |
| J3 | 2×20 female header | 2.54mm pitch | — | For Pi Zero GPIO |
| J1 | 1×5 pin header | 2.54mm pitch | — | Keyboard cable |
| J2 | JST-PH 2-pin | S2B-PH-K | — | LiPo battery |
| J4 | 1×7 pin header | 2.54mm pitch | — | Display module |
| J5 | JST-PH 2-pin | S2B-PH-K | — | Speaker |
| L1 | Inductor | 5×5mm | 6.8µH | TDK VLC5045 or similar |
| R1,R2 | Resistor | 0402 | 5.1kΩ | USB-C CC pulldowns |
| R5 | Resistor | 0402 | 100kΩ | EN pull-down (soft-latch) |
| — | (PowerBoost passives) | 0402/0805 | Various | Copy values from PB1000C |

## Getting Started

1. Open `pi-zero-mainboard.kicad_pro` in KiCad 8
2. The schematic has all symbols defined inline (no external libs needed)
3. Download the [Adafruit PowerBoost 1000C Eagle files](https://github.com/adafruit/Adafruit-PowerBoost-1000C)
4. Reference the Eagle schematic for exact MCP73871 and TPS61090 passive values
5. Add the PowerBoost passives to this schematic around U1 and U2
6. Assign footprints (most are pre-assigned, verify against KiCad 8 libraries)
7. Run ERC, then transfer to PCB editor
8. Place components per the layout diagram, route traces

## PCB Layout Notes

- **Power traces**: Use 0.5mm minimum for VLIPO, VBAT_OUT, 5V_BOOST
- **TPS61090 layout**: Keep L1, input cap, and output cap as close as possible
  to the IC. Follow TI's layout guidelines in the TPS61090 datasheet.
- **Ground plane**: Pour copper on both layers, stitched with vias
- **USB-C**: Edge-mount at bottom of board
- **Battery**: JST connector on bottom edge, pouch cell sits under the PCB
- **Display/audio headers**: Right side of board for cable routing
