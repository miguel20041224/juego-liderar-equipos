"""Motor del juego: estado, efectos, condiciones, IA rival y finales.

No depende de pygame, así se puede probar sin ventana.

CONTRATO DE CONTENIDO (lo usa liderar/content.py)
================================================
CHAPTERS es una lista de capítulos:

    {
        "id": "garaje",
        "title": "Capítulo 1 · El garaje",
        "concept": "Estilos de liderazgo",          # concepto académico del capítulo
        "lesson": "Texto corto que explica el concepto (se muestra al iniciar).",
        "scenes": [ <escena>, ... ],
    }

Tipos de escena (clave "type"):

  "story"  -> narrativa con decisiones
      {"type": "story", "speaker": "Steve Wozniac", "portrait": "woz",
       "text": "...",
       "choices": [
           {"text": "Opción", "effects": {...}, "feedback": "Consecuencia",
            "concept": "Poder experto",          # opcional: etiqueta que se muestra
            "requires": {...}},                  # opcional: condición para mostrarla
       ],
       "requires": {...}}                         # opcional: la escena se salta si no se cumple

  "leader" -> el jugador elige su estilo de liderazgo (ver LEADER_STYLES)
      {"type": "leader", "text": "..."}

  "hire"   -> contratación con presupuesto
      {"type": "hire", "text": "...", "max_hires": 3,
       "candidates": [{"name", "role", "skill", "salary", "trait"}, ...]}

  "allocate" -> repartir puntos entre opciones (p. ej. triángulo alcance/tiempo/costo)
      {"type": "allocate", "text": "...", "points": 6,
       "slots": [{"key": "alcance", "label": "Alcance", "effects_per_point": {...}}, ...]}

  "matrix" -> juego simultáneo contra el rival (teoría de juegos)
      {"type": "matrix", "text": "...", "rival": "Macrosoft", "rounds": 3,
       "ai": "tit_for_tat" | "greedy" | "random" | "grim",
       "options": ["Mantener precio", "Bajar precio"],   # índice 0 = cooperar, 1 = competir
       "payoffs": [[[3, 3], [0, 5]],                     # payoffs[mi][rival] = [yo, rival]
                   [[5, 0], [1, 1]]],
       "effects_per_point": {"cash": 4000, "reputation": 1},
       "explain": "Texto que explica el equilibrio de Nash al terminar."}

Efectos ("effects"): dict con claves de stats (cash, morale, reputation,
progress, innovation), "power.<tipo>" para poder, "rival.<stat>" para el
rival, "flag": "nombre" o "flags": [...] para marcar decisiones, "unflag".

Condiciones ("requires"): {"min": {"cash": 10000}, "max": {...},
"flag": "x", "not_flag": "y", "style": "democratico"}.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

STATS = ("cash", "morale", "reputation", "progress", "innovation")
# Stats acotadas a 0..100 (cash no tiene tope).
BOUNDED = ("morale", "reputation", "progress", "innovation")

STAT_LABELS = {
    "cash": "Dinero",
    "morale": "Moral",
    "reputation": "Reputación",
    "progress": "Producto",
    "innovation": "Innovación",
}

# Bases del poder de French y Raven.
POWER_TYPES = {
    "legitimo": "Legítimo",
    "recompensa": "Recompensa",
    "coercitivo": "Coercitivo",
    "experto": "Experto",
    "referente": "Referente",
}

LEADER_STYLES = {
    "autocratico": {
        "name": "Autocrático",
        "desc": "Decides tú solo y rápido. Mucha productividad, poca moral.",
        "mods": {"morale": 0.6, "progress": 1.3, "innovation": 0.8},
        "power": {"legitimo": 15, "coercitivo": 15},
    },
    "democratico": {
        "name": "Democrático",
        "desc": "El equipo vota. Moral alta y buenas ideas, pero decisiones lentas.",
        "mods": {"morale": 1.4, "progress": 0.85, "innovation": 1.2},
        "power": {"referente": 15, "experto": 5},
    },
    "laissez_faire": {
        "name": "Laissez-faire",
        "desc": "Dejas hacer. Funciona con expertos y se vuelve un caos con novatos.",
        "mods": {"morale": 1.1, "progress": 0.9, "innovation": 1.4},
        "power": {"experto": 10},
    },
    "transformacional": {
        "name": "Transformacional",
        "desc": "Inspiras con una visión. Innovación y reputación, aunque cuesta dinero.",
        "mods": {"morale": 1.3, "innovation": 1.4, "reputation": 1.2, "cash": 1.15},
        "power": {"referente": 20, "experto": 5},
    },
    "transaccional": {
        "name": "Transaccional",
        "desc": "Premios por resultados. Eficiente y predecible, con poca innovación.",
        "mods": {"progress": 1.2, "innovation": 0.75, "cash": 0.9},
        "power": {"recompensa": 20, "legitimo": 5},
    },
}


def money(n: int) -> str:
    return f"${n:,}".replace(",", ".")


@dataclass
class Employee:
    name: str
    role: str
    skill: int
    salary: int
    trait: str = ""
    morale: int = 70


@dataclass
class Rival:
    name: str = "Macrosoft"
    cash: int = 80_000
    reputation: int = 40
    last_move: int = 0          # última jugada del rival en una matriz
    betrayed: bool = False      # para la IA "grim"


@dataclass
class GameState:
    company: str = "Aple"
    cash: int = 30_000
    morale: int = 60
    reputation: int = 20
    progress: int = 0
    innovation: int = 30
    power: dict = field(default_factory=lambda: {k: 0 for k in POWER_TYPES})
    leader_style: str | None = None
    team: list = field(default_factory=list)
    rival: Rival = field(default_factory=Rival)
    flags: set = field(default_factory=set)
    log: list = field(default_factory=list)   # (concepto, texto) de decisiones

    # ---------- efectos ----------
    def apply(self, effects: dict, scale_by_style: bool = True) -> list[str]:
        """Aplica efectos y devuelve frases legibles de los cambios ("+5 Moral")."""
        changes = []
        mods = LEADER_STYLES.get(self.leader_style, {}).get("mods", {}) if scale_by_style else {}
        for key, value in (effects or {}).items():
            if key == "flag":
                self.flags.add(value)
            elif key == "flags":
                self.flags.update(value)
            elif key == "unflag":
                self.flags.discard(value)
            elif key.startswith("power."):
                kind = key.split(".", 1)[1]
                self.power[kind] = max(0, min(100, self.power.get(kind, 0) + value))
                changes.append(f"{value:+d} Poder {POWER_TYPES.get(kind, kind)}")
            elif key.startswith("rival."):
                attr = key.split(".", 1)[1]
                setattr(self.rival, attr, getattr(self.rival, attr) + value)
                changes.append(f"{value:+d} {self.rival.name} ({attr})")
            elif key in STATS:
                # El estilo amplifica las ganancias; en dinero amplifica los gastos.
                if key == "cash":
                    factor = mods.get("cash", 1.0) if value < 0 else 1.0
                else:
                    factor = mods.get(key, 1.0) if value > 0 else 1.0
                delta = int(round(value * factor))
                new = getattr(self, key) + delta
                if key in BOUNDED:
                    new = max(0, min(100, new))
                setattr(self, key, new)
                if delta == 0:
                    continue
                if key == "cash":
                    changes.append(("+" if delta >= 0 else "-") + money(abs(delta)) + " Dinero")
                else:
                    changes.append(f"{delta:+d} {STAT_LABELS[key]}")
        return changes

    def check(self, req: dict | None) -> bool:
        if not req:
            return True
        for k, v in req.get("min", {}).items():
            if self._get(k) < v:
                return False
        for k, v in req.get("max", {}).items():
            if self._get(k) > v:
                return False
        if "flag" in req and req["flag"] not in self.flags:
            return False
        if "not_flag" in req and req["not_flag"] in self.flags:
            return False
        if "style" in req and self.leader_style != req["style"]:
            return False
        return True

    def _get(self, key: str):
        if key.startswith("power."):
            return self.power.get(key.split(".", 1)[1], 0)
        if key.startswith("rival."):
            return getattr(self.rival, key.split(".", 1)[1])
        if key == "team_size":
            return len(self.team)
        return getattr(self, key)

    # ---------- liderazgo y equipo ----------
    def set_style(self, style: str) -> None:
        self.leader_style = style
        for kind, val in LEADER_STYLES[style]["power"].items():
            self.power[kind] = min(100, self.power[kind] + val)
        self.log.append(("Estilo de liderazgo", LEADER_STYLES[style]["name"]))

    def hire(self, emp: Employee) -> None:
        self.team.append(emp)
        self.cash -= emp.salary
        self.progress = min(100, self.progress + emp.skill)

    def payroll(self) -> int:
        return sum(e.salary for e in self.team)

    def team_skill(self) -> int:
        return sum(e.skill for e in self.team)

    def end_of_chapter(self) -> list[str]:
        """Entre capítulos: se paga la nómina y el equipo produce."""
        notes = []
        pay = self.payroll()
        if pay:
            self.cash -= pay
            notes.append(f"Nómina pagada: -{money(pay)}")
        skill = self.team_skill()
        if skill:
            boost = skill * (0.5 + self.morale / 100) / 4
            notes += self.apply({"progress": int(boost)})
        if self.leader_style == "laissez_faire" and self.team and skill / len(self.team) < 5:
            notes += self.apply({"morale": -8, "progress": -3})
            notes.append("Sin dirección, el equipo novato se dispersa.")
        return notes

    # ---------- finales ----------
    def score(self) -> int:
        return int(self.cash / 2000 + self.reputation + self.progress + self.innovation
                   + self.morale / 2 + sum(self.power.values()) / 5)

    def is_bankrupt(self) -> bool:
        return self.cash < 0

    def dominant_power(self) -> str:
        return max(self.power, key=self.power.get)


# ---------- teoría de juegos ----------
def rival_move(ai: str, my_last: int | None, rival: Rival, rng=None) -> int:
    """Devuelve 0 (cooperar) o 1 (competir) según la estrategia del rival."""
    rng = rng or random
    if ai == "greedy":
        return 1
    if ai == "random":
        return rng.randint(0, 1)
    if ai == "grim":
        if my_last == 1:
            rival.betrayed = True
        return 1 if rival.betrayed else 0
    # tit_for_tat: empieza cooperando y luego copia tu última jugada
    return 0 if my_last is None else my_last


def nash_equilibria(payoffs) -> list[tuple[int, int]]:
    """Equilibrios de Nash en estrategias puras de una matriz 2x2."""
    eq = []
    for a in range(2):
        for b in range(2):
            mine, theirs = payoffs[a][b]
            best_me = all(mine >= payoffs[x][b][0] for x in range(2))
            best_rival = all(theirs >= payoffs[a][y][1] for y in range(2))
            if best_me and best_rival:
                eq.append((a, b))
    return eq


def play_round(state: GameState, scene: dict, my_move: int, my_last: int | None,
               rng=None) -> dict:
    """Resuelve una ronda de matriz y aplica efectos. Devuelve el detalle."""
    if my_last is None:
        state.rival.betrayed = False  # cada matriz es un juego nuevo
    their = rival_move(scene.get("ai", "tit_for_tat"), my_last, state.rival, rng)
    mine_pts, their_pts = scene["payoffs"][my_move][their]
    per = scene.get("effects_per_point", {"cash": 3000})
    changes = state.apply({k: v * mine_pts for k, v in per.items()}, scale_by_style=False)
    state.rival.cash += per.get("cash", 0) * their_pts
    state.rival.last_move = their
    return {"rival_move": their, "my_points": mine_pts, "rival_points": their_pts,
            "changes": changes}


ENDINGS = [
    # (id, título, condición, texto). Se evalúan en orden.
    ("quiebra", "Quiebra", lambda s: s.is_bankrupt(),
     "Te quedaste sin caja. Aple cierra y el garaje vuelve a ser un garaje. "
     "Lección: un líder sin control del presupuesto no saca el proyecto adelante."),
    ("leyenda", "Leyenda tecnológica", lambda s: s.score() >= 260 and "trato_mosk" in s.flags,
     "Aple es un ícono mundial y Elon Mosk te llama socio. Tu liderazgo y tu manejo "
     "del poder hicieron historia."),
    ("exito", "Empresa exitosa", lambda s: s.score() >= 200,
     "Aple sale a bolsa. No cambiaste el mundo del todo, pero tu equipo te sigue."),
    ("sobrevive", "Sobreviviente", lambda s: s.score() >= 130,
     "Aple sigue viva como empresa de nicho. Algunas decisiones costaron caro."),
    ("absorbida", "Absorbida", lambda s: True,
     "Macrosoft compra Aple por una fracción de su valor. El rival jugó mejor el juego."),
]


def compute_ending(state: GameState):
    for eid, title, cond, text in ENDINGS:
        if cond(state):
            return eid, title, text
    return ENDINGS[-1][0], ENDINGS[-1][1], ENDINGS[-1][3]
