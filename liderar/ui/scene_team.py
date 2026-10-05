"""Escenas leader, hire y allocate."""

from __future__ import annotations

import math

import pygame

from ..engine import LEADER_STYLES, POWER_TYPES, STAT_LABELS, Employee, money
from .theme import (ACCENT, ACCENT2, BAD, GOLD, GOOD, LINE, MUTED, PANEL, PANEL2, TEXT, Button,
                    Screen, draw_lines, fmt_effects, font, header, panel, star, text, wrap)


def _digit(ev):
    if pygame.K_1 <= ev.key <= pygame.K_9:
        return ev.key - pygame.K_1
    if pygame.K_KP_1 <= ev.key <= pygame.K_KP_9:
        return ev.key - pygame.K_KP_1
    return None


class LeaderScreen(Screen):
    def __init__(self, app, scene):
        super().__init__(app)
        self.scene = scene
        self.keys = list(LEADER_STYLES)
        self.sel = None
        self.cards = [pygame.Rect(32 + i * 246, 0, 232, 0) for i in range(5)]
        self.btn = Button(490, 648, 300, "Confirmar estilo", None, 22, primary=True, center=True)
        self.btn.tx = 18
        self.btn.enabled = False

    def choose(self, i):
        self.sel = i
        self.btn.enabled = True

    def confirm(self):
        if self.sel is None:
            return
        before = dict(self.state.power)
        self.state.set_style(self.keys[self.sel])
        for k, v in self.state.power.items():
            if v != before[k]:
                self.app.float(f"+{v - before[k]} Poder {POWER_TYPES[k]}", GOOD, "power")
        self.finished = True

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.btn.hit(ev.pos):
                self.confirm()
                return
            for i, r in enumerate(self.cards):
                if r.collidepoint(ev.pos):
                    if self.sel == i:
                        self.confirm()
                    else:
                        self.choose(i)
        elif ev.type == pygame.KEYDOWN:
            n = _digit(ev)
            if n is not None and n < 5:
                self.choose(n)
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.confirm()

    def draw(self, surf):
        hb = header(surf, self.scene.get("text", "Elige tu estilo de liderazgo."))
        top = hb + 14
        for i, k in enumerate(self.keys):
            st = LEADER_STYLES[k]
            r = self.cards[i]
            r.y, r.h = top, 640 - top
            hov = r.collidepoint(pygame.mouse.get_pos())
            sel = self.sel == i
            panel(surf, r, PANEL2 if (sel or hov) else PANEL, ACCENT if sel else LINE, 14, 3 if sel else 1)
            pygame.draw.circle(surf, ACCENT, (r.x + 24, r.y + 26), 14)
            text(surf, str(i + 1), font(19, True), (10, 14, 24), (r.x + 24, r.y + 26), "center")
            size = 23
            while size > 16 and font(size, True).size(st["name"])[0] > r.w - 56:
                size -= 1
            text(surf, st["name"], font(size, True), TEXT, (r.x + 46, r.y + 14 + (23 - size) // 2))
            y = draw_lines(surf, wrap(font(17), st["desc"], r.w - 28), font(17), MUTED, r.x + 14, r.y + 56)
            y += 8
            for stat, m in st["mods"].items():
                good = (m > 1) != (stat == "cash")
                lab = "Gastos" if stat == "cash" else STAT_LABELS[stat]
                text(surf, f"{lab} ×{m}", font(17, True), GOOD if good else BAD, (r.x + 14, y))
                y += 24
            y += 8
            for kind, v in st["power"].items():
                text(surf, f"+{v} Poder {POWER_TYPES[kind]}", font(16), ACCENT2, (r.x + 14, y))
                y += 22
        self.btn.draw(surf)

    def auto(self, rng):
        self.choose(rng.randrange(5))
        self.confirm()


class HireScreen(Screen):
    def __init__(self, app, scene):
        super().__init__(app)
        self.scene = scene
        self.cands = scene.get("candidates", [])
        self.max = scene.get("max_hires", 1)
        self.sel = []
        self.msg = ""
        self.msg_t = 0.0
        self.rects = []
        self.btn = Button(940, 650, 300, "Confirmar contratación", None, 20, primary=True, center=True)
        self.btn.tx = 18

    def cost(self):
        return sum(self.cands[i]["salary"] for i in self.sel)

    def toggle(self, i):
        if i >= len(self.cands):
            return
        if i in self.sel:
            self.sel.remove(i)
        elif len(self.sel) >= self.max:
            self.say(f"Máximo {self.max} contrataciones")
        elif self.state.cash - self.cost() - self.cands[i]["salary"] < 0:
            self.say("Presupuesto insuficiente")
        else:
            self.sel.append(i)

    def say(self, m):
        self.msg, self.msg_t = m, 2.0

    def confirm(self):
        for i in self.sel:
            c = self.cands[i]
            self.state.hire(Employee(c["name"], c["role"], c["skill"], c["salary"], c.get("trait", "")))
            self.state.log.append(("Contratación", f"{c['name']} ({c['role']})"))
            self.app.float(f"-{money(c['salary'])} {c['name']}", BAD, "cash")
        self.finished = True

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.btn.hit(ev.pos):
                self.confirm()
                return
            for i, r in enumerate(self.rects):
                if r.collidepoint(ev.pos):
                    self.toggle(i)
        elif ev.type == pygame.KEYDOWN:
            n = _digit(ev)
            if n is not None:
                self.toggle(n)
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.confirm()

    def update(self, dt):
        super().update(dt)
        self.msg_t -= dt

    def draw(self, surf):
        hb = header(surf, self.scene.get("text", "Contrata a tu equipo."))
        n = len(self.cands)
        cols = 4
        rows = max(1, math.ceil(n / cols))
        ch = int(min(190, (610 - hb - 14 - (rows - 1) * 12) / rows))
        self.rects = []
        smax = max([c["skill"] for c in self.cands] + [1])
        for i, c in enumerate(self.cands):
            r = pygame.Rect(40 + (i % cols) * 304, hb + 14 + (i // cols) * (ch + 12), 288, ch)
            self.rects.append(r)
            sel = i in self.sel
            afford = sel or self.state.cash - self.cost() - c["salary"] >= 0
            hov = r.collidepoint(pygame.mouse.get_pos())
            panel(surf, r, PANEL2 if (sel or hov) else PANEL, GOOD if sel else LINE, 12, 3 if sel else 1)
            text(surf, f"{i + 1}", font(15, True), MUTED, (r.x + 10, r.y + 8))
            text(surf, c["name"], font(21, True), TEXT, (r.x + 30, r.y + 8))
            text(surf, c["role"], font(16), ACCENT, (r.x + 14, r.y + 38))
            stars = c["skill"] if smax <= 5 else -(-c["skill"] // 2)
            for s in range(5):
                star(surf, r.x + 26 + s * 24, r.y + 74, 10, GOLD if s < stars else (55, 62, 90))
            text(surf, f"Nivel {c['skill']}", font(14), MUTED, (r.x + 150, r.y + 66))
            text(surf, "Salario " + money(c["salary"]), font(17, True), GOLD if afford else BAD,
                 (r.x + 14, r.y + 94))
            draw_lines(surf, wrap(font(15), c.get("trait", ""), r.w - 28)[:3], font(15), MUTED,
                       r.x + 14, r.y + 120, 1)
            if sel:
                text(surf, "✔", font(22, True), GOOD, (r.right - 14, r.y + 6), "topright")
        info = (f"Contratados {len(self.sel)}/{self.max}  ·  Salarios {money(self.cost())}"
                f"  ·  Caja tras contratar {money(self.state.cash - self.cost())}")
        text(surf, info, font(19), TEXT, (40, 654))
        if self.msg_t > 0:
            text(surf, self.msg, font(19, True), BAD, (40, 682))
        self.btn.draw(surf)

    def auto(self, rng):
        for i in rng.sample(range(len(self.cands)), len(self.cands)):
            if rng.random() < 0.6:
                self.toggle(i)
        self.confirm()


class AllocateScreen(Screen):
    def __init__(self, app, scene):
        super().__init__(app)
        self.scene = scene
        self.slots = scene["slots"]
        self.total = scene.get("points", 5)
        self.vals = [0] * len(self.slots)
        self.cur = 0
        self.minus, self.plus = [], []
        self.btn = Button(490, 650, 300, "Confirmar reparto", None, 22, primary=True, center=True)
        self.btn.tx = 18

    def left(self):
        return self.total - sum(self.vals)

    def adj(self, i, d):
        if d > 0 and self.left() <= 0:
            return
        if d < 0 and self.vals[i] <= 0:
            return
        self.vals[i] += d

    def confirm(self):
        if self.left() != 0:
            return
        parts = []
        for s, n in zip(self.slots, self.vals):
            if n:
                self.app.float_changes(self.state.apply({k: v * n for k, v in s["effects_per_point"].items()}))
                parts.append(f"{s['label']} {n}")
        self.state.log.append(("Asignación de recursos", ", ".join(parts)))
        self.finished = True

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.btn.hit(ev.pos):
                self.confirm()
            for i in range(len(self.slots)):
                if self.minus[i:i + 1] and self.minus[i].collidepoint(ev.pos):
                    self.adj(i, -1)
                if self.plus[i:i + 1] and self.plus[i].collidepoint(ev.pos):
                    self.adj(i, 1)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_UP:
                self.cur = (self.cur - 1) % len(self.slots)
            elif ev.key == pygame.K_DOWN:
                self.cur = (self.cur + 1) % len(self.slots)
            elif ev.key in (pygame.K_RIGHT, pygame.K_PLUS, pygame.K_KP_PLUS):
                self.adj(self.cur, 1)
            elif ev.key in (pygame.K_LEFT, pygame.K_MINUS, pygame.K_KP_MINUS):
                self.adj(self.cur, -1)
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.confirm()

    def draw(self, surf):
        hb = header(surf, self.scene.get("text", "Reparte tus puntos."))
        text(surf, f"Puntos por repartir: {self.left()}", font(26, True),
             ACCENT2 if self.left() else GOOD, (640, hb + 14), "midtop")
        n = len(self.slots)
        rh = min(84, int((560 - hb - 50) / n) - 8)
        self.minus, self.plus = [], []
        totals: dict = {}
        for i, s in enumerate(self.slots):
            r = pygame.Rect(120, hb + 56 + i * (rh + 8), 1040, rh)
            panel(surf, r, PANEL2 if i == self.cur else PANEL, ACCENT if i == self.cur else LINE, 12)
            text(surf, s["label"], font(24, True), TEXT, (r.x + 18, r.y + 8))
            text(surf, " · ".join(fmt_effects(s["effects_per_point"])) + " por punto", font(16), MUTED,
                 (r.x + 18, r.y + 12 + 26 if rh > 60 else r.y + 36))
            m = pygame.Rect(r.x + 470, r.centery - 18, 36, 36)
            p = pygame.Rect(r.right - 70, r.centery - 18, 36, 36)
            self.minus.append(m)
            self.plus.append(p)
            for rect, lab, on in ((m, "−", self.vals[i] > 0), (p, "+", self.left() > 0)):
                panel(surf, rect, (46, 58, 96) if on else (26, 30, 44),
                      ACCENT if on and rect.collidepoint(pygame.mouse.get_pos()) else LINE, 8)
                text(surf, lab, font(26, True), TEXT if on else (90, 98, 120), rect.center, "center")
            for k in range(self.total):
                px = m.right + 12 + k * ((p.x - m.right - 24) // max(1, self.total))
                pygame.draw.rect(surf, ACCENT if k < self.vals[i] else (44, 54, 84),
                                 (px, r.centery - 12, max(8, (p.x - m.right - 24) // max(1, self.total) - 6), 24),
                                 border_radius=5)
            for key, v in s["effects_per_point"].items():
                totals[key] = totals.get(key, 0) + v * self.vals[i]
        eff = fmt_effects({k: v for k, v in totals.items() if v})
        text(surf, "Efecto estimado: " + (", ".join(eff) or "—"), font(18), MUTED, (640, 622), "midtop")
        self.btn.enabled = self.left() == 0
        self.btn.draw(surf)

    def auto(self, rng):
        while self.left() > 0:
            self.adj(rng.randrange(len(self.slots)), 1)
        self.confirm()
