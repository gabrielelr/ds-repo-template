#!/usr/bin/env python3
"""
DS — Weekly Report Generator
Messaggio 1: report strutturato (componenti, date, autori, progetti)
Messaggio 2+: post conversazionale per ogni componente (Claude)

NOTA: personalizza `DS_NAME` (vedi env nel workflow) con il nome del tuo
Design System prima di usare lo script in produzione.
"""

import os
import json
import re
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
CLAUDE_MODEL = "claude-sonnet-4-6"
FIGMA_BASE_URL = "https://www.figma.com/file/"
DS_NAME = os.environ.get("DS_NAME", "Design System")

TYPE_EMOJI = {
    "new": "🆕",
    "updated": "✏️",
    "update": "✏️",
    "bug fix": "🐛",
    "fix": "🐛",
    "removed": "🗑️",
    "deprecated": "⚠️",
}

def get_emoji(change_type: str) -> str:
    return TYPE_EMOJI.get(change_type.lower(), "•")


# ─── Git ─────────────────────────────────────────────────────────────────────

def get_last_report_tag():
    result = subprocess.run(
        ["git", "tag", "--list", "report-*", "--sort=-version:refname"],
        capture_output=True, text=True
    )
    tags = [t for t in result.stdout.strip().split("\n") if t]
    return tags[0] if tags else None


def get_changed_changelog_files(since_ref):
    if since_ref:
        cmd = ["git", "diff", "--name-only", since_ref, "HEAD"]
    else:
        cmd = ["git", "log", "--name-only", "--pretty=format:", "--since=7 days ago"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    return list(set(
        f for f in files
        if f.endswith("changelog.md") and f.startswith("components/")
    ))


def get_new_lines_from_diff(filepath: str, since_ref: str) -> str:
    """Restituisce solo le righe AGGIUNTE nel file rispetto all'ultimo tag."""
    if since_ref:
        cmd = ["git", "diff", since_ref, "HEAD", "--", filepath]
    else:
        cmd = ["git", "diff", "HEAD~7", "HEAD", "--", filepath]
    result = subprocess.run(cmd, capture_output=True, text=True)
    added = [
        line[1:]  # rimuove il "+" iniziale
        for line in result.stdout.split("\n")
        if line.startswith("+") and not line.startswith("+++")
    ]
    return "\n".join(added)


def create_report_tag():
    base = datetime.now().strftime("%Y-%m-%d")
    tag = f"report-{base}"
    # Se il tag esiste già (run multipli nello stesso giorno) aggiungi orario
    existing = subprocess.run(
        ["git", "tag", "--list", tag], capture_output=True, text=True
    ).stdout.strip()
    if existing:
        tag = f"report-{datetime.now().strftime('%Y-%m-%d-%H%M')}"
    subprocess.run(["git", "tag", tag], check=True)
    subprocess.run(["git", "push", "origin", tag], check=True)
    return tag


# ─── Parsing ─────────────────────────────────────────────────────────────────

def parse_frontmatter(content: str) -> dict:
    meta = {"component": "", "figma_id": "", "last_updated": ""}
    if not content.startswith("---"):
        return meta
    end = content.find("---", 3)
    if end == -1:
        return meta
    for line in content[3:end].strip().split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip().strip('"')
    return meta


def parse_entries(content: str) -> list:
    """
    Estrae le voci changelog come lista di dict:
    {date, type, description, author, project}
    """
    entries = []
    current_date = ""
    body = re.sub(r"^---.*?---\s*", "", content, flags=re.DOTALL)
    body = re.sub(r"^#(?!#)[^\n]*\n", "", body, flags=re.MULTILINE)  # rimuove solo # non ##

    for line in body.split("\n"):
        date_match = re.match(r"^###\s+(.+)", line)
        if date_match:
            current_date = date_match.group(1).strip()
            continue

        entry_match = re.match(r"^-\s+\*\*(.+?)\*\*\s*[·•]\s*(.+)", line)
        if entry_match and current_date:
            change_type = entry_match.group(1).strip()
            rest = entry_match.group(2).strip()
            parts = rest.split(" — ")
            description = parts[0].strip()
            author, project = "", ""
            if len(parts) > 1:
                m = re.match(r"\*(.+?)\*\s*[·•]?\s*(.*)", parts[1])
                if m:
                    author = m.group(1).strip()
                    project = m.group(2).strip()
                else:
                    author = parts[1].strip()
            entries.append({
                "date": current_date,
                "type": change_type,
                "description": description,
                "author": author,
                "project": project,
            })
    return entries


# ─── Messaggio 1: Report strutturato Block Kit ───────────────────────────────

def build_weekly_report_blocks(changelogs_data: list) -> dict:
    today = datetime.now().strftime("%d %b %Y")
    active = [d for d in changelogs_data if d["entries"]]
    n = len(active)

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📋  {DS_NAME} — Weekly Report  |  {today}",
                "emoji": True,
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"_{n} {'componente aggiornato' if n == 1 else 'componenti aggiornati'} questa settimana_",
                }
            ],
        },
        {"type": "divider"},
    ]

    # Larghezze colonne fisse — la descrizione va su riga separata
    W = {"date": 11, "type": 13, "author": 18, "project": 14}

    def pad(s, w):
        return str(s or "—").ljust(w)

    for item in active:
        meta    = item["meta"]
        entries = item["entries"]
        component = meta.get("component") or item["filepath"].split("/")[1].title()
        figma_id  = meta.get("figma_id", "").strip().strip('"')
        figma_url = f"{FIGMA_BASE_URL}{figma_id}" if figma_id else None

        # ── Intestazione componente ──
        header_md = f"*{component}*"
        if figma_url:
            header_md += f"   |   <{figma_url}|Apri in Figma →>"

        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": header_md},
        })

        # ── Tabella monospace ──
        col_header = (
            pad("DATA",   W["date"])
            + pad("TIPO", W["type"])
            + pad("AUTORE", W["author"])
            + "PROGETTO"
        )
        sep = "─" * sum(W.values())
        rows = [col_header, sep]

        for e in entries:
            # Riga con colonne fisse
            rows.append(
                pad(e["date"],   W["date"])
                + pad(e["type"], W["type"])
                + pad(e["author"] or "—", W["author"])
                + (e["project"] or "—")
            )
            # Descrizione su riga dedicata, indentata
            rows.append(f"  → {e['description']}")
            rows.append("")  # riga vuota tra entry

        table = "```" + "\n".join(rows) + "```"
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": table},
        })

        blocks.append({"type": "divider"})

    return {"blocks": blocks}


# ─── Messaggio 2+: Post per componente (Claude) ───────────────────────────────

def call_claude(changelogs_data: list) -> dict:
    components_text = ""
    for item in changelogs_data:
        meta = item["meta"]
        entries = item["entries"]
        if not entries:
            continue

        component_name = meta.get("component") or item["filepath"].split("/")[1].title()
        figma_id = meta.get("figma_id", "").strip().strip('"')
        figma_url = f"{FIGMA_BASE_URL}{figma_id}" if figma_id else None

        components_text += f"\n### {component_name}\n"
        if figma_url:
            components_text += f"Link Figma: {figma_url}\n"
        components_text += "Modifiche:\n"
        for e in entries:
            line = f"- [{e['type']}] {e['description']}"
            if e["author"]:
                line += f" (di {e['author']})"
            if e["project"]:
                line += f" — progetto: {e['project']}"
            components_text += line + "\n"

    prompt = f"""Sei il comunicatore del {DS_NAME}. Scrivi in italiano.

Questa settimana sono stati aggiornati questi componenti:
{components_text}

Per ogni componente scrivi UN POST SLACK seguendo questo stile esatto:

ESEMPIO:
---
Ciao a tutti! 👋

Ho appena pubblicato un aggiornamento al componente *Button* — da adesso lo stato hover è molto più leggibile su sfondi chiari.

Questa modifica è arrivata perché diversi team ci avevano segnalato difficoltà nel distinguere lo stato hover su alcuni layout. Ho aumentato il contrasto e allineato tutto alle linee guida di accessibilità.

🔗 Componente su Figma: https://www.figma.com/file/xxx

⚠️ Ricordate di aggiornare le librerie nei vostri file di lavoro per ricevere questa modifica — qualsiasi file in cui usate il Button andrà refreshato.

Grazie, DS Team
---

REGOLE:
- Prima persona, tono caldo e diretto
- Inizia sempre con un saluto ("Ciao a tutti! 👋" o "Hey! 👋" o simile)
- Spiega il PERCHÉ della modifica — il problema che risolve, non solo cosa è cambiato
- Se il link Figma è disponibile includilo, altrimenti ometti la riga
- Includi SEMPRE il reminder di aggiornare le librerie con menzione dei file impattati
- Chiudi sempre con "Grazie, DS Team"
- In Slack grassetto = *asterischi*, corsivo = _underscore_
- Usa emoji con misura

Rispondi ESCLUSIVAMENTE con un oggetto JSON valido, senza testo prima o dopo:
{{
  "component_posts": [
    {{
      "component": "nome componente",
      "post": "testo completo del post Slack"
    }}
  ]
}}"""

    body = json.dumps({
        "model": CLAUDE_MODEL,
        "max_tokens": 3000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        raw = result["content"][0]["text"].strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        return json.loads(raw)


# ─── Slack ────────────────────────────────────────────────────────────────────

def post_to_slack(payload: dict):
    """payload può essere {"text": "..."} oppure {"blocks": [...]}"""
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status != 200:
                print(f"⚠️  Slack ha risposto con status {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"❌ Errore Slack: {e.code} — {e.read().decode()}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("🔍 Cerco l'ultimo tag report...")
    last_tag = get_last_report_tag()
    print(f"   Ultimo tag: {last_tag or 'nessuno — uso gli ultimi 7 giorni'}")

    print("📂 Cerco changelog modificati...")
    changed_files = get_changed_changelog_files(last_tag)

    if not changed_files:
        print("✅ Nessun changelog modificato questa settimana. Nessun post inviato.")
        return

    print(f"   Trovati: {changed_files}")

    changelogs_data = []
    for filepath in changed_files:
        if os.path.exists(filepath):
            full_content = open(filepath).read()
            # Parsifica solo le righe AGGIUNTE dal diff → evita di ripubblicare entry vecchie
            diff_content = get_new_lines_from_diff(filepath, last_tag)
            entries = parse_entries(diff_content)
            print(f"   📄 {filepath} → {len(entries)} entry nuove trovate")
            if not entries:
                preview = "\n".join(diff_content.splitlines()[:20])
                print(f"   ⚠️  Nessuna entry nel diff. Anteprima diff:\n{preview}\n")
            changelogs_data.append({
                "filepath": filepath,
                "content": full_content,
                "meta": parse_frontmatter(full_content),
                "entries": entries,
            })
        else:
            print(f"⚠️  File non trovato: {filepath}")

    if not changelogs_data:
        print("❌ Nessun file leggibile. Esco.")
        return

    # Messaggio 1 — Report strutturato Block Kit
    print("📤 Invio report strutturato su Slack...")
    post_to_slack(build_weekly_report_blocks(changelogs_data))
    print("   ✅ Report settimanale inviato")

    # Messaggi 2+ — Post per componente
    print("🤖 Chiamo Claude per i post per componente...")
    result = call_claude(changelogs_data)
    for item in result.get("component_posts", []):
        post_to_slack({"text": item["post"]})
        print(f"   ✅ Post inviato: {item['component']}")

    print("🏷️  Creo tag report...")
    tag = create_report_tag()
    print(f"   ✅ Tag creato: {tag}")
    print("🎉 Report completato.")


if __name__ == "__main__":
    main()
