# Projeto Focus

Baixar semanalmente o boletim **Focus** do Banco Central do Brasil (PDF), extrair o
texto e preparar um resumo executivo.

## Objetivo

- Toda **segunda-feira**, baixar o Focus mais recente do BCB.
- Extrair o texto do PDF.
- Preparar um **resumo executivo** em markdown.

## Fonte

- Página de referência: https://www.bcb.gov.br/publicacoes/focus
- Padrão de URL do PDF: `https://www.bcb.gov.br/content/focus/focus/R{AAAAMMDD}.pdf`
  - `{AAAAMMDD}` = data de publicação, ex.: `R20260601.pdf` para 2026-06-01.

## Convenções

- **Nomenclatura de arquivos:** `focus_AAAA-MM-DD` (data da **publicação**).
  - PDF: `focus_AAAA-MM-DD.pdf`
  - Texto extraído: `focus_AAAA-MM-DD.txt`
  - Resumo: `focus_AAAA-MM-DD.md`
- **Datas:** sempre no formato `AAAA-MM-DD` (ISO 8601). Nunca `DD/MM/AAAA`.

## Estrutura de pastas

```
.
├── src/                  # código-fonte (download, extração, resumo)
├── tests/                # testes
├── data/                 # PDFs e textos baixados (focus_AAAA-MM-DD.pdf / .txt)
├── output/
│   └── focus/            # resumos em markdown (focus_AAAA-MM-DD.md)
├── .github/
│   └── workflows/        # automação (agendamento semanal)
└── CLAUDE.md
```

## Regras (importantes — não violar)

1. **Nunca inventar número.** Toda mediana (ou qualquer valor) citada no resumo
   **precisa estar literalmente no texto extraído** do PDF. Se não está no texto,
   não entra no resumo.
2. **Feriado na segunda:** quando a segunda é feriado, o BCB publica na **terça**.
   O download deve **retroceder dia a dia** (segunda → terça → ...) até encontrar o
   PDF disponível na URL.

## Ambiente

- Python (env Anaconda `bwgi`).
- Datas e nomes de arquivo sempre em `AAAA-MM-DD`.
