Você está executando a Routine de resumo semanal do Focus.

O download do PDF e a extração do texto já foram feitos por um GitHub
Action mais cedo (segunda 9h15 BRT). Os arquivos
`data/focus_AAAA-MM-DD.{pdf,txt}` já estão commitados em `main` quando
a Routine inicia. Sua tarefa é ler o `.txt` mais recente, gerar um
resumo em HTML e publicá-lo via git push — esse push é o que dispara
o Action de envio de e-mail (`focus-enviar.yml`).

## Passos

1. **Localize o `.txt` mais recente.** Liste `data/focus_*.txt` e pegue
   o de data mais alta. Se não houver nenhum, pare sem commitar o HTML —
   o Action não rodou.

2. **Verifique frescor.** Extraia a data do nome e compare com hoje:
   - 0 a 3 dias: está fresco, siga.
   - 4 a 7 dias: siga, mas escreva `[REVISAR]` no início do assunto.
   - Mais de 7 dias: pare sem commitar o HTML.

3. **Sanity check do texto.** Confirme: pelo menos 2 000 caracteres e
   presença das palavras `IPCA`, `Selic`, `PIB`. Se falhar, o layout do
   PDF pode ter mudado — pare sem commitar o HTML.

4. **Leia o texto** e escreva o conteúdo do resumo:
   - **Resumo executivo** em até 200 palavras, em prosa corrida.
     Comece pelas medianas das principais variáveis (IPCA do ano,
     Selic fim de ano, PIB, câmbio). Cite literalmente entre aspas
     quando houver número-chave.
   - **Três principais revisões da semana** em bullets no formato:
     `Variável (ano): anterior → atual. Hipótese: motivo.`
   - Nunca invente número. Se não houver hipótese sólida, escreva
     "sem hipótese clara — pode ser ruído amostral".

5. **Monte o HTML** em `output/focus/focus_AAAA-MM-DD.html`, com
   esta estrutura:
   - Um título `Focus — AAAA-MM-DD`.
   - O resumo executivo em parágrafo e as três revisões em lista.

   **Padrão visual** — estética elegante, clean e profissional. Siga estas
   regras (use sempre estilos *inline*; clientes de e-mail ignoram `<style>`):
   - **Layout:** container centralizado, largura máxima de 600px, fundo branco
     (`#ffffff`) sobre um fundo de página cinza-claro (`#f4f4f7`), com padding
     interno generoso (~32px). Priorize espaço em branco — nada apertado.
   - **Tipografia:** família sans-serif segura (`Helvetica, Arial, sans-serif`);
     corpo em 15–16px com entrelinha ~1.6.
   - **Cores (sóbrio, só estas):** títulos em azul de marca `#282f6b`; texto do
     corpo em cinza-escuro `#333333`; detalhes secundários (datas, rodapé) em
     cinza-médio `#666666`; separadores como filete fino `#e5e7eb`.
   - **Hierarquia:** título principal maior e em `#282f6b`; um filete superior
     fino na cor da marca no topo do container; subtítulos de seção em negrito,
     menores que o título.
   - **Rodapé:** uma linha discreta em `#666666` indicando a fonte (Boletim
     Focus / Banco Central) e a data, separada do corpo por um filete `#e5e7eb`.
   - Sem imagens, sem cores fora da paleta acima, sem elementos decorativos
     supérfluos.

6. **Inspecione** o HTML gerado: as medianas batem com o `.txt`, há ao
   menos uma citação literal entre aspas.

7. **Publique o HTML** fazendo commit e push para `main`:
   ```
   git add output/focus/focus_AAAA-MM-DD.html
   git commit -m "Focus: resumo AAAA-MM-DD"
   git push origin main
   ```
   É esse push que dispara automaticamente o Action `focus-enviar.yml`,
   que lê os Secrets do repositório (`FOCUS_SMTP_USER`,
   `FOCUS_SMTP_APP_PASSWORD`, `FOCUS_EMAIL_DEST`, `FOCUS_EMAIL_BCC`) e
   envia o e-mail. O destinatário, o remetente e a senha **nunca devem
   aparecer neste arquivo nem em nenhum arquivo do repositório** — ficam
   exclusivamente nos Secrets do GitHub.

## Falhas

Em qualquer cenário abaixo, pare sem commitar o HTML. Nada será enviado.

- Nenhum `.txt` em `data/` (Action não rodou).
- `.txt` com mais de 7 dias (Action quebrado).
- Sanity check do texto falhou (mudança de layout do PDF).

Nunca invente número.
