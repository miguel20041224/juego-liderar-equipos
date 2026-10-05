"""Escena matrix: juego simultáneo 2x2 contra el rival con revelación animada."""

from __future__ import annotations

import math

import pygame

from ..engine import nash_equilibria, play_round
from .theme import (ACCENT, ACCENT2, BAD, GOLD, GOOD, LINE, MUTED, PANEL, PANEL2, TEXT, Button,
                    Screen, Typewriter, draw_lines, fit, font, header, panel, text, wrap)

GX, CW, CH = 470, 230, 112
REVEAL = 1.6


class MatrixScreen(Screen):
    def __init__(self, app, scene):
        super().__init__(app)
        self.sc = scene
        self.opts = scene["options"]
        self.pay = scene["payoffs"]
        self.rival = scene.get("rival", "Rival")
        self.rounds = scene.get("rounds", 3)
        self.eq = nash_equilibria(self.pay)
        self.round = 0
        self.my_last = None
        self.tot = [0, 0]
        self.hist = []
        self.phase = "choose"
        self.timer = 0.0
        self.my = self.their = None
        self.res = None
        self.tw = None
        self.oy = 0
        self.btns = [Button(0, 0, 380, o, str(i + 1), 20) for i, o in enumerate(self.opts)]
        self.next_btn = Button(960, 654, 280, "Siguiente ronda", None, 20, primary=True, center=True)
        self.next_btn.tx = 18

    # ---- acciones ----
    def pick(self, i):
        if self.phase == "choose":
            self.my, self.phase, self.timer = i, "reveal", 0.0

    def _resolve(self):
        self.res = play_round(self.state, self.sc, self.my, self.my_last, self.app.rng)
        self.their = self.res["rival_move"]
        self.tot[0] += self.res["my_points"]
        self.tot[1] += self.res["rival_points"]
        self.hist.append((self.my, self.their, self.res["my_points"], self.res["rival_points"]))
        self.app.float_changes(self.res["changes"])
        self.phase = "result"
        self.next_btn.label = "Siguiente ronda" if self.round + 1 < self.rounds else "Ver resultado"
        self.next_btn.lines = [self.next_btn.label]

    def _next(self):
        self.my_last = self.my
        self.round += 1
        if self.round >= self.rounds:
            self.phase = "final"
            eqs = ", ".join(f"({self.opts[a]} / {self.opts[b]})" for a, b in self.eq)
            self.state.log.append(("Teoría de juegos: equilibrio de Nash",
                                   f"vs {self.rival}: {self.tot[0]}-{self.tot[1]} puntos"))
            self.tw = Typewriter(self.sc.get("explain", ""), font(19), 920, 90)
            self.eq_text = ("Equilibrio de Nash: " + eqs) if self.eq else \
                "No hay equilibrio de Nash en estrategias puras."
            self.next_btn.label = "Continuar"
            self.next_btn.lines = ["Continuar"]
        else:
            self.phase, self.my, self.their = "choose", None, None

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.phase == "choose":
                for i, b in enumerate(self.btns):
                    if b.hit(ev.pos):
                        self.pick(i)
            elif self.phase == "result" and self.next_btn.hit(ev.pos):
                self._next()
            elif self.phase == "final":
                if self.tw and not self.tw.done:
                    self.tw.complete()
                elif self.next_btn.hit(ev.pos):
                    self.finished = True
        elif ev.type == pygame.KEYDOWN:
            if self.phase == "choose" and pygame.K_1 <= ev.key <= pygame.K_2:
                self.pick(ev.key - pygame.K_1)
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                if self.phase == "result":
                    self._next()
                elif self.phase == "final":
                    if not self.tw.done:
                        self.tw.complete()
                    else:
                        self.finished = True

    def update(self, dt):
        super().update(dt)
        self.timer += dt
        if self.phase == "reveal" and self.timer >= REVEAL:
            self._resolve()
        if self.tw:
            self.tw.update(dt)

    def shot_key(self):
        if self.phase == "reveal":
            return None
        return "matrix_" + self.phase

    # ---- dibujo ----
    def cell_rect(self, a, b):
        return pygame.Rect(GX + b * CW, self.oy + 62 + a * CH, CW - 6, CH - 6)

    def draw(self, surf):
        hb = header(surf, self.sc.get("text", ""), size=18)
        self.oy = oy = max(hb + 8, 140)
        pulse = 0.5 + 0.5 * math.sin(self.age * 6)
        # etiquetas
        text(surf, f"{self.rival} (rival)", font(18, True), ACCENT2, (GX + CW, oy), "midtop")
        text(surf, "TÚ", font(18, True), ACCENT, (GX - 20, oy + 28), "topright")
        for j, o in enumerate(self.opts):
            draw_lines(surf, wrap(font(17), o, CW - 20)[:2], font(17), TEXT, GX + j * CW + CW // 2 - 3,
                       oy + 26, 0, True)
        hover = None
        if self.phase == "choose":
            hover = next((i for i, b in enumerate(self.btns) if b.is_hover()), None)
        for i, o in enumerate(self.opts):
            lines = wrap(font(17), o, 250)[:3]
            ly = self.cell_rect(i, 0).centery - len(lines) * 11
            draw_lines(surf, lines, font(17), TEXT, GX - 20 - 0, ly, 0) if False else None
            for k, ln in enumerate(lines):
                text(surf, ln, font(17), TEXT, (GX - 20, ly + k * 22), "topright")
        # reveal: columna parpadeante
        flick = None
        if self.phase == "reveal":
            flick = int(self.timer * 9) % 2 if self.timer < REVEAL - 0.3 else None
        for a in range(2):
            for b in range(2):
                r = self.cell_rect(a, b)
                fill, border, bw = PANEL, LINE, 1
                if self.phase == "choose" and hover == a:
                    fill, border, bw = PANEL2, ACCENT, 2
                if self.phase == "reveal":
                    if a == self.my:
                        fill, border, bw = PANEL2, ACCENT, 2
                    if flick == b:
                        fill, border, bw = (46, 40, 30), ACCENT2, 2
                if self.phase in ("result",) and (a, b) == (self.my, self.their):
                    fill, border, bw = (50, 46, 24), GOLD, 3 + int(pulse * 2)
                if self.phase == "final":
                    if (a, b) in self.eq:
                        fill, border, bw = (20, 52, 40), GOOD, 3
                    if (a, b) == (self.my, self.their):
                        border, bw = GOLD, 3
                panel(surf, r, fill, border, 12, bw)
                y, rv = self.pay[a][b]
                text(surf, str(y), font(44, True), ACCENT, (r.centerx - 22, r.centery - 6), "midright")
                text(surf, ",", font(36, True), MUTED, (r.centerx, r.centery - 6), "center")
                text(surf, str(rv), font(44, True), ACCENT2, (r.centerx + 22, r.centery - 6), "midleft")
                text(surf, "tú", font(13), ACCENT, (r.centerx - 22, r.bottom - 16), "midright")
                text(surf, "rival", font(13), ACCENT2, (r.centerx + 22, r.bottom - 16), "midleft")
                if self.phase == "final" and (a, b) in self.eq:
                    text(surf, "NASH", font(15, True), GOOD, (r.right - 8, r.y + 6), "topright")
        # panel de marcador
        sp = pygame.Rect(960, oy, 280, 300)
        panel(surf, sp, PANEL, LINE, 12)
        shown = min(self.round + (1 if self.phase in ("choose", "reveal", "result") else 0), self.rounds)
        text(surf, f"Ronda {shown}/{self.rounds}", font(22, True), TEXT, (sp.x + 16, sp.y + 10))
        text(surf, f"Tú: {self.tot[0]}", font(20, True), ACCENT, (sp.x + 16, sp.y + 44))
        text(surf, f"{self.rival}: {self.tot[1]}", font(20, True), ACCENT2, (sp.x + 140, sp.y + 44))
        for k, (m, t_, a, b) in enumerate(self.hist[-7:]):
            s = f"R{len(self.hist) - len(self.hist[-7:]) + k + 1}: {self.opts[m]} vs {self.opts[t_]}  {a}-{b}"
            text(surf, fit(font(14), s, 250), font(14), MUTED, (sp.x + 16, sp.y + 84 + k * 28))
        base = oy + 62 + 2 * CH + 6
        # estado por fase
        if self.phase == "choose":
            text(surf, "Tu decisión (1-2 o clic):", font(18), MUTED, (60, base))
            for i, b in enumerate(self.btns):
                b.rect.topleft = (60 + i * 400, base + 28)
                b.draw(surf)
        elif self.phase == "reveal":
            dots = "." * (int(self.timer * 4) % 4)
            text(surf, f"{self.rival} está decidiendo{dots}", font(24, True), ACCENT2, (640, base + 20), "midtop")
        elif self.phase == "result":
            text(surf, f"{self.rival} eligió: {self.opts[self.their]}", font(22, True), ACCENT2, (60, base + 6))
            text(surf, f"Ganas {self.res['my_points']} pts, el rival {self.res['rival_points']}",
                 font(20), TEXT, (60, base + 40))
            self.next_btn.draw(surf)
        elif self.phase == "final":
            diff = self.tot[0] - self.tot[1]
            msg, col = (("Terminaste por delante", GOOD) if diff > 0 else
                        ("Terminaste por detrás", BAD) if diff < 0 else ("Empate", GOLD))
            text(surf, f"{msg}: {self.tot[0]} a {self.tot[1]}", font(22, True), col, (60, base + 4))
            text(surf, self.eq_text, font(19, True), GOOD, (60, base + 36))
            self.tw.draw(surf, 60, base + 66, TEXT)
            if self.tw.done:
                self.next_btn.draw(surf)

    def auto(self, rng):
        if self.phase == "choose":
            self.pick(rng.randrange(2))
        elif self.phase == "result":
            self._next()
        elif self.phase == "final":
            if self.tw and not self.tw.done:
                self.tw.complete()
            self.finished = True
