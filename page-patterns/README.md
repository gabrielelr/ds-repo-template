# `page-patterns/` — Macro-pattern per tipologia di schermata

Ogni cartella qui dentro è un **page-pattern**: un macro-pattern che definisce **come si compone una determinata tipologia di schermata** del DS. I page-pattern sono **owned dall'UX team** e descrivono regole, slot obbligatori/vietati, e composizioni canoniche per quella tipologia.

A differenza dei componenti (in `components/`) che documentano i singoli pezzi, i page-pattern documentano **come si assemblano** in una schermata coerente.

---

## ⚠️ Critico: i page-pattern DEVONO essere descritti narrativamente

Ogni pattern ha due file di contenuto: `composition.json` (struttura) e `pattern.md` (descrizione).

**Entrambi sono obbligatori. Non saltare `pattern.md`.**

Lo `composition.json` da solo elenca i vincoli quantitativi, ma **un LLM che legge solo i vincoli senza contesto allucina**: riempie i buchi con assunzioni plausibili ma sbagliate. Per esempio: rispetta `maxPrimaryCTA: 1` ma usa il componente nel contesto sbagliato perché "non sapeva" cosa rappresenta nella vertical.

Il `pattern.md` deve raccontare:

- **Quando usare** il pattern (use case concreti)
- **Quando NON usarlo** (page-type alternative)
- **Perché ogni slot esiste** (razionale UX, non solo "esiste")
- **Perché certe regole sono come sono** (motivazione, vincoli storici, lezioni imparate)
- **Esempi reali** con Figma node ID

> **Workflow obbligato per chi crea/aggiorna un pattern**:
> 1. **Prima** scrivi `pattern.md` (la narrative)
> 2. **Poi** compila `composition.json` (la struttura derivata dalla narrative)
>
> Mai il contrario. Mai solo lo schema.

---

## Perché esistono

Senza page-pattern strutturati:
- Gli agenti AI inventano composizioni "ragionevoli" che però violano regole non scritte (es. due Primary in dettaglio, Header in pagina immersiva, ecc.)
- Le regole di pagina vivono solo nella testa dei designer e in mockup sparsi → non scalano
- Lo scorer automatico (review di schermate) non ha un oracle machine-readable contro cui verificare aderenza

Con page-pattern strutturati:
- L'UX team possiede regole esplicite versionabili
- Gli agenti AI leggono `composition.json` come oracle
- Lo scorer automatico verifica conformità senza hardcode

---

## Struttura di un pattern

```
page-patterns/<slug>/
├── pattern.md          # narrative UX: when-to-use, when-NOT-to-use, ratio
├── composition.json    # definizione strutturata (machine-readable)
├── changelog.md        # storico modifiche
└── examples/           # screenshot/notes degli esempi (opzionale)
```

Schema del `composition.json` documentato in [`SCHEMA-PATTERN.md`](SCHEMA-PATTERN.md).

Uno scaffold neutro di partenza è in [`_example/`](_example/).

---

## Status flow

- **`scaffold`** — solo skeleton (`slug`, `name`, top-level fields vuoti)
- **`draft`** — UX team sta scrivendo / iterando
- **`full`** — validato e approvato dall'UX team

Promozione `scaffold → draft` può farla chiunque (incluso AI agent). Promozione `draft → full` la fa solo l'UX team owner.

---

## Come contribuire (UX team)

### Compilare un pattern esistente in `draft`

1. Apri `pattern.md` → scrivi razionale, when-to-use, when-NOT-to-use, anti-pattern reali (non quelli derivati per osservazione)
2. Apri `composition.json` → verifica slot, aggiungi `constraints`, completa `rules`, aggiungi `compositionExamples` reali con `figmaNodeId`
3. Compila `rationale` se hai un razionale UX consolidato
4. Aggiungi entry al `changelog.md` con la modifica
5. Promuovi `status` da `draft` a `full`

### Creare un pattern nuovo

1. `cp -r _example <new-slug>` come template di partenza
2. Aggiorna `slug`, `name`, `status: "scaffold"`, svuota i campi che non si applicano
3. Aggiungi alla tabella dell'indice (se ne mantieni uno locale)
4. Procedi come sopra

---

## Come usano i pattern gli agenti AI

Quando un agente AI deve comporre una schermata:

1. Identifica la **page-type** richiesta (detail / form / menu / homepage / …)
2. Apre `page-patterns/<slug>/composition.json` e lo carica come context
3. Genera la composizione rispettando:
   - Ogni slot `required: true` → presente
   - Ogni slot `forbidden: true` → assente
   - Ogni vincolo in `rules` rispettato
   - I componenti dello slot sono quelli in `components[]`
4. Verifica contro `antiPatterns` del pattern + regole globali del DS

---

## Come usa i pattern lo scorer di review

Lo scorer carica `composition.json` del pattern corrispondente alla page-type rilevata in una schermata Figma, e verifica per ogni regola pass/fail:

```python
# pseudo-code
pattern = json.load(f"page-patterns/{detected_page_type}/composition.json")
for slot_name, slot_def in pattern["slots"].items():
    if slot_def.get("required") and not screen_has_slot(slot_name):
        report.fail(f"Missing required slot: {slot_name}")
    if slot_def.get("forbidden") and screen_has_slot(slot_name):
        report.fail(f"Forbidden slot present: {slot_name} ({slot_def['reason']})")
for rule, expected in pattern["rules"].items():
    actual = screen_count_for_rule(rule)
    if not check_rule(rule, actual, expected):
        report.fail(f"Rule violation: {rule}, expected {expected}, got {actual}")
```

Zero hardcode dello scorer — tutta la logica è nei `composition.json`.

---

## Versionamento

Ogni `composition.json` cambia → entry obbligatoria in `changelog.md` con data + modifica + status flow. Stesso pattern dei componenti.

Es. `2026-05-22 — Aggiunto slot fab opzionale per FAB Filter.`
