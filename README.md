# Garage → Imperio

Juego educativo 2D de escritorio donde diriges una startup desde un garaje hasta convertirla (o no) en un imperio. Cada decisión enseña un concepto real de **liderazgo, poder, gestión de proyectos y teoría de juegos**.

<!-- ![Captura del juego](docs/captura.png) -->

## Qué se aprende, capítulo a capítulo

| Capítulo | Concepto | Qué practicas |
|---|---|---|
| Liderazgo | Estilos de liderazgo | Autocrático, democrático, laissez-faire, transformacional y transaccional: cada uno modifica moral, avance, innovación y dinero. |
| Personal y presupuesto | Gestión de equipo | Contratar con presupuesto limitado; la nómina se paga cada capítulo y la moral afecta la productividad. |
| Proyectos | Triángulo de restricciones | Repartir puntos entre alcance, tiempo y costo y ver qué sacrificas. |
| Teoría de juegos | Jugadores, estrategias, pagos, dilema del prisionero, equilibrio de Nash | Matrices de decisión simultánea contra un rival. |
| Poder | Bases de poder de French y Raven y política | Poder legítimo, de recompensa, coercitivo, experto y referente. |
| Negociación | Negociar y cerrar tratos | Alianzas y acuerdos que cambian el final de la historia. |

## Jugadores y estrategias

Juegas tú (**Aple**) contra el rival **Macrosoft**. En cada matriz eliges entre cooperar o competir mientras la IA sigue una estrategia:

- **tit-for-tat**: empieza cooperando y copia tu última jugada.
- **grim**: coopera hasta que lo traicionas; después nunca perdona.
- **greedy**: siempre compite.

Al final de cada matriz el juego explica el equilibrio de Nash. Los nombres de empresas y personajes son **parodias con fines académicos**.

## Instalación (un solo comando)

Requiere Python 3.10+ y [GitHub CLI](https://cli.github.com/).

Linux / macOS:

```bash
gh repo clone miguel20041224/juego-liderar-equipos && cd juego-liderar-equipos && ./install.sh
```

Windows (PowerShell / cmd):

```bat
gh repo clone miguel20041224/juego-liderar-equipos && cd juego-liderar-equipos && install.bat
```

El instalador crea un entorno virtual `.venv`, instala las dependencias, genera el lanzador (`jugar.sh` / `jugar.bat`) y abre el juego. Usa `--no-run` para instalar sin abrirlo. Para jugar después: `./jugar.sh` (o `jugar.bat`).

> **Repositorio privado:** necesitas haber ejecutado `gh auth login` con una cuenta que tenga acceso. Alternativa sin `gh`:
> `git clone https://github.com/miguel20041224/juego-liderar-equipos.git` (te pedirá credenciales o token) y luego `./install.sh` o `install.bat`.

## Controles

- **Ratón**: clic en opciones y botones.
- **1–4**: elegir la opción correspondiente.
- **Enter / Espacio**: continuar o confirmar.
- **Esc**: salir o volver.

## Pruebas

El motor no depende de pygame y se prueba con `unittest` (biblioteca estándar):

```bash
python3 -m unittest discover -s tests -v
```

## Estructura

```
liderar/
  engine.py      motor: estado, efectos, IA rival, equilibrio de Nash, finales
  content.py     capítulos, escenas y textos
  ui/            interfaz pygame
  __main__.py    punto de entrada (python -m liderar)
tests/           pruebas del motor
install.sh / install.bat   instaladores de un comando
pyproject.toml / requirements.txt
```

## Herramientas usadas

Python, pygame-ce, VS Code (o cualquier IDE), Git/GitHub y Claude Code.
