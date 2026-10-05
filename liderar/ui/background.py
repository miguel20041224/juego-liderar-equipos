"""Fondo animado: degradado, skyline con ventanas, circuitos y partículas."""

from __future__ import annotations

import math
import random

import pygame

from .theme import ACCENT, H, W, mix


class Background:
    def __init__(self):
        rng = random.Random(7)
        self.t = 0.0
        self.base = pygame.Surface((W, H))
        for y in range(H):
            pygame.draw.line(self.base, mix((9, 12, 24), (22, 24, 52), y / H), (0, y), (W, y))
        self.windows = []
        x = -10
        while x < W:
            bw = rng.randint(50, 110)
            bh = rng.randint(120, 330)
            top = H - bh
            pygame.draw.rect(self.base, (14, 18, 34), (x, top, bw, bh))
            pygame.draw.rect(self.base, (24, 30, 54), (x, top, bw, bh), 1)
            for wx in range(x + 8, x + bw - 10, 16):
                for wy in range(top + 10, H - 10, 20):
                    self.windows.append((pygame.Rect(wx, wy, 8, 10), rng.random() * 6.28,
                                         rng.uniform(0.3, 1.2)))
            x += bw + rng.randint(2, 10)
        self.traces = []
        for _ in range(9):
            px, py = rng.randrange(0, W, 40), rng.randrange(40, 400, 40)
            pts = [(px, py)]
            for _ in range(rng.randint(3, 5)):
                if rng.random() < 0.5:
                    px += rng.choice((-1, 1)) * rng.randrange(80, 240, 40)
                else:
                    py += rng.choice((-1, 1)) * rng.randrange(40, 160, 40)
                pts.append((px, py))
            self.traces.append((pts, rng.random()))
        self.parts = [[rng.random() * W, rng.random() * H, rng.uniform(8, 30), rng.uniform(1, 3)]
                      for _ in range(50)]

    def update(self, dt):
        self.t += dt
        for p in self.parts:
            p[1] -= p[2] * dt
            if p[1] < -5:
                p[1], p[0] = H + 5, random.random() * W

    def draw(self, surf, title=False):
        surf.blit(self.base, (0, 0))
        t = self.t
        if title:
            for r, ph, sp in self.windows:
                if math.sin(t * sp + ph) > 0.55:
                    pygame.draw.rect(surf, (255, 214, 120), r)
        for pts, off in self.traces:
            col = (28, 52, 84) if title else (20, 32, 56)
            pygame.draw.lines(surf, col, False, pts, 2)
            for p in pts:
                pygame.draw.circle(surf, col, p, 4)
            # pulso de datos recorriendo la traza
            seg = (t * 0.6 + off) % 1.0 * (len(pts) - 1)
            i = min(int(seg), len(pts) - 2)
            f = seg - i
            a, b = pts[i], pts[i + 1]
            pygame.draw.circle(surf, ACCENT, (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f), 3)
        for x, y, _, s in self.parts:
            pygame.draw.circle(surf, (60, 90, 130), (x, y), s)
