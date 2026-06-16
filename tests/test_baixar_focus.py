"""Testes para src/baixar_focus.py.

Os testes de ultima_segunda sao puros (sem rede). O teste de baixar() faz
download real e por isso esta marcado com @pytest.mark.network — pule-o com
    pytest -m "not network"
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

# Insere src/ no path de import, como no demo.py (tests/ fica um nivel abaixo da raiz).
SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

from baixar_focus import MAX_TENTATIVAS, baixar, ultima_segunda  # noqa: E402


# ---------------------------------------------------------------------------
# Testes puros (sem rede) para ultima_segunda.
# weekday(): segunda=0, terca=1, ..., domingo=6.
# Referencia: 2026-06-01 e uma segunda-feira.
# ---------------------------------------------------------------------------


def test_quinta_volta_para_segunda_da_mesma_semana():
    # Quinta 2026-06-04 -> segunda 2026-06-01 (mesma semana).
    assert ultima_segunda(date(2026, 6, 4)) == date(2026, 6, 1)


def test_terca_volta_para_segunda_anterior():
    # Terca 2026-06-09 -> segunda 2026-06-08 (vespera).
    assert ultima_segunda(date(2026, 6, 9)) == date(2026, 6, 8)


def test_segunda_recua_uma_semana_inteira():
    # Segunda 2026-06-08 -> NAO devolve a propria data; recua 7 dias -> 2026-06-01.
    assert ultima_segunda(date(2026, 6, 8)) == date(2026, 6, 1)


def test_domingo_volta_para_segunda_da_semana():
    # Domingo 2026-06-07 -> segunda 2026-06-01 (inicio da mesma semana).
    assert ultima_segunda(date(2026, 6, 7)) == date(2026, 6, 1)


def test_varredura_60_dias_sempre_segunda_anterior():
    # Para 60 dias consecutivos, o retorno deve ser SEMPRE:
    #   (a) uma segunda-feira (weekday() == 0) e
    #   (b) estritamente anterior a data dada.
    base = date(2026, 1, 1)
    for i in range(60):
        dia = base + timedelta(days=i)
        resultado = ultima_segunda(dia)
        assert resultado.weekday() == 0, f"{resultado} nao e segunda (dia={dia})"
        assert resultado < dia, f"{resultado} nao e anterior a {dia}"


# ---------------------------------------------------------------------------
# Teste de rede: download real do Focus.
# ---------------------------------------------------------------------------


@pytest.mark.network
def test_baixar_download_real(tmp_path):
    data_pub, caminho = baixar(tmp_path)

    # Arquivo foi criado.
    assert caminho.exists(), "o arquivo nao foi criado"

    conteudo = caminho.read_bytes()

    # Comeca com a assinatura de PDF.
    assert conteudo[:4] == b"%PDF", "o arquivo nao comeca com os bytes %PDF"

    # Tem mais de 50 KB (um Focus real pesa centenas de KB).
    assert len(conteudo) > 50 * 1024, "arquivo menor que 50 KB"

    # O nome bate com a data de publicacao retornada.
    assert caminho.name == f"focus_{data_pub.isoformat()}.pdf"

    # A data esta dentro da janela esperada:
    #   - nunca no futuro (<= hoje);
    #   - nao muito no passado: baixar() parte da ultima segunda e recua ate
    #     MAX_TENTATIVAS dias, entao o piso e (ultima_segunda - MAX_TENTATIVAS).
    hoje = date.today()
    teto = ultima_segunda(hoje)
    piso = teto - timedelta(days=MAX_TENTATIVAS)
    assert data_pub <= hoje, "data de publicacao no futuro"
    assert piso <= data_pub <= teto, f"data {data_pub} fora da janela [{piso}, {teto}]"
