from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass
from typing import Iterable

RGBA = tuple[int, int, int, int]


def _chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def encode_png(width: int, height: int, rgba: bytes) -> bytes:
    if width <= 0 or height <= 0:
        raise ValueError("PNG dimensions must be positive")
    expected = width * height * 4
    if len(rgba) != expected:
        raise ValueError(f"Expected {expected} RGBA bytes, got {len(rgba)}")
    rows = []
    stride = width * 4
    for y in range(height):
        rows.append(b"\x00" + rgba[y * stride : (y + 1) * stride])
    raw = b"".join(rows)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) + _chunk(
        b"IDAT", zlib.compress(raw, 9)
    ) + _chunk(b"IEND", b"")


def solid_png(width: int, height: int, color: RGBA) -> bytes:
    row = bytes(color) * width
    rgba = row * height
    return encode_png(width, height, rgba)


@dataclass
class Canvas:
    width: int
    height: int
    bg: RGBA = (0, 0, 0, 0)

    def __post_init__(self) -> None:
        self.pixels = bytearray(bytes(self.bg) * self.width * self.height)

    def _idx(self, x: int, y: int) -> int:
        return (y * self.width + x) * 4

    def set_pixel(self, x: int, y: int, color: RGBA) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            i = self._idx(x, y)
            self.pixels[i : i + 4] = bytes(color)

    def blend_pixel(self, x: int, y: int, color: RGBA) -> None:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        sr, sg, sb, sa = color
        if sa == 255:
            self.set_pixel(x, y, color)
            return
        if sa == 0:
            return
        i = self._idx(x, y)
        dr, dg, db, da = self.pixels[i], self.pixels[i + 1], self.pixels[i + 2], self.pixels[i + 3]
        a = sa / 255.0
        out_a = int(sa + da * (1 - a))
        if out_a == 0:
            out = (0, 0, 0, 0)
        else:
            out = (
                int(sr * a + dr * (1 - a)),
                int(sg * a + dg * (1 - a)),
                int(sb * a + db * (1 - a)),
                out_a,
            )
        self.pixels[i : i + 4] = bytes(out)

    def rect(self, x0: int, y0: int, x1: int, y1: int, color: RGBA) -> None:
        for y in range(max(0, y0), min(self.height, y1)):
            for x in range(max(0, x0), min(self.width, x1)):
                self.blend_pixel(x, y, color)

    def rounded_rect(self, x0: int, y0: int, x1: int, y1: int, radius: int, color: RGBA) -> None:
        radius = max(0, radius)
        for y in range(max(0, y0), min(self.height, y1)):
            for x in range(max(0, x0), min(self.width, x1)):
                cx = x
                cy = y
                if x < x0 + radius:
                    cx = x0 + radius
                elif x >= x1 - radius:
                    cx = x1 - radius - 1
                if y < y0 + radius:
                    cy = y0 + radius
                elif y >= y1 - radius:
                    cy = y1 - radius - 1
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= radius * radius:
                    self.blend_pixel(x, y, color)

    def circle(self, cx: int, cy: int, radius: int, color: RGBA) -> None:
        r2 = radius * radius
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r2:
                    self.blend_pixel(x, y, color)

    def ring(self, cx: int, cy: int, radius: int, thickness: int, color: RGBA) -> None:
        outer = radius * radius
        inner = max(0, radius - thickness) ** 2
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                d = (x - cx) * (x - cx) + (y - cy) * (y - cy)
                if inner <= d <= outer:
                    self.blend_pixel(x, y, color)

    def line(self, x0: int, y0: int, x1: int, y1: int, color: RGBA, thickness: int = 1) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        r = max(0, thickness // 2)
        while True:
            self.circle(x, y, r, color) if r else self.blend_pixel(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def polygon(self, points: Iterable[tuple[int, int]], color: RGBA) -> None:
        pts = list(points)
        if len(pts) < 3:
            return
        min_y = max(0, min(y for _, y in pts))
        max_y = min(self.height - 1, max(y for _, y in pts))
        for y in range(min_y, max_y + 1):
            xs: list[float] = []
            for i, (x1, y1) in enumerate(pts):
                x2, y2 = pts[(i + 1) % len(pts)]
                if y1 == y2:
                    continue
                if (y >= min(y1, y2)) and (y < max(y1, y2)):
                    t = (y - y1) / (y2 - y1)
                    xs.append(x1 + t * (x2 - x1))
            xs.sort()
            for i in range(0, len(xs), 2):
                if i + 1 >= len(xs):
                    break
                for x in range(max(0, int(xs[i])), min(self.width, int(xs[i + 1]) + 1)):
                    self.blend_pixel(x, y, color)

    def to_png(self) -> bytes:
        return encode_png(self.width, self.height, bytes(self.pixels))
