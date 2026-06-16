"""Extrai o texto de um PDF do boletim Focus e salva como .txt (UTF-8).

O texto e extraido cru e fiel ao PDF: nao ha limpeza nem normalizacao, para
nao correr o risco de corromper numeros (medianas, projecoes) que serao usados
no resumo (regra nº 1 do CLAUDE.md: nunca inventar/alterar numero).

Uso:
    python src/extrair_texto.py                 # pega o focus_*.pdf mais recente de data/
    python src/extrair_texto.py --pdf <caminho> # extrai de um PDF especifico
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pdfplumber


def extrair(pdf_path: Path) -> Path:
    """Extrai o texto de `pdf_path` e salva num .txt de mesmo nome (UTF-8).

    Junta o texto de todas as paginas, separando-as por uma linha em branco.
    Paginas sem texto extraivel (ex.: imagem) sao tratadas como vazias.
    Salva ao lado do PDF, trocando apenas a extensao (.pdf -> .txt).

    Retorna o caminho do .txt gerado.

    Levanta RuntimeError se o PDF nao produzir nenhum texto (evita gravar um
    .txt vazio que envenenaria o resumo).
    """
    pdf_path = Path(pdf_path)

    paginas: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            # extract_text() devolve None em pagina sem texto -> trata como "".
            texto = pagina.extract_text() or ""
            paginas.append(texto)

    # Une as paginas com uma linha em branco entre elas.
    texto_completo = "\n\n".join(paginas).strip()

    if not texto_completo:
        raise RuntimeError(
            f"Nenhum texto extraido de {pdf_path.name}. "
            "O PDF pode estar vazio, corrompido ou ser somente imagem."
        )

    # Mesmo nome do PDF, trocando a extensao para .txt.
    txt_path = pdf_path.with_suffix(".txt")
    # UTF-8 explicito: o Focus tem acentos e simbolos (%, –) que o cp1252
    # (padrao do Windows) quebraria.
    txt_path.write_text(texto_completo, encoding="utf-8")

    return txt_path


def _pdf_mais_recente(pasta_data: Path) -> Path | None:
    """Retorna o focus_*.pdf de data mais recente em `pasta_data`, ou None.

    Como o nome segue o padrao focus_AAAA-MM-DD.pdf (data ISO), a ordem
    alfabetica coincide com a ordem cronologica: basta pegar o maior.
    """
    candidatos = sorted(pasta_data.glob("focus_*.pdf"))
    return candidatos[-1] if candidatos else None


def main() -> int:
    """CLI: extrai o texto de um PDF do Focus. Retorna o codigo de saida."""
    parser = argparse.ArgumentParser(
        description="Extrai o texto de um PDF do Focus e salva como .txt (UTF-8)."
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=None,
        help="Caminho de um PDF especifico. Se omitido, usa o focus_*.pdf "
        "mais recente da pasta data/.",
    )
    args = parser.parse_args()

    if args.pdf is not None:
        pdf_path = args.pdf
        if not pdf_path.is_file():
            print(f"Erro: arquivo nao encontrado: {pdf_path}", file=sys.stderr)
            return 1
    else:
        # data/ fica na raiz do projeto (um nivel acima de src/).
        pasta_data = Path(__file__).resolve().parent.parent / "data"
        pdf_path = _pdf_mais_recente(pasta_data)
        if pdf_path is None:
            print(
                "Erro: nenhum PDF (focus_*.pdf) encontrado em data/.\n"
                "Rode 'python src/baixar_focus.py' primeiro para baixar o Focus.",
                file=sys.stderr,
            )
            return 1

    txt_path = extrair(pdf_path)

    n_chars = len(txt_path.read_text(encoding="utf-8"))
    print(f"Texto extraido de: {pdf_path.name}")
    print(f"Arquivo gerado:    {txt_path}")
    print(f"Tamanho:           {n_chars} caracteres")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
