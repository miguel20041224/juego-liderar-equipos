"""Aplicación: bucle principal, máquina de pantallas con fade y flujo del juego."""

from __future__ import annotations

import importlib
import os
import random
import sys

import pygame

from ..engine import STAT_LABELS, GameState
from .background import Background
from .hud import HUD
from .scene_matrix import MatrixScreen
from .scene_story import StoryScreen
from .scene_team import AllocateScreen, HireScreen, LeaderScreen
from .screens import EndingScreen, LessonScreen, SummaryScreen, TitleScreen
from .theme import BAD, GOOD, H, TEXT, W, Button, FloatText, change_color, font, panel, text

SCENES = {"story": StoryScreen, "leader": LeaderScreen, "hire": HireScreen,
          "allocate": AllocateScreen, "matrix": MatrixScreen}


class App:
    def __init__(self, content, smoke=False, shots=None, seed=None):
        self.content = content
        self.smoke = smoke
        self.shots = shots
        self.rng = random.Random(seed)
        pygame.init()
        pygame.display.set_caption("Garage → Imperio")
        self.surf = pygame.display.set_mode((W, H), pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.bg = Background()
        self.state = GameState()
        self.hud = HUD(self.state)
        self.chapter = {"title": "", "concept": ""}
        self.floats: list[FloatText] = []
        self.fade = 255.0
        self.mode = "in"
        self.overlay = pygame.Surface((W, H))
        self.overlay.fill((0, 0, 0))
        self.confirm = False
        self.to_menu = False
        self.running = True
        self.scenes_played = 0
        self.last_ending = None
        self.shot_done: set = set()
        self.smoke_delay = 1.0 if shots else 0.0
        if shots:
            os.makedirs(shots, exist_ok=True)

    # ---- textos flotantes ----
    def float(self, s, color, key=None, delay=0.0):
        x, y = self.hud.anchor(key)
        self.floats.append(FloatText(s, color, x, y, delay))

    def float_changes(self, changes):
        n = 0
        for c in changes:
            key = next((k for k, lab in STAT_LABELS.items() if lab in c), None)
            if key is None and "Poder" in c:
                key = "power"
            self.float(c, change_color(c), key, delay=n * 0.3)
            n += 1

    # ---- flujo del juego ----
    def _flow(self):
        chapters = self.content.CHAPTERS
        while True:
            title = TitleScreen(self)
            yield title
            if title.result == "quit":
                return
            self.state = GameState()
            self.hud = HUD(self.state)
            self.to_menu = False
            self.floats.clear()
            for ci, ch in enumerate(chapters):
                self.chapter = ch
                yield LessonScreen(self, ch)
                for scene in ch["scenes"]:
                    if self.to_menu:
                        break
                    if not self.state.check(scene.get("requires")):
                        continue
                    cls = SCENES.get(scene.get("type"))
                    if cls is None:
                        print(f"[liderar] tipo de escena desconocido: {scene.get('type')!r}", file=sys.stderr)
                        continue
                    self.scenes_played += 1
                    yield cls(self, scene)
                if self.to_menu:
                    break
                notes = self.state.end_of_chapter()
                yield SummaryScreen(self, ch, notes, ci == len(chapters) - 1)
                if self.state.is_bankrupt():
                    break
            if self.to_menu:
                continue
            end = EndingScreen(self)
            self.last_ending = (end.eid, end.score)
            yield end
            if end.result == "quit":
                return

    def _advance(self):
        try:
            self.screen = next(self.flow)
        except StopIteration:
            self.running = False
            return
        self.mode = "in"

    # ---- bucle ----
    def run(self) -> int:
        self.flow = self._flow()
        self._advance()
        frames = 0
        while self.running:
            dt = 0.05 if self.smoke else min(self.clock.tick(60) / 1000, 0.05)
            for ev in pygame.event.get():
                self._event(ev)
            if not self.running:
                break
            if (self.smoke and self.mode == "idle" and not self.screen.finished and not self.confirm
                    and self.screen.age >= self.smoke_delay):
                self.screen.auto(self.rng)
            self._update(dt)
            if not self.running:
                break
            self._draw()
            pygame.display.flip()
            frames += 1
            if self.smoke and frames > 60000:
                raise RuntimeError("smoke: el juego no terminó (posible bloqueo)")
        pygame.quit()
        return 0

    def _event(self, ev):
        if ev.type == pygame.QUIT:
            self.running = False
        elif self.confirm:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_y, pygame.K_s):
                    self.confirm, self.to_menu, self.screen.finished = False, True, True
                elif ev.key in (pygame.K_ESCAPE, pygame.K_n):
                    self.confirm = False
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE and not self.screen.is_menu:
            self.confirm = True
        elif self.mode != "out" and not self.screen.finished:
            self.screen.handle(ev)

    def _update(self, dt):
        self.bg.update(dt)
        self.screen.update(dt)
        self.hud.update(dt)
        for f in self.floats:
            f.update(dt)
        self.floats = [f for f in self.floats if not f.dead]
        if self.mode == "in":
            self.fade -= dt * 700
            if self.fade <= 0:
                self.fade, self.mode = 0, "idle"
        elif self.mode == "out":
            self.fade += dt * 800
            if self.fade >= 255:
                self.fade = 255
                self._advance()
        elif self.screen.finished:
            self.mode = "out"

    def _draw(self):
        s, scr = self.surf, self.screen
        self.bg.draw(s, scr.is_menu)
        if scr.show_hud:
            self.hud.draw(s, self.chapter["title"])
        scr.draw(s)
        for f in self.floats:
            f.draw(s)
        if self.confirm:
            self.overlay.set_alpha(170)
            s.blit(self.overlay, (0, 0))
            panel(s, (390, 280, 500, 160), (22, 28, 46), BAD, 14, 2)
            text(s, "¿Volver al menú principal?", font(26, True), TEXT, (640, 305), "midtop")
            text(s, "Enter: sí  ·  Esc: seguir jugando", font(19), TEXT, (640, 360), "midtop")
        if self.fade > 0:
            self.overlay.set_alpha(int(self.fade))
            s.blit(self.overlay, (0, 0))
        if self.shots and self.mode == "idle":
            key = scr.shot_key()
            if key and key not in self.shot_done and scr.age > 0.5:
                self.shot_done.add(key)
                pygame.image.save(s, os.path.join(self.shots, f"{len(self.shot_done):02d}_{key}.png"))


def load_content(name="liderar.content"):
    return importlib.import_module(name)


def run(content_module=None, smoke=False, shots=None, seed=None) -> int:
    if smoke:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    content = content_module or load_content()
    app = App(content, smoke, shots, seed)
    code = app.run()
    if smoke:
        print(f"SMOKE OK: {app.scenes_played} escenas, final={app.last_ending}")
    return code
