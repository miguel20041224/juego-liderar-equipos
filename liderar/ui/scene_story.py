"""Escena story: retrato, texto con máquina de escribir y decisiones (1-5 opciones)."""

from __future__ import annotations

import pygame

from .hud import HUD_H
from .portraits import draw_portrait
from .theme import (ACCENT, ACCENT2, MUTED, PANEL, LINE, TEXT, Button, Screen, Typewriter,
                    change_color, draw_lines, font, fmt_effects, panel, text, wrap)

TX, TW = 400, 840


class StoryScreen(Screen):
    def __init__(self, app, scene):
        super().__init__(app)
        self.scene = scene
        self.char = app.content.CHARACTERS.get(scene.get("portrait"))
        self.speaker = scene.get("speaker") or (self.char or {}).get("name", "Narrador")
        self.role = (self.char or {}).get("role", "")
        self.choices = [c for c in scene.get("choices", []) if self.state.check(c.get("requires"))]
        self.phase = "ask"
        self.chosen = None
        self.changes = []
        self.tw = Typewriter(scene.get("text", ""), font(22), TW - 36)
        self.buttons = []
        self._layout()

    def _layout(self):
        """Posiciona botones debajo del texto; reduce tamaño si no caben (hasta 5 opciones)."""
        y0 = HUD_H + 16 + self.tw.height + 28 + 12
        labels = [(c["text"], str(i + 1)) for i, c in enumerate(self.choices)] or [("Continuar", None)]
        for size, gap in ((20, 8), (18, 6), (16, 5)):
            self.buttons = [Button(TX, 0, TW, t, k, size, min_h=38 if size < 20 else 44,
                                   primary=not self.choices) for t, k in labels]
            total = sum(b.rect.h for b in self.buttons) + gap * (len(self.buttons) - 1)
            if y0 + total <= 706:
                break
        y = y0
        for b in self.buttons:
            b.rect.y = y
            y += b.rect.h + gap

    def pick(self, i):
        if self.phase != "ask":
            return
        if not self.choices:
            self.finished = True
            return
        c = self.choices[i]
        self.chosen = c
        self.changes = self.state.apply(c.get("effects", {}))
        self.state.log.append((c.get("concept") or self.app.chapter["title"], c["text"]))
        self.app.float_changes(self.changes)
        self.phase = "feedback"
        self.tw = Typewriter(c.get("feedback") or "Decisión tomada.", font(22), TW - 36)
        self.buttons = [Button(TX, HUD_H + 16 + 50 + self.tw.height + 120, 260, "Continuar", "↵",
                               primary=True, center=True)]
        self.buttons[0].key = None
        self.buttons[0].tx = 18

    def _advance(self):
        if not self.tw.done:
            self.tw.complete()
        elif self.phase == "feedback":
            self.finished = True
        elif not self.choices:
            self.finished = True

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if not self.tw.done:
                self.tw.complete()
                return
            for i, b in enumerate(self.buttons):
                if b.hit(ev.pos):
                    if self.phase == "feedback" or not self.choices:
                        self.finished = True
                    else:
                        self.pick(i)
                    return
            if self.phase == "feedback":
                pass
        elif ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                self._advance()
            elif self.phase == "ask" and self.tw.done and self.choices:
                n = ev.key - pygame.K_1
                if ev.key >= pygame.K_KP_1 and ev.key <= pygame.K_KP_9:
                    n = ev.key - pygame.K_KP_1
                if 0 <= n < len(self.choices):
                    self.pick(n)

    def update(self, dt):
        super().update(dt)
        self.tw.update(dt)

    def shot_key(self):
        return f"story_{self.phase}" if self.tw.done else None

    def draw(self, surf):
        talking = not self.tw.done
        draw_portrait(surf, pygame.Rect(40, HUD_H + 16, 330, 470), self.char, self.age, talking)
        text(surf, self.speaker, font(26, True), TEXT, (205, HUD_H + 16 + 490), "midtop")
        if self.role:
            text(surf, self.role, font(16), MUTED, (205, HUD_H + 16 + 524), "midtop")
        top = HUD_H + 16
        if self.phase == "ask":
            box = pygame.Rect(TX, top, TW, self.tw.height + 28)
            panel(surf, box, PANEL, LINE, 12)
            self.tw.draw(surf, TX + 18, top + 14)
        else:
            quote = wrap(font(17), "Elegiste: " + self.chosen["text"], TW - 36)[:2]
            qh = len(quote) * (font(17).get_linesize() + 2)
            box = pygame.Rect(TX, top, TW, qh + self.tw.height + 56)
            panel(surf, box, PANEL, ACCENT, 12)
            draw_lines(surf, quote, font(17), MUTED, TX + 18, top + 10, 2)
            self.tw.draw(surf, TX + 18, top + qh + 24, TEXT)
            y = box.bottom + 12
            if self.chosen.get("concept"):
                text(surf, "Concepto: " + self.chosen["concept"], font(19, True), ACCENT2, (TX, y))
                y += 30
            x = TX
            for ch in self.changes:
                img = font(18, True).render(ch, True, change_color(ch))
                if x + img.get_width() + 20 > TX + TW:
                    x, y = TX, y + 32
                chip = pygame.Rect(x, y, img.get_width() + 20, 28)
                panel(surf, chip, (26, 34, 58), change_color(ch), 14)
                surf.blit(img, (x + 10, y + 3))
                x += chip.w + 8
            self.buttons[0].rect.y = max(y + 50, box.bottom + 90)
        if self.tw.done:
            for b in self.buttons:
                b.draw(surf)
        else:
            text(surf, "clic / Espacio para completar", font(14), MUTED, (TX + TW, box.bottom + 6), "topright")

    def auto(self, rng):
        if not self.tw.done:
            self.tw.complete()
        elif self.phase == "feedback" or not self.choices:
            self.finished = True
        else:
            self.pick(rng.randrange(len(self.choices)))
