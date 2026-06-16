# Projeto Focus

Pipeline que acompanha o boletim **Focus** do Banco Central do Brasil: baixa o
PDF mais recente, extrai o texto e — numa automação agendada — gera um **resumo
executivo** e o deixa como **rascunho de e-mail no Gmail** para revisão humana.

## Como funciona (divisão de trabalho)

A separação de responsabilidades é proposital:

- **Os scripts Python apenas baixam e extraem.** Nenhum código interpreta,
  comenta ou resume o conteúdo. `baixar_focus.py` busca o PDF; `extrair_texto.py`
  transforma o PDF em texto cru e fiel (`.txt`), sem limpeza nem normalização.
- **O resumo é escrito por um agente lendo o texto extraído.** A leitura
  analítica — identificar o que mudou, contextualizar, redigir o resumo
  executivo — é feita por um agente sobre o `.txt`, não por regras em Python.
  Daí a regra de ouro: todo número citado tem de estar **literalmente** no texto
  extraído (ver `CLAUDE.md`).
- **A entrega final é um rascunho no Gmail**, deixado para revisão antes de
  qualquer envio. Nada é enviado automaticamente.

### Fluxo semanal

```
[Agendado: seg 09h15 BRT]
   src/baixar_focus.py   →  data/focus_AAAA-MM-DD.pdf
   src/extrair_texto.py  →  data/focus_AAAA-MM-DD.txt
        │
        ▼
   agente lê o .txt  →  resumo executivo  →  rascunho de e-mail no Gmail
                                                  (revisão humana)
```

## Estrutura de pastas

```
.
├── src/
│   ├── baixar_focus.py     # baixa o PDF do Focus (trata feriado, valida %PDF)
│   └── extrair_texto.py    # extrai o texto do PDF -> .txt (UTF-8)
├── tests/
│   └── test_baixar_focus.py
├── data/                   # PDFs e textos baixados (não versionados)
├── output/
│   └── focus/              # resumos em markdown (versionados de propósito)
├── .github/
│   └── workflows/
│       └── focus-download.yml   # baixa + extrai toda segunda e commita de volta
├── demo.py                 # roda baixar + extrair em sequência (uso local)
├── requirements.txt
├── pytest.ini
├── CLAUDE.md               # especificação e regras do projeto
└── README.md
```

## Como rodar localmente

Requer Python e as dependências de `requirements.txt`.

```bash
pip install -r requirements.txt
python demo.py            # baixa o Focus mais recente e extrai o texto
python demo.py --abrir    # idem e abre o .txt gerado no navegador
```

Os arquivos baixados ficam em `data/` (ex.: `data/focus_2026-06-05.pdf` e
`data/focus_2026-06-05.txt`).

> Em rede corporativa com inspeção de SSL, o `pip` pode falhar ao acessar o
> PyPI. Nesse caso, instale as dependências via `conda install -c conda-forge`
> (requests, pdfplumber, pytest) num ambiente isolado.

## Como rodar os testes

Rode o `pytest` **de dentro da pasta do projeto** (para carregar o `pytest.ini`):

```bash
pytest -m "not network"   # testes offline (rápidos, sem rede)
pytest -m network         # inclui o download real do BCB
pytest                    # todos
```
