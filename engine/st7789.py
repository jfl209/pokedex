"""
Minimal ST7789 direct-SPI display driver.

Drives the display over spidev + RPi.GPIO with no kernel framebuffer
driver required — works regardless of Pi OS version or dtoverlay support.

Wiring (matches project schematic):
    SCK  → GPIO 11  (SPI0 CLK,  handled by spidev)
    MOSI → GPIO 10  (SPI0 MOSI, handled by spidev)
    CS   → GPIO 8   (SPI0 CE0,  handled by spidev)
    DC   → GPIO 25
    RST  → GPIO 24
    BL   → 3.3V     (hardwired, no software control)
"""

import time
import numpy as np
import spidev
import RPi.GPIO as GPIO

# ── ST7789 command bytes ────────────────────────────────────────────────────
_SWRESET = 0x01
_SLPOUT  = 0x11
_NORON   = 0x13
_INVON   = 0x21
_DISPON  = 0x29
_CASET   = 0x2A
_RASET   = 0x2B
_RAMWR   = 0x2C
_MADCTL  = 0x36
_COLMOD  = 0x3A

# MADCTL values for each 90° rotation step
_MADCTL_MAP = {0: 0x00, 90: 0x60, 180: 0xC0, 270: 0xA0}


class ST7789:
    def __init__(
        self,
        width: int = 240,
        height: int = 240,
        dc_pin: int = 25,
        rst_pin: int = 24,
        spi_bus: int = 0,
        spi_device: int = 0,
        spi_speed_hz: int = 64_000_000,
        rotation: int = 0,
        x_offset: int = 0,
        y_offset: int = 0,
    ) -> None:
        self._w    = width
        self._h    = height
        self._dc   = dc_pin
        self._rst  = rst_pin
        self._x0   = x_offset
        self._y0   = y_offset

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._dc,  GPIO.OUT)
        GPIO.setup(self._rst, GPIO.OUT)

        self._spi = spidev.SpiDev()
        self._spi.open(spi_bus, spi_device)
        self._spi.max_speed_hz = spi_speed_hz
        self._spi.mode = 0

        self._reset()
        self._init(rotation)

    # ── low-level helpers ───────────────────────────────────────────────────

    def _reset(self) -> None:
        GPIO.output(self._rst, GPIO.HIGH); time.sleep(0.05)
        GPIO.output(self._rst, GPIO.LOW);  time.sleep(0.05)
        GPIO.output(self._rst, GPIO.HIGH); time.sleep(0.15)

    def _cmd(self, cmd: int) -> None:
        GPIO.output(self._dc, GPIO.LOW)
        self._spi.writebytes([cmd])

    def _data(self, data) -> None:
        GPIO.output(self._dc, GPIO.HIGH)
        if isinstance(data, int):
            self._spi.writebytes([data])
        else:
            self._spi.writebytes2(bytes(data))

    # ── initialisation sequence ─────────────────────────────────────────────

    def _init(self, rotation: int) -> None:
        self._cmd(_SWRESET); time.sleep(0.15)
        self._cmd(_SLPOUT);  time.sleep(0.50)

        self._cmd(_COLMOD); self._data(0x55)   # 16-bit colour (RGB565)

        madctl = _MADCTL_MAP.get(rotation, 0x00)
        self._cmd(_MADCTL); self._data(madctl)

        # Set the full 240×240 address window
        x1 = self._x0 + self._w - 1
        y1 = self._y0 + self._h - 1
        self._cmd(_CASET)
        self._data([self._x0 >> 8, self._x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        self._cmd(_RASET)
        self._data([self._y0 >> 8, self._y0 & 0xFF, y1 >> 8, y1 & 0xFF])

        # Colour inversion required by most 240×240 ST7789 panels
        self._cmd(_INVON)
        self._cmd(_NORON)
        self._cmd(_DISPON); time.sleep(0.10)
        print("st7789: display initialised")

    # ── frame output ────────────────────────────────────────────────────────

    def blit_surface(self, surface) -> None:
        """Push a pygame Surface to the display (RGB888 → RGB565 over SPI)."""
        import pygame.surfarray

        # surfarray shape is (x, y, 3); transpose to row-major (y, x, 3)
        arr = pygame.surfarray.array3d(surface).transpose(1, 0, 2).astype(np.uint16)

        r = (arr[:, :, 0] >> 3) & 0x1F
        g = (arr[:, :, 1] >> 2) & 0x3F
        b = (arr[:, :, 2] >> 3) & 0x1F
        rgb565 = ((r << 11) | (g << 5) | b).byteswap()
        data   = rgb565.tobytes()

        self._cmd(_RAMWR)
        # Send in 4096-byte chunks — the Linux spidev kernel buffer is 4096 bytes
        # by default. The ST7789 continues its internal address auto-increment
        # across CS toggles after RAMWR, so chunked writes are safe.
        GPIO.output(self._dc, GPIO.HIGH)
        for i in range(0, len(data), 4096):
            self._spi.writebytes2(data[i : i + 4096])

    def cleanup(self) -> None:
        self._spi.close()
        GPIO.cleanup()
