"""Baixa o PDF mais recente do boletim Focus do Banco Central do Brasil.

Padrão de URL do PDF (data de publicação sem hífens):
    https://www.bcb.gov.br/content/focus/focus/R{AAAAMMDD}.pdf

Uso:
    python src/baixar_focus.py
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import requests

# URL-base do PDF; {} recebe a data de publicacao no formato AAAAMMDD (sem hifens).
URL_FOCUS = "https://www.bcb.gov.br/content/focus/focus/R{}.pdf"

# Quantos dias retroceder, a partir da ultima segunda, antes de desistir.
# 7 tentativas cobrem semanas com feriado (o BCB publica na terca, quarta, etc.).
MAX_TENTATIVAS = 7

# User-Agent de navegador: o site do BCB tende a rejeitar clientes "sem cara".
CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def ultima_segunda(hoje: date) -> date:
    """Retorna a segunda-feira mais recente ESTRITAMENTE anterior a `hoje`.

    Se `hoje` ja for uma segunda-feira, retrocede para a segunda da semana
    passada (nunca devolve a propria data recebida).
    """
    # weekday(): segunda=0, terca=1, ..., domingo=6.
    dias_atras = hoje.weekday()
    if dias_atras == 0:
        # Hoje e segunda -> volta uma semana inteira.
        dias_atras = 7
    return hoje - timedelta(days=dias_atras)


def baixar(dest: Path) -> tuple[date, Path]:
    """Baixa o PDF do Focus mais recente para a pasta `dest`.

    Parte da ultima segunda-feira e tenta a URL do dia. Se nao encontrar,
    recua um dia e tenta de novo, ate `MAX_TENTATIVAS` (cobre feriados em que
    a publicacao escorrega para terca/quarta).

    Valida que a resposta comeca com os bytes b"%PDF" antes de aceitar.
    Salva como focus_AAAA-MM-DD.pdf e retorna (data_da_publicacao, caminho).

    Levanta RuntimeError se nenhuma tentativa der certo.
    """
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    candidata = ultima_segunda(date.today())

    for _ in range(MAX_TENTATIVAS):
        # AAAAMMDD para a URL; AAAA-MM-DD para o nome do arquivo.
        url = URL_FOCUS.format(candidata.strftime("%Y%m%d"))

        try:
            resposta = requests.get(url, headers=CABECALHOS, timeout=30)
        except requests.RequestException:
            # Falha de rede nesta data: tenta o dia anterior.
            candidata -= timedelta(days=1)
            continue

        # So aceita 200 com conteudo que realmente seja PDF (assinatura %PDF).
        if resposta.status_code == 200 and resposta.content[:4] == b"%PDF":
            nome = f"focus_{candidata.isoformat()}.pdf"
            caminho = dest / nome
            caminho.write_bytes(resposta.content)
            return candidata, caminho

        # Nao encontrou (404, HTML de erro, etc.): recua um dia.
        candidata -= timedelta(days=1)

    raise RuntimeError(
        f"Nao foi possivel baixar o Focus apos {MAX_TENTATIVAS} tentativas "
        f"(ate {candidata.isoformat()})."
    )


def main() -> None:
    """Baixa o Focus para a pasta data/ e imprime caminho e tamanho em KB."""
    # data/ fica na raiz do projeto (um nivel acima de src/).
    pasta_data = Path(__file__).resolve().parent.parent / "data"

    data_pub, caminho = baixar(pasta_data)

    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Focus de {data_pub.isoformat()}")
    print(f"Arquivo: {caminho}")
    print(f"Tamanho: {tamanho_kb:.1f} KB")


if __name__ == "__main__":
    main()
