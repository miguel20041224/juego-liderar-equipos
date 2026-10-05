"""HUD permanente: stats, poder, equipo y capítulo."""

from __future__ import annotations

import pygame

from ..engine import LEADER_STYLES, POWER_TYPES, STAT_LABELS, STATS, money
from .theme import (BAD, GOOD, LINE, MUTED, STAT_COLORS, TEXT, ACCENT, ACCENT2, W, fit, font,
                    mix, text)

HUD_H = 84
STAT_X0, STAT_W = 262, 150
POWER_X0 = 1036


class HUD:
    def __init__(self, state):
        self.state = state
        self.disp = {k: float(getattr(state, k)) for k in STATS}
        self.last = {k: getattr(state, k) for k in STATS}
        self.flash = {k: [0.0, GOOD] for k in STATS}
        self.pdisp = {k: float(v) for k, v in state.power.items()}
        self.plast = dict(state.power)
        self.pflash = {k: 0.0 for k in state.power}

    def anchor(self, key):
        if key in STATS:
            return STAT_X0 + STATS.index(key) * STAT_W + 75, HUD_H + 4
        if key == "power":
            return POWER_X0 + 100, HUD_H + 4
        return 130, HUD_H + 4

    def update(self, dt):
        st = self.state
        k_ = min(1.0, dt * 5)
        for k in STATS:
            v = getattr(st, k)
            if v != self.last[k]:
                self.flash[k] = [1.0, GOOD if v > self.last[k] else BAD]
                self.last[k] = v
            self.disp[k] += (v - self.disp[k]) * k_
            self.flash[k][0] = max(0.0, self.flash[k][0] - dt * 1.2)
        for k, v in st.power.items():
            if v != self.plast.get(k):
                self.pflash[k] = 1.0
                self.plast[k] = v
            self.pdisp[k] += (v - self.pdisp.get(k, 0)) * k_
            self.pflash[k] = max(0.0, self.pflash[k] - dt * 1.2)

    def draw(self, surf, chapter_title=""):
        st = self.state
        pygame.draw.rect(surf, (13, 17, 31), (0, 0, W, HUD_H))
        pygame.draw.line(surf, LINE, (0, HUD_H), (W, HUD_H), 2)
        text(surf, st.company, font(26, True), ACCENT, (16, 8))
        text(surf, fit(font(13), chapter_title, 232), font(13), MUTED, (16, 36))
        text(surf, f"Equipo: {len(st.team)}  ·  Nómina: {money(st.payroll())}", font(13), TEXT, (16, 52))
        style = LEADER_STYLES.get(st.leader_style, {}).get("name", "sin definir")
        text(surf, f"Estilo: {style}", font(13), ACCENT2, (16, 67))
        for i, k in enumerate(STATS):
            x0 = STAT_X0 + i * STAT_W
            fl, fcol = self.flash[k]
            text(surf, STAT_LABELS[k], font(14), MUTED, (x0 + 6, 14))
            v = self.disp[k]
            if k == "cash":
                label = ("-" if v < 0 else "") + money(abs(int(v)))
                frac = max(0.0, v) / max(100_000, st.cash)
            else:
                label = str(int(round(v)))
                frac = v / 100
            vcol = mix(BAD if k == "cash" and v < 0 else TEXT, fcol, fl)
            text(surf, label, font(17, True), vcol, (x0 + STAT_W - 6, 12), "topright")
            bar = pygame.Rect(x0 + 6, 42, STAT_W - 16, 14)
            pygame.draw.rect(surf, (30, 38, 62), bar, border_radius=7)
            w = int(bar.w * max(0.0, min(1.0, frac)))
            if w > 0:
                col = STAT_COLORS[k]
                if k != "cash" and v < 25:
                    col = BAD
                pygame.draw.rect(surf, col, (bar.x, bar.y, w, bar.h), border_radius=7)
            pygame.draw.rect(surf, mix(LINE, fcol, fl), bar, 1 + int(fl * 2), border_radius=7)
        # panel de poder
        for i, (k, name) in enumerate(POWER_TYPES.items()):
            y = 5 + i * 15
            fl = self.pflash.get(k, 0.0)
            text(surf, name, font(12), mix(MUTED, TEXT, fl), (POWER_X0, y))
            bar = pygame.Rect(POWER_X0 + 82, y + 3, 110, 8)
            pygame.draw.rect(surf, (30, 38, 62), bar, border_radius=4)
            v = self.pdisp.get(k, 0)
            if v > 0.5:
                pygame.draw.rect(surf, mix((130, 100, 230), ACCENT2, fl),
                                 (bar.x, bar.y, int(bar.w * min(1, v / 100)), bar.h), border_radius=4)
            text(surf, str(int(round(v))), font(12), TEXT, (POWER_X0 + 198, y))
