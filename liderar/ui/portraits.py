"""Retratos procedurales dibujados con formas simples."""

from __future__ import annotations

import math

import pygame

from .theme import LINE, mix, panel, shade

DEFAULT = {"name": "", "role": "", "skin": (200, 160, 130), "hair": (60, 50, 45),
           "shirt": (70, 80, 110), "accessory": "none"}


def draw_portrait(surf, rect, ch, t, talking=False):
    ch = ch or DEFAULT
    skin, hair, shirt = ch["skin"], ch["hair"], ch["shirt"]
    acc = ch.get("accessory", "none")
    panel(surf, rect, (16, 22, 40), LINE, 16)
    old = surf.get_clip()
    surf.set_clip(rect.inflate(-4, -4))
    cx = rect.centerx
    hr = int(rect.w * 0.21)
    hy = rect.y + int(rect.h * 0.36) + math.sin(t * 2.0) * 3
    # halo de fondo
    pygame.draw.circle(surf, mix((16, 22, 40), shirt, 0.28), (cx, int(hy + 10)), int(hr * 2.1))
    pygame.draw.circle(surf, mix((16, 22, 40), shirt, 0.15), (cx, int(hy + 10)), int(hr * 2.6), 6)
    # cuerpo y cuello
    pygame.draw.ellipse(surf, shirt, (cx - hr * 1.9, hy + hr * 1.05, hr * 3.8, hr * 3.2))
    pygame.draw.rect(surf, shade(skin, -28), (cx - hr * 0.3, hy + hr * 0.8, hr * 0.6, hr * 0.6))
    if acc == "turtleneck":
        pygame.draw.rect(surf, shade(shirt, -15), (cx - hr * 0.5, hy + hr * 0.75, hr * 1.0, hr * 0.7),
                         border_radius=8)
    if acc == "tie":
        pygame.draw.polygon(surf, (235, 235, 240), [(cx - hr * 0.5, hy + hr * 1.05),
                            (cx + hr * 0.5, hy + hr * 1.05), (cx, hy + hr * 1.6)])
        pygame.draw.polygon(surf, (200, 40, 60), [(cx - 9, hy + hr * 1.2), (cx + 9, hy + hr * 1.2),
                            (cx + 14, hy + hr * 2.6), (cx, hy + hr * 2.8), (cx - 14, hy + hr * 2.6)])
    # pelo trasero, orejas, cara
    pygame.draw.ellipse(surf, hair, (cx - hr * 1.05, hy - hr * 1.15, hr * 2.1, hr * 1.7))
    for sx in (-1, 1):
        pygame.draw.circle(surf, shade(skin, -15), (cx + sx * hr * 0.97, hy + hr * 0.1), hr * 0.17)
    pygame.draw.ellipse(surf, skin, (cx - hr * 0.95, hy - hr, hr * 1.9, hr * 2.1))
    # barba
    if acc == "beard":
        pygame.draw.polygon(surf, hair, [(cx - hr * 0.93, hy + hr * 0.05), (cx - hr * 0.8, hy + hr * 0.8),
                            (cx - hr * 0.3, hy + hr * 1.15), (cx + hr * 0.3, hy + hr * 1.15),
                            (cx + hr * 0.8, hy + hr * 0.8), (cx + hr * 0.93, hy + hr * 0.05),
                            (cx + hr * 0.55, hy + hr * 0.45), (cx, hy + hr * 0.4),
                            (cx - hr * 0.55, hy + hr * 0.45)])
    # flequillo / gorra
    if acc == "cap":
        cap = mix(shirt, (0, 170, 255), 0.6)
        pygame.draw.ellipse(surf, cap, (cx - hr * 0.98, hy - hr * 1.18, hr * 1.96, hr * 1.1))
        pygame.draw.rect(surf, shade(cap, -30), (cx - hr * 0.98, hy - hr * 0.2, hr * 2.4, hr * 0.17),
                         border_radius=6)
    else:
        pygame.draw.polygon(surf, hair, [(cx - hr * 0.95, hy - hr * 0.1), (cx - hr * 0.85, hy - hr * 0.8),
                            (cx, hy - hr * 1.12), (cx + hr * 0.85, hy - hr * 0.8),
                            (cx + hr * 0.95, hy - hr * 0.1), (cx + hr * 0.55, hy - hr * 0.55),
                            (cx - hr * 0.25, hy - hr * 0.6)])
    # ojos con parpadeo
    blink = (t % 3.6) < 0.13
    for sx in (-1, 1):
        ex, ey = cx + sx * hr * 0.4, hy + hr * 0.12
        if blink:
            pygame.draw.line(surf, (30, 25, 25), (ex - 9, ey), (ex + 9, ey), 3)
        else:
            pygame.draw.ellipse(surf, (245, 245, 250), (ex - 10, ey - 8, 20, 16))
            pygame.draw.circle(surf, (30, 28, 40), (ex + math.sin(t * 0.8) * 2, ey), 5)
        pygame.draw.line(surf, shade(hair, -10), (ex - 11, ey - 14), (ex + 11, ey - 14 - sx * 2), 3)
        if acc == "glasses":
            pygame.draw.circle(surf, (20, 20, 30), (ex, ey), 17, 3)
    if acc == "glasses":
        pygame.draw.line(surf, (20, 20, 30), (cx - hr * 0.4 + 17, hy + hr * 0.12),
                         (cx + hr * 0.4 - 17, hy + hr * 0.12), 3)
    # nariz y boca
    pygame.draw.line(surf, shade(skin, -35), (cx, hy + hr * 0.2), (cx - 4, hy + hr * 0.5), 2)
    my = hy + hr * 0.68
    if talking:
        h = 3 + abs(math.sin(t * 14)) * 10
        pygame.draw.ellipse(surf, (60, 20, 30), (cx - 12, my - h / 2, 24, h))
    else:
        pygame.draw.arc(surf, (90, 40, 45), (cx - 15, my - 9, 30, 16), 3.5, 5.9, 3)
    surf.set_clip(old)
