#!/usr/bin/env bash
# Instalador de "Garage -> Imperio". Uso: ./install.sh [--no-run]
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"
RUN=1
for arg in "$@"; do
  case "$arg" in
    --no-run) RUN=0 ;;
    -h|--help) echo "Uso: ./install.sh [--no-run]"; exit 0 ;;
    *) echo "Opcion desconocida: $arg" >&2; exit 2 ;;
  esac
done

PY=""
for cand in python3 python python3.14 python3.13 python3.12 python3.11 python3.10; do
  if command -v "$cand" >/dev/null 2>&1 && \
     "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    PY="$cand"; break
  fi
done

if [ -z "$PY" ]; then
  cat >&2 <<'MSG'
ERROR: se necesita Python 3.10 o superior y no se encontro.
Instalalo segun tu sistema:
  Debian/Ubuntu : sudo apt install python3 python3-venv python3-pip
  Fedora        : sudo dnf install python3
  Arch/CachyOS  : sudo pacman -S python
  macOS         : brew install python
Luego vuelve a ejecutar ./install.sh
MSG
  exit 1
fi
echo ">> Usando $($PY --version) ($PY)"

if [ ! -x .venv/bin/python ]; then
  echo ">> Creando entorno virtual .venv"
  if ! "$PY" -m venv .venv; then
    echo "ERROR: no se pudo crear el entorno virtual." >&2
    echo "En Debian/Ubuntu instala: sudo apt install python3-venv" >&2
    echo "Borra la carpeta .venv incompleta y reintenta." >&2
    exit 1
  fi
fi

echo ">> Instalando dependencias"
.venv/bin/python -m pip install --quiet -U pip
.venv/bin/python -m pip install --quiet -e .

cat > jugar.sh <<'LAUNCH'
#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")"
exec .venv/bin/python -m liderar "$@"
LAUNCH
chmod +x jugar.sh

echo ">> Instalacion completa. Para jugar en el futuro: ./jugar.sh"
if [ "$RUN" -eq 1 ]; then
  exec ./jugar.sh
fi
