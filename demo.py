"""Roda o pipeline do Focus localmente: baixa o PDF e extrai o texto, em sequencia.

Uso:
    python demo.py            # baixa + extrai
    python demo.py --abrir    # idem e abre o .txt no navegador padrao
"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

# Raiz do projeto (pasta onde este demo.py esta) e a pasta src/.
RAIZ = Path(__file__).resolve().parent
SRC = RAIZ / "src"

# Coloca src/ no path de import para usar os modulos do pipeline como pacotes soltos.
sys.path.insert(0, str(SRC))

from baixar_focus import baixar  # noqa: E402  (import apos ajustar sys.path)
from extrair_texto import extrair  # noqa: E402


def main() -> int:
    """Executa as duas etapas em sequencia. Retorna o codigo de saida."""
    parser = argparse.ArgumentParser(
        description="Roda o pipeline do Focus: baixa o PDF e extrai o texto."
    )
    parser.add_argument(
        "--abrir",
        action="store_true",
        help="Abre o .txt gerado no navegador padrao ao final.",
    )
    args = parser.parse_args()

    pasta_data = RAIZ / "data"

    # [1/2] Download do PDF mais recente para data/.
    _data_pub, pdf_path = baixar(pasta_data)
    tamanho_kb = pdf_path.stat().st_size / 1024
    print(f"[1/2] PDF baixado: {pdf_path.name} ({tamanho_kb:.1f} KB)")

    # [2/2] Extracao do texto do PDF recem-baixado.
    txt_path = extrair(pdf_path)
    print(f"[2/2] Texto extraido: {txt_path}")

    # --abrir: abre o .txt no navegador padrao (file:// URI funciona no Windows).
    if args.abrir:
        webbrowser.open(txt_path.as_uri())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
