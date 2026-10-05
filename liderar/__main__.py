"""Punto de entrada: `python -m liderar` o el comando `liderar`."""

from __future__ import annotations

import argparse
import importlib
import sys


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="liderar", description="Garage → Imperio")
    p.add_argument("--smoke", action="store_true", help="partida automática headless (prueba)")
    p.add_argument("--shots", metavar="DIR", help="(con --smoke) guarda capturas en DIR")
    p.add_argument("--seed", type=int, help="semilla del azar del smoke test")
    p.add_argument("--content", default="liderar.content",
                   help="módulo de contenido (por defecto liderar.content)")
    args = p.parse_args(argv)
    try:
        content = importlib.import_module(args.content)
    except ImportError as exc:
        print(f"No se pudo cargar el contenido '{args.content}': {exc}", file=sys.stderr)
        return 2
    from .ui.app import run
    return run(content, smoke=args.smoke, shots=args.shots, seed=args.seed)


if __name__ == "__main__":
    raise SystemExit(main())
