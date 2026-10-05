"""Pantallas de flujo: título, lección, resumen de capítulo y final."""

from __future__ import annotations

import math

import pygame

from ..engine import LEADER_STYLES, POWER_TYPES, STAT_LABELS, compute_ending, money
from .hud import HUD_H
from .theme import (ACCENT, ACCENT2, BAD, GOLD, GOOD, H, LINE, MUTED, PANEL, TEXT, W, Button,
                    Screen, change_color, draw_lines, font, panel, text, wrap)

ENDING_COLORS = {"quiebra": BAD, "leyenda": GOLD, "exito": GOOD, "sobrevive": ACCENT,
                 "absorbida": ACCENT2}


def draw_title(surf, cx, y, size):
    f = font(size, True)
    a, b = f.render("Garage", True, TEXT), f.render("Imperio", True, ACCENT)
    gap = size
    x = cx - (a.get_width() + b.get_width() + gap * 1.6) / 2
    surf.blit(a, (x, y))
    ax = x + a.get_width() + gap * 0.3
    ay = y + a.get_height() // 2
    pygame.draw.line(surf, ACCENT2, (ax, ay), (ax + gap, ay), 6)
    pygame.draw.polygon(surf, ACCENT2, [(ax + gap + 14, ay), (ax + gap - 6, ay - 16), (ax + gap - 6, ay + 16)])
    surf.blit(b, (ax + gap * 1.3, y))


class TitleScreen(Screen):
    show_hud = False
    is_menu = True

    def __init__(self, app):
        super().__init__(app)
        self.result = None
        self.credits = False
        labels = ["Jugar", "Créditos", "Salir"]
        self.btns = [Button(490, 400 + i * 66, 300, t, str(i + 1), 24, primary=i == 0, min_h=52)
                     for i, t in enumerate(labels)]
        self.back = Button(490, 590, 300, "Volver", None, 22, center=True)
        self.back.tx = 18

    def act(self, i):
        if i == 0:
            self.result = "play"
            self.finished = True
        elif i == 1:
            self.credits = True
        else:
            self.result = "quit"
            self.finished = True

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.credits:
                if self.back.hit(ev.pos):
                    self.credits = False
                return
            for i, b in enumerate(self.btns):
                if b.hit(ev.pos):
                    self.act(i)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                if self.credits:
                    self.credits = False
                else:
                    self.act(2)
            elif self.credits:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.credits = False
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.act(0)
            elif pygame.K_1 <= ev.key <= pygame.K_3:
                self.act(ev.key - pygame.K_1)

    def draw(self, surf):
        draw_title(surf, W // 2, 150 + int(math.sin(self.age * 2) * 4), 78)
        text(surf, "De fundar Aple en un garaje a construir un imperio", font(24), MUTED, (W // 2, 262), "midtop")
        text(surf, "Liderazgo · Poder · Teoría de juegos", font(20), ACCENT, (W // 2, 298), "midtop")
        if self.credits:
            panel(surf, (340, 340, 600, 270), PANEL, LINE, 14)
            draw_lines(surf, ["Garage → Imperio".replace("→", "a"),
                              "Juego educativo de liderazgo de equipos.", "",
                              "Hecho con Python y pygame-ce.", "Todo el arte está dibujado por código.",
                              "", "Aple vs. Macrosoft: ¡que gane el mejor líder!"],
                       font(21), TEXT, 640, 358, 4, True)
            self.back.draw(surf)
        else:
            for b in self.btns:
                b.draw(surf)
        text(surf, "Esc: salir  ·  ratón o teclado", font(14), MUTED, (W // 2, H - 24), "midtop")

    def auto(self, rng):
        self.act(0)


class LessonScreen(Screen):
    def __init__(self, app, chapter):
        super().__init__(app)
        self.ch = chapter
        self.btn = Button(490, 560, 300, "Comenzar capítulo", None, 22, primary=True, center=True)
        self.btn.tx = 18

    def handle(self, ev):
        if (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.btn.hit(ev.pos)) or \
                (ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER)):
            self.finished = True

    def draw(self, surf):
        r = pygame.Rect(170, HUD_H + 30, 940, 480)
        panel(surf, r, PANEL, ACCENT, 18, 2)
        text(surf, self.ch["title"], font(32, True), TEXT, (640, r.y + 26), "midtop")
        pill = font(22, True).render("Concepto: " + self.ch["concept"], True, (12, 16, 28))
        pr = pill.get_rect(midtop=(640, r.y + 84)).inflate(36, 14)
        panel(surf, pr, ACCENT2, None, 20)
        surf.blit(pill, pill.get_rect(center=pr.center))
        draw_lines(surf, wrap(font(24), self.ch["lesson"], r.w - 100), font(24), TEXT, r.x + 50, r.y + 150, 6)
        self.btn.draw(surf)

    def auto(self, rng):
        self.finished = True


class SummaryScreen(Screen):
    def __init__(self, app, chapter, notes, last):
        super().__init__(app)
        self.ch, self.notes = chapter, notes
        self.bankrupt = self.state.is_bankrupt()
        label = "Ver final" if (last or self.bankrupt) else "Siguiente capítulo"
        self.btn = Button(490, 590, 300, label, None, 22, primary=True, center=True)
        self.btn.tx = 18
        app.float_changes([n.split(": ", 1)[-1] for n in notes if n[:1] in "+-" or ": -" in n])

    def handle(self, ev):
        if (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.btn.hit(ev.pos)) or \
                (ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER)):
            self.finished = True

    def draw(self, surf):
        r = pygame.Rect(240, HUD_H + 30, 800, 500)
        panel(surf, r, PANEL, BAD if self.bankrupt else LINE, 18, 2)
        text(surf, "Resumen del capítulo", font(30, True), TEXT, (640, r.y + 22), "midtop")
        text(surf, self.ch["title"], font(20), MUTED, (640, r.y + 62), "midtop")
        y = r.y + 110
        for n in self.notes or ["Sin novedades este capítulo."]:
            for ln in wrap(font(21), n, r.w - 80):
                text(surf, "• " + ln, font(21), TEXT, (r.x + 40, y))
                y += 28
        y = max(y + 14, r.y + 300)
        if self.bankrupt:
            text(surf, "¡Te quedaste sin dinero! Aple quiebra.", font(26, True), BAD, (640, y), "midtop")
        else:
            st = self.state
            text(surf, f"Dinero {money(st.cash)}  ·  Moral {st.morale}  ·  Reputación {st.reputation}",
                 font(20), MUTED, (640, y), "midtop")
            text(surf, f"Producto {st.progress}  ·  Innovación {st.innovation}", font(20), MUTED,
                 (640, y + 30), "midtop")
        self.btn.draw(surf)

    def auto(self, rng):
        self.finished = True


class EndingScreen(Screen):
    show_hud = False

    def __init__(self, app):
        super().__init__(app)
        st = self.state
        self.eid, self.title, self.body = compute_ending(st)
        self.score = st.score()
        self.scroll = 0
        self.result = None
        self.btns = [Button(40, 640, 280, "Volver a jugar", "1", 21, primary=True),
                     Button(340, 640, 200, "Salir", "2", 21)]
        f = font(17)
        self.rows = []
        for concept, t in st.log:
            self.rows.append((concept, wrap(f, t, 540)))
        self.content_h = sum(24 + len(ls) * 22 + 8 for _, ls in self.rows)

    def end(self, res):
        self.result = res
        self.finished = True

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for i, b in enumerate(self.btns):
                if b.hit(ev.pos):
                    self.end("again" if i == 0 else "quit")
        elif ev.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, min(max(0, self.content_h - 440), self.scroll - ev.y * 40))
        elif ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_1, pygame.K_RETURN, pygame.K_KP_ENTER):
                self.end("again")
            elif ev.key == pygame.K_2:
                self.end("quit")
            elif ev.key == pygame.K_DOWN:
                self.scroll = min(max(0, self.content_h - 440), self.scroll + 40)
            elif ev.key == pygame.K_UP:
                self.scroll = max(0, self.scroll - 40)

    def draw(self, surf):
        st = self.state
        col = ENDING_COLORS.get(self.eid, ACCENT)
        left = pygame.Rect(30, 24, 600, 600)
        panel(surf, left, PANEL, col, 16, 2)
        text(surf, "FINAL", font(16, True), MUTED, (54, 44))
        text(surf, self.title, font(44, True), col, (54, 66))
        y = draw_lines(surf, wrap(font(21), self.body, 540), font(21), TEXT, 54, 130, 4) + 16
        shown = int(self.score * min(1.0, self.age / 1.5))
        text(surf, f"Puntaje: {shown}", font(36, True), GOLD, (54, y))
        y += 56
        style = LEADER_STYLES.get(st.leader_style, {}).get("name", "Sin definir")
        text(surf, f"Estilo de liderazgo: {style}", font(21), TEXT, (54, y))
        dom = st.dominant_power()
        text(surf, f"Poder dominante: {POWER_TYPES[dom]} ({st.power[dom]})", font(21), TEXT, (54, y + 32))
        text(surf, f"Equipo: {len(st.team)}  ·  Caja final: {money(st.cash)}", font(19), MUTED, (54, y + 70))
        text(surf, f"Moral {st.morale} · Reputación {st.reputation} · Producto {st.progress} · "
                   f"Innovación {st.innovation}", font(16), MUTED, (54, y + 100))
        right = pygame.Rect(650, 24, 600, 600)
        panel(surf, right, PANEL, LINE, 16)
        text(surf, "Decisiones y conceptos", font(24, True), ACCENT, (672, 38))
        clip = pygame.Rect(662, 80, 576, 530)
        old = surf.get_clip()
        surf.set_clip(clip)
        yy = 84 - self.scroll
        for concept, ls in self.rows:
            text(surf, concept, font(16, True), ACCENT2, (672, yy))
            yy += 24
            for ln in ls:
                text(surf, ln, font(17), TEXT, (684, yy))
                yy += 22
            yy += 8
        surf.set_clip(old)
        for b in self.btns:
            b.draw(surf)

    def auto(self, rng):
        self.end("quit")
