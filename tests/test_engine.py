"""Pruebas del motor (sin pygame). Ejecutar: python3 -m unittest discover -s tests -v"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from liderar import engine  # noqa: E402
from liderar.engine import (  # noqa: E402
    Employee, GameState, Rival, compute_ending, nash_equilibria, play_round, rival_move,
)

PRISONERS = [[[3, 3], [0, 5]], [[5, 0], [1, 1]]]
COORDINATION = [[[2, 2], [0, 0]], [[0, 0], [1, 1]]]


class ApplyTests(unittest.TestCase):
    def test_bounded_stats_clamped(self):
        s = GameState()
        s.apply({"morale": 500, "reputation": -500})
        self.assertEqual(s.morale, 100)
        self.assertEqual(s.reputation, 0)

    def test_cash_unbounded_and_message(self):
        s = GameState(cash=1000)
        changes = s.apply({"cash": -5000})
        self.assertEqual(s.cash, -4000)
        self.assertIn("Dinero", changes[0])

    def test_style_amplifies_gains_only(self):
        s = GameState(morale=50)
        s.set_style("democratico")          # morale x1.4
        s.apply({"morale": 10})
        self.assertEqual(s.morale, 64)
        s.apply({"morale": -10})            # perdidas sin modificar
        self.assertEqual(s.morale, 54)

    def test_style_amplifies_spending(self):
        s = GameState(cash=10_000)
        s.set_style("transformacional")     # cash x1.15 en gastos
        s.apply({"cash": -1000})
        self.assertEqual(s.cash, 10_000 - 1150)

    def test_scale_by_style_false(self):
        s = GameState(morale=50)
        s.set_style("democratico")
        s.apply({"morale": 10}, scale_by_style=False)
        self.assertEqual(s.morale, 60)

    def test_power_clamped(self):
        s = GameState()
        s.apply({"power.experto": 150})
        self.assertEqual(s.power["experto"], 100)
        s.apply({"power.experto": -300})
        self.assertEqual(s.power["experto"], 0)

    def test_rival_effect(self):
        s = GameState()
        s.apply({"rival.cash": -10_000, "rival.reputation": 5})
        self.assertEqual(s.rival.cash, 70_000)
        self.assertEqual(s.rival.reputation, 45)

    def test_flags(self):
        s = GameState()
        s.apply({"flag": "a", "flags": ["b", "c"]})
        self.assertEqual(s.flags, {"a", "b", "c"})
        s.apply({"unflag": "a"})
        self.assertNotIn("a", s.flags)
        s.apply({"unflag": "no_existe"})    # no debe fallar

    def test_empty_effects(self):
        self.assertEqual(GameState().apply(None), [])


class CheckTests(unittest.TestCase):
    def test_empty_requirement(self):
        self.assertTrue(GameState().check(None))
        self.assertTrue(GameState().check({}))

    def test_min_max(self):
        s = GameState(cash=5000)
        self.assertTrue(s.check({"min": {"cash": 5000}}))
        self.assertFalse(s.check({"min": {"cash": 5001}}))
        self.assertTrue(s.check({"max": {"cash": 5000}}))
        self.assertFalse(s.check({"max": {"cash": 4999}}))

    def test_min_power_and_team_size(self):
        s = GameState()
        s.power["experto"] = 10
        self.assertTrue(s.check({"min": {"power.experto": 10}}))
        self.assertFalse(s.check({"min": {"team_size": 1}}))
        s.hire(Employee("A", "dev", 5, 100))
        self.assertTrue(s.check({"min": {"team_size": 1}}))

    def test_flag_not_flag(self):
        s = GameState()
        s.flags.add("x")
        self.assertTrue(s.check({"flag": "x"}))
        self.assertFalse(s.check({"flag": "y"}))
        self.assertFalse(s.check({"not_flag": "x"}))
        self.assertTrue(s.check({"not_flag": "y"}))

    def test_style(self):
        s = GameState()
        self.assertFalse(s.check({"style": "autocratico"}))
        s.set_style("autocratico")
        self.assertTrue(s.check({"style": "autocratico"}))
        self.assertFalse(s.check({"style": "democratico"}))


class TeamTests(unittest.TestCase):
    def test_set_style_adds_power_and_logs(self):
        s = GameState()
        s.set_style("autocratico")
        self.assertEqual(s.leader_style, "autocratico")
        self.assertEqual(s.power["coercitivo"], 15)
        self.assertEqual(s.power["legitimo"], 15)
        self.assertEqual(s.log[-1][0], "Estilo de liderazgo")

    def test_hire_and_payroll(self):
        s = GameState(cash=10_000)
        s.hire(Employee("A", "dev", 10, 2000))
        s.hire(Employee("B", "arte", 5, 1000))
        self.assertEqual(s.cash, 7000)
        self.assertEqual(s.progress, 15)
        self.assertEqual(s.payroll(), 3000)
        self.assertEqual(s.team_skill(), 15)

    def test_hire_progress_capped(self):
        s = GameState(progress=95)
        s.hire(Employee("A", "dev", 20, 0))
        self.assertEqual(s.progress, 100)

    def test_end_of_chapter_pays_and_produces(self):
        s = GameState(cash=10_000, morale=100)
        s.hire(Employee("A", "dev", 8, 1000))
        cash, prog = s.cash, s.progress
        notes = s.end_of_chapter()
        self.assertEqual(s.cash, cash - 1000)
        self.assertGreater(s.progress, prog)
        self.assertTrue(any("Nómina" in n for n in notes))

    def test_end_of_chapter_empty_team(self):
        s = GameState()
        self.assertEqual(s.end_of_chapter(), [])

    def test_laissez_faire_novices_penalty(self):
        s = GameState(cash=10_000, morale=60, progress=10)
        s.set_style("laissez_faire")
        s.hire(Employee("Novato", "dev", 2, 500))
        before = s.morale
        notes = s.end_of_chapter()
        self.assertLess(s.morale, before + 1)
        self.assertTrue(any("novato" in n for n in notes))


class GameTheoryTests(unittest.TestCase):
    def test_nash_prisoners_dilemma(self):
        self.assertEqual(nash_equilibria(PRISONERS), [(1, 1)])

    def test_nash_coordination_two_equilibria(self):
        self.assertEqual(sorted(nash_equilibria(COORDINATION)), [(0, 0), (1, 1)])

    def test_tit_for_tat(self):
        r = Rival()
        self.assertEqual(rival_move("tit_for_tat", None, r), 0)
        self.assertEqual(rival_move("tit_for_tat", 1, r), 1)
        self.assertEqual(rival_move("tit_for_tat", 0, r), 0)

    def test_greedy(self):
        r = Rival()
        self.assertEqual(rival_move("greedy", None, r), 1)
        self.assertEqual(rival_move("greedy", 0, r), 1)

    def test_grim_never_forgives(self):
        r = Rival()
        self.assertEqual(rival_move("grim", None, r), 0)
        self.assertEqual(rival_move("grim", 0, r), 0)
        self.assertEqual(rival_move("grim", 1, r), 1)
        self.assertTrue(r.betrayed)
        self.assertEqual(rival_move("grim", 0, r), 1)

    def test_random_uses_rng(self):
        r = Rival()
        moves = {rival_move("random", None, r, random.Random(i)) for i in range(30)}
        self.assertEqual(moves, {0, 1})

    def test_play_round(self):
        s = GameState(cash=0)
        scene = {"strategy": "greedy", "payoffs": PRISONERS,
                 "effects_per_point": {"cash": 1000}}
        res = play_round(s, scene, 0, None)      # yo coopero, rival traiciona
        self.assertEqual(res["rival_move"], 1)
        self.assertEqual(res["my_points"], 0)
        self.assertEqual(res["rival_points"], 5)
        self.assertEqual(s.cash, 0)
        self.assertEqual(s.rival.cash, 80_000 + 5000)
        self.assertEqual(s.rival.last_move, 1)

    def test_play_round_ignores_style(self):
        s = GameState(cash=0)
        s.set_style("transaccional")
        scene = {"strategy": "tit_for_tat", "payoffs": PRISONERS,
                 "effects_per_point": {"cash": 1000}}
        res = play_round(s, scene, 0, None)      # ambos cooperan: 3 pts
        self.assertEqual(res["my_points"], 3)
        self.assertEqual(s.cash, 3000)


class EndingTests(unittest.TestCase):
    def test_bankruptcy(self):
        s = GameState(cash=-1, reputation=100, progress=100, innovation=100)
        self.assertTrue(s.is_bankrupt())
        self.assertEqual(compute_ending(s)[0], "quiebra")

    def test_absorbed_default(self):
        s = GameState(cash=0, morale=0, reputation=0, progress=0, innovation=0)
        self.assertEqual(compute_ending(s)[0], "absorbida")

    def test_success_tiers(self):
        s = GameState(cash=50_000, morale=100, reputation=80, progress=80, innovation=60)
        self.assertGreaterEqual(s.score(), 200)
        self.assertIn(compute_ending(s)[0], ("exito", "leyenda"))
        s.flags.add("trato_mosk")
        s.power["referente"] = 100
        self.assertEqual(compute_ending(s)[0], "leyenda")

    def test_dominant_power(self):
        s = GameState()
        s.power["referente"] = 30
        self.assertEqual(s.dominant_power(), "referente")

    def test_money_format(self):
        self.assertEqual(engine.money(1234567), "$1.234.567")


if __name__ == "__main__":
    unittest.main()
