"""Envia o resumo HTML do Focus por e-mail via SMTP do Gmail (SSL, porta 465).

Credenciais lidas de variáveis de ambiente (nunca em código):
    FOCUS_SMTP_USER         remetente (ex.: voce@gmail.com)
    FOCUS_SMTP_APP_PASSWORD senha de app do Gmail (16 chars, sem espaços)
    FOCUS_EMAIL_DEST        destinatários separados por vírgula
    FOCUS_EMAIL_BCC         destinatários em cópia oculta (opcional)

Uso rápido:
    python src/enviar_email.py                   # envia o HTML mais recente
    python src/enviar_email.py --dry-run         # monta e imprime sem enviar
    python src/enviar_email.py --html output/focus/focus_2026-06-12.html
    python src/enviar_email.py --dest a@b.com,c@d.com --assunto "Meu assunto"
"""

from __future__ import annotations

import argparse
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL direto (não STARTTLS)

# Pasta onde os resumos HTML são gravados.
PASTA_OUTPUT = Path(__file__).resolve().parent.parent / "output" / "focus"


# ---------------------------------------------------------------------------
# Localização do HTML
# ---------------------------------------------------------------------------


def html_mais_recente(pasta: Path) -> Path | None:
    """Retorna o focus_*.html de data mais alta em `pasta`, ou None se vazio."""
    candidatos = sorted(pasta.glob("focus_*.html"))
    return candidatos[-1] if candidatos else None


# ---------------------------------------------------------------------------
# Montagem da mensagem
# ---------------------------------------------------------------------------


def _texto_fallback(html: str) -> str:
    """Gera um fallback em texto plano removendo as tags HTML.

    Clientes que não renderizam HTML mostram este texto em vez de código.
    Não é um parser completo — serve apenas de leitura de emergência.
    """
    import re

    sem_tags = re.sub(r"<[^>]+>", " ", html)
    # Colapsa espaços/quebras múltiplas que sobraram após remover as tags.
    linhas = [l.strip() for l in sem_tags.splitlines() if l.strip()]
    return "\n".join(linhas)


def montar_mensagem(
    *,
    html_path: Path,
    remetente: str,
    destinatarios: list[str],
    bcc: list[str],
    assunto: str,
) -> MIMEMultipart:
    """Monta o objeto MIMEMultipart com as partes texto e HTML."""
    html_content = html_path.read_text(encoding="utf-8")
    texto_plano = _texto_fallback(html_content)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)
    if bcc:
        # BCC não aparece no cabeçalho — é passado só no envelope SMTP.
        msg["Bcc"] = ", ".join(bcc)

    # Ordem importa: clientes escolhem a última parte que conseguem renderizar.
    msg.attach(MIMEText(texto_plano, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    return msg


# ---------------------------------------------------------------------------
# Envio
# ---------------------------------------------------------------------------


def enviar(msg: MIMEMultipart, usuario: str, senha: str) -> None:
    """Conecta ao Gmail via SSL e envia `msg`."""
    # Todos os destinatários (To + Bcc) precisam ir no envelope.
    todos = msg["To"].split(", ")
    if msg["Bcc"]:
        todos += msg["Bcc"].split(", ")
    todos = [e.strip() for e in todos if e.strip()]

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as servidor:
        servidor.login(usuario, senha)
        servidor.sendmail(msg["From"], todos, msg.as_string())


# ---------------------------------------------------------------------------
# Helpers de CLI
# ---------------------------------------------------------------------------


def _assunto_do_nome(html_path: Path) -> str:
    """Deriva o assunto a partir do nome do arquivo (focus_AAAA-MM-DD.html)."""
    stem = html_path.stem  # ex.: "focus_2026-06-12"
    # Extrai a data que vem depois do primeiro underscore.
    partes = stem.split("_", 1)
    data_str = partes[1] if len(partes) == 2 else stem
    return f"Resumo Focus — {data_str}"


def _ler_env(nome: str, obrigatorio: bool = True) -> str:
    """Lê variável de ambiente; levanta EnvironmentError se obrigatória e ausente."""
    valor = os.environ.get(nome, "").strip()
    if obrigatorio and not valor:
        raise EnvironmentError(
            f"Variável de ambiente '{nome}' não definida ou vazia.\n"
            "Defina-a antes de rodar o script (nunca coloque a senha no código)."
        )
    return valor


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Envia o resumo HTML do Focus por e-mail via Gmail SMTP."
    )
    parser.add_argument(
        "--html",
        type=Path,
        default=None,
        help="Caminho do HTML a enviar. Padrão: focus_*.html mais recente em output/focus/.",
    )
    parser.add_argument(
        "--dest",
        default="",
        help="Destinatários separados por vírgula (sobrescreve FOCUS_EMAIL_DEST).",
    )
    parser.add_argument(
        "--assunto",
        default="",
        help="Assunto do e-mail (padrão derivado do nome do arquivo).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Monta e imprime o e-mail sem enviar nem exigir credenciais.",
    )
    args = parser.parse_args()

    # --- Localiza o HTML ---
    if args.html is not None:
        html_path = Path(args.html)
        if not html_path.is_file():
            print(f"Erro: arquivo não encontrado: {html_path}", file=sys.stderr)
            return 1
    else:
        html_path = html_mais_recente(PASTA_OUTPUT)
        if html_path is None:
            print(
                "Erro: nenhum HTML (focus_*.html) encontrado em output/focus/.\n"
                "Gere o resumo antes de enviar.",
                file=sys.stderr,
            )
            return 1

    # --- Assunto ---
    assunto = args.assunto or _assunto_do_nome(html_path)

    # --- Destinatários ---
    dest_raw = args.dest or (os.environ.get("FOCUS_EMAIL_DEST", "") if not args.dry_run else "dry-run@exemplo.com")
    destinatarios = [e.strip() for e in dest_raw.split(",") if e.strip()]
    if not destinatarios:
        print(
            "Erro: nenhum destinatário definido.\n"
            "Use --dest ou defina FOCUS_EMAIL_DEST.",
            file=sys.stderr,
        )
        return 1

    bcc_raw = os.environ.get("FOCUS_EMAIL_BCC", "")
    bcc = [e.strip() for e in bcc_raw.split(",") if e.strip()]

    # --- Remetente (só obrigatório fora do dry-run) ---
    if args.dry_run:
        remetente = os.environ.get("FOCUS_SMTP_USER", "dry-run@exemplo.com")
    else:
        remetente = _ler_env("FOCUS_SMTP_USER")

    # --- Monta a mensagem ---
    msg = montar_mensagem(
        html_path=html_path,
        remetente=remetente,
        destinatarios=destinatarios,
        bcc=bcc,
        assunto=assunto,
    )

    # --- Dry-run: imprime cabeçalhos e prévia do corpo montado ---
    if args.dry_run:
        # Extrai o texto plano da parte já montada para confirmar que o HTML foi lido.
        texto_preview = ""
        for parte in msg.walk():
            if parte.get_content_type() == "text/plain":
                texto_preview = parte.get_payload(decode=True).decode("utf-8")
                break
        # Mostra as primeiras 300 chars do corpo para validação visual.
        preview = texto_preview[:300].strip()
        if len(texto_preview) > 300:
            preview += " [...]"

        print("=== DRY-RUN — e-mail NÃO enviado ===")
        print(f"De:       {msg['From']}")
        print(f"Para:     {msg['To']}")
        if bcc:
            print(f"Bcc:      {msg['Bcc']}")
        print(f"Assunto:  {msg['Subject']}")
        print(f"HTML:     {html_path}")
        print(f"Tamanho:  {html_path.stat().st_size / 1024:.1f} KB")
        print(f"Partes:   {len(msg.get_payload())} (text/plain + text/html)")
        print("--- prévia do corpo (texto plano) ---")
        print(preview)
        print("=====================================")
        return 0

    # --- Envio real ---
    senha = _ler_env("FOCUS_SMTP_APP_PASSWORD")
    try:
        enviar(msg, remetente, senha)
    except smtplib.SMTPAuthenticationError:
        print(
            "Erro de autenticação no Gmail.\n"
            "Verifique FOCUS_SMTP_USER e FOCUS_SMTP_APP_PASSWORD.\n"
            "A senha de app deve ter 16 caracteres sem espaços.",
            file=sys.stderr,
        )
        return 1
    except smtplib.SMTPException as exc:
        print(f"Erro SMTP: {exc}", file=sys.stderr)
        return 1

    print(f"E-mail enviado com sucesso para: {msg['To']}")
    if bcc:
        print(f"Bcc: {msg['Bcc']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
