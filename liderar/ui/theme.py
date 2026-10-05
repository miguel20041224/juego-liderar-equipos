"""Tema, widgets y utilidades de dibujo compartidas por toda la UI."""

from __future__ import annotations

import math

import pygame

from ..engine import POWER_TYPES, STAT_LABELS, money

W, H = 1280, 720

BG = (11, 14, 24)
PANEL = (22, 28, 46)
PANEL2 = (32, 41, 68)
LINE = (56, 68, 104)
TEXT = (232, 236, 248)
MUTED = (146, 156, 184)
ACCENT = (0, 205, 255)
ACCENT2 = (255, 170, 60)
GOOD = (76, 217, 130)
BAD = (255, 92, 104)
GOLD = (255, 210, 74)
PURPLE = (160, 120, 255)

STAT_COLORS = {
    "cash": GOLD,
    "morale": (255, 120, 170),
    "reputation": PURPLE,
    "progress": ACCENT,
    "innovation": GOOD,
}

_fonts: dict = {}


def font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _fonts:
        try:
            _fonts[key] = pygame.font.SysFont(
                "dejavusans,notosans,liberationsans,arial,freesans", size, bold=bold)
        except (OSError, pygame.error):
            _fonts[key] = pygame.font.Font(None, int(size * 1.25))
    return _fonts[key]


def mix(a, b, t: float):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(c, d: int):
    return tuple(max(0, min(255, v + d)) for v in c)


def text(surf, s, f, color, pos, anchor="topleft"):
    img = f.render(s, True, color)
    r = img.get_rect(**{anchor: pos})
    surf.blit(img, r)
    return r


def wrap(f, s: str, w: int) -> list[str]:
    lines = []
    for para in s.split("\n"):
        cur = ""
        for word in para.split(" "):
            t = f"{cur} {word}" if cur else word
            if f.size(t)[0] <= w or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def fit(f, s: str, w: int) -> str:
    if f.size(s)[0] <= w:
        return s
    while s and f.size(s + "…")[0] > w:
        s = s[:-1]
    return s + "…"


def draw_lines(surf, lines, f, color, x, y, gap=3, center=False):
    lh = f.get_linesize() + gap
    for ln in lines:
        text(surf, ln, f, color, (x, y), "midtop" if center else "topleft")
        y += lh
    return y


def panel(surf, rect, fill=PANEL, border=LINE, radius=12, width=1):
    pygame.draw.rect(surf, fill, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surf, border, rect, width, border_radius=radius)


def star(surf, cx, cy, r, color):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(surf, color, pts)


def header(surf, s: str, y: int = 94, width: int = 1200, size: int = 20) -> int:
    """Texto introductorio de la escena en una barra. Devuelve el y inferior."""
    f = font(size)
    lines = wrap(f, s, width - 36)[:4]
    h = len(lines) * (f.get_linesize() + 2) + 16
    panel(surf, (40, y, width, h), PANEL, LINE, 10)
    pygame.draw.rect(surf, ACCENT, (40, y + 6, 4, h - 12), border_radius=2)
    draw_lines(surf, lines, f, TEXT, 58, y + 8, 2)
    return y + h


def fmt_effects(eff: dict) -> list[str]:
    out = []
    for k, v in (eff or {}).items():
        if k == "cash":
            out.append(("+" if v >= 0 else "-") + money(abs(v)) + " Dinero")
        elif k in STAT_LABELS:
            out.append(f"{v:+d} {STAT_LABELS[k]}")
        elif k.startswith("power."):
            out.append(f"{v:+d} Poder {POWER_TYPES.get(k[6:], k[6:])}")
        elif k.startswith("rival."):
            out.append(f"{v:+d} Rival ({k[6:]})")
    return out


def change_color(s: str):
    return BAD if s.startswith("-") else GOOD


class Typewriter:
    def __init__(self, s: str, f, width: int, cps: float = 70):
        self.f = f
        self.lines = wrap(f, s, width)
        self.total = sum(len(ln) for ln in self.lines)
        self.pos = 0.0
        self.cps = cps
        self.lh = f.get_linesize() + 3

    @property
    def done(self) -> bool:
        return self.pos >= self.total

    @property
    def height(self) -> int:
        return len(self.lines) * self.lh

    def update(self, dt):
        self.pos = min(self.total, self.pos + self.cps * dt)

    def complete(self):
        self.pos = self.total

    def draw(self, surf, x, y, color=TEXT):
        n = int(self.pos)
        for ln in self.lines:
            if n <= 0:
                break
            surf.blit(self.f.render(ln[:n], True, color), (x, y))
            n -= len(ln)
            y += self.lh


class Button:
    def __init__(self, x, y, w, label, key=None, size=21, primary=False, min_h=46,
                 center=False):
        self.f = font(size)
        self.key = key
        self.primary = primary
        self.center = center
        self.enabled = True
        self.selected = False
        self.tx = 52 if key else 18
        self.label = label
        self.lines = wrap(self.f, label, w - self.tx - 14)
        h = max(min_h, len(self.lines) * self.f.get_linesize() + 20)
        self.rect = pygame.Rect(x, y, w, h)
        self.hover = 0.0

    def hit(self, pos) -> bool:
        return self.enabled and self.rect.collidepoint(pos)

    def is_hover(self) -> bool:
        return self.enabled and self.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self, surf):
        self.hover += ((1.0 if self.is_hover() else 0.0) - self.hover) * 0.3
        base = (0, 110, 150) if self.primary else PANEL2
        hot = (0, 160, 205) if self.primary else (46, 58, 96)
        fill = mix(base, hot, self.hover)
        if not self.enabled:
            fill = (26, 30, 44)
        panel(surf, self.rect, fill, None, 10)
        border = ACCENT if (self.hover > 0.5 or self.selected) else LINE
        if self.enabled:
            pygame.draw.rect(surf, border, self.rect, 2 if self.selected else 1, border_radius=10)
        col = TEXT if self.enabled else (96, 104, 128)
        if self.key:
            c = (self.rect.x + 26, self.rect.centery)
            pygame.draw.circle(surf, ACCENT if self.enabled else LINE, c, 14)
            text(surf, str(self.key), font(19, True), BG, c, "center")
        lh = self.f.get_linesize()
        y = self.rect.centery - len(self.lines) * lh // 2
        for ln in self.lines:
            if self.center:
                text(surf, ln, self.f, col, (self.rect.centerx, y), "midtop")
            else:
                text(surf, ln, self.f, col, (self.rect.x + self.tx, y))
            y += lh


class FloatText:
    def __init__(self, s, color, x, y, delay=0.0):
        self.s, self.color, self.x, self.y = s, color, x, y
        self.age = -delay
        self.life = 2.2
        self.img = font(26, True).render(s, True, color)
        self.shadow = font(26, True).render(s, True, (0, 0, 0))

    @property
    def dead(self):
        return self.age > self.life

    def update(self, dt):
        self.age += dt

    def draw(self, surf):
        if self.age < 0:
            return
        a = 255 if self.age < self.life * 0.6 else int(255 * (1 - (self.age - self.life * 0.6) / (self.life * 0.4)))
        y = self.y + 20 - self.age * 38 if self.age < 0.25 else self.y + 20 - self.age * 38
        for img, off in ((self.shadow, 2), (self.img, 0)):
            img.set_alpha(max(0, a))
            r = img.get_rect(midtop=(self.x + off, y + off))
            r.clamp_ip(pygame.Rect(0, 0, W, H))
            surf.blit(img, r)


class Screen:
    """Pantalla base. Las pantallas marcan `finished` cuando terminan."""

    show_hud = True
    is_menu = False

    def __init__(self, app):
        self.app = app
        self.state = app.state
        self.finished = False
        self.age = 0.0

    def handle(self, ev):
        pass

    def update(self, dt):
        self.age += dt

    def draw(self, surf):
        pass

    def auto(self, rng):
        self.finished = True

    def shot_key(self):
        return type(self).__name__
