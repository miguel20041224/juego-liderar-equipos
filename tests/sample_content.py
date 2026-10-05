"""Contenido mínimo de prueba que cubre los 5 tipos de escena."""

CHARACTERS = {
    "woz": {"name": "Steve Wozniac", "role": "Ingeniero", "skin": (224, 180, 150),
            "hair": (110, 80, 50), "shirt": (60, 90, 140), "accessory": "beard"},
    "inv": {"name": "Inversora", "role": "Capital riesgo", "skin": (190, 140, 110),
            "hair": (30, 25, 25), "shirt": (120, 40, 80), "accessory": "glasses"},
}

CHAPTERS = [
    {"id": "garaje", "title": "Capítulo 1 · El garaje", "concept": "Estilos de liderazgo",
     "lesson": "Cada estilo de liderazgo tiene ventajas y costos. Elige según tu equipo.",
     "scenes": [
         {"type": "leader", "text": "Antes de empezar, define cómo vas a liderar."},
         {"type": "story", "speaker": "Steve Wozniac", "portrait": "woz",
          "text": "Jefe, la placa falla otra vez. ¿Qué hacemos? Podemos arreglarla con calma, "
                  "ordenar turnos de noche o dejar que cada uno la resuelva a su manera.",
          "choices": [
              {"text": "Turnos de noche obligatorios", "effects": {"progress": 8, "morale": -6},
               "feedback": "Avanzan, pero están agotados.", "concept": "Poder coercitivo"},
              {"text": "Reunión para decidir juntos", "effects": {"morale": 6, "power.referente": 4},
               "feedback": "El equipo se siente escuchado."},
              {"text": "Cada quien a su manera", "effects": {"innovation": 6, "progress": -2},
               "feedback": "Surgen ideas raras.", "requires": {"min": {"cash": 1}}},
              {"text": "Solo si eres autocrático", "effects": {"progress": 3}, "feedback": "Ok.",
               "requires": {"style": "autocratico"}},
              {"text": "Opción extra 5", "effects": {"cash": -1000}, "feedback": "Costó dinero."},
          ]},
         {"type": "hire", "text": "Tienes presupuesto limitado. Contrata con cuidado.", "max_hires": 2,
          "candidates": [
              {"name": "Ana", "role": "Diseñadora", "skill": 6, "salary": 9000, "trait": "Creativa"},
              {"name": "Beto", "role": "Programador", "skill": 9, "salary": 18000, "trait": "Estrella, caro"},
              {"name": "Cami", "role": "Becaria", "skill": 3, "salary": 2000, "trait": "Aprende rápido"},
          ]},
         {"type": "allocate", "text": "Triángulo de hierro: reparte 6 puntos.", "points": 6,
          "slots": [
              {"key": "alcance", "label": "Alcance", "effects_per_point": {"progress": 3}},
              {"key": "tiempo", "label": "Tiempo", "effects_per_point": {"morale": 2}},
              {"key": "costo", "label": "Costo", "effects_per_point": {"cash": -1000}},
          ]},
     ]},
    {"id": "rival", "title": "Capítulo 2 · La guerra de precios", "concept": "Teoría de juegos",
     "lesson": "Dilema del prisionero: cooperar es mejor en conjunto, pero competir tienta.",
     "scenes": [
         {"type": "matrix", "text": "Macrosoft y tú fijan precios a la vez.", "rival": "Macrosoft",
          "rounds": 3, "strategy": "tit_for_tat", "options": ["Mantener precio", "Bajar precio"],
          "payoffs": [[[3, 3], [0, 5]], [[5, 0], [1, 1]]],
          "effects_per_point": {"cash": 4000, "reputation": 1},
          "explain": "El equilibrio de Nash es (Bajar, Bajar), aunque (Mantener, Mantener) sería mejor "
                     "para ambos: ese es el dilema del prisionero."},
     ]},
]
