# Page Pattern Schema — `composition.json`

Schema strutturato per definire un **page-pattern** (macro-pattern di una tipologia di schermata: home, detail, form, menu, ecc.). Ogni page-pattern vive in `page-patterns/<slug>/` con tre file:

- `pattern.md` — narrative UX (razionale, when-to-use, when-NOT-to-use, anti-pattern)
- `composition.json` — definizione strutturata (slot, rules, examples) — **questo schema**
- `changelog.md` — storico delle modifiche

Lo scopo del `composition.json` è essere **machine-readable**: uno scorer automatico può leggerlo per validare le schermate generate, e gli agenti AI lo caricano come context per comporre schermate. **Va sempre accompagnato da `pattern.md`** (descrizione narrativa) — il solo schema senza contesto causa allucinazioni.

---

## Top-level fields

| Campo | Tipo | Required | Descrizione |
|---|---|---|---|
| `$schema` | string | ✓ | Riferimento allo schema, sempre `"../SCHEMA-PATTERN.md"` |
| `slug` | string | ✓ | Kebab-case identifier (es. `detail-product-game`) |
| `name` | string | ✓ | Nome human-readable in italiano |
| `status` | enum | ✓ | `scaffold` (skeleton) / `draft` (UX in lavorazione) / `full` (validato dall'UX team) |
| `ownedBy` | string | ✓ | Chi è responsabile del pattern (tipicamente `"UX team"`) |
| `lastUpdated` | string ISO date | ✓ | Data ultima modifica del pattern |
| `description` | string | ✓ | Breve overview di cosa fa questa pagina e quando si usa |
| `useCases` | string[] | ✓ | Lista di use case concreti (es. `["game detail", "product detail", "promo landing"]`) |
| `categories` | string[] | — | Tag di categoria (`detail`, `form`, `modal`, `error`, ecc.) |
| `platforms` | string[] | — | Piattaforme su cui si applica (`android`, `ios`, `ios-liquid-glass`) |
| `slots` | object | ✓ | Mappa slot → definizione (vedi sotto) |
| `rules` | object | ✓ | Regole quantitative del pattern (vedi sotto) |
| `antiPatterns` | array | — | Anti-pattern specifici della page-type |
| `commonPartners` | string[] | — | Altri pattern o componenti che si usano spesso insieme |
| `compositionExamples` | array | — | Lista di esempi Figma canonici |
| `rationale` | string | — | Razionale UX (può restare `""` finché non fornito) |

---

## `slots` — definizione

Ogni slot rappresenta una **posizione strutturale** della pagina (es. `header`, `hero`, `body`, `stickyFooter`, `fab`). Il valore è un oggetto con:

| Campo | Tipo | Default | Descrizione |
|---|---|---|---|
| `required` | bool | `false` | Lo slot DEVE essere presente. Mutuamente esclusivo con `forbidden`. |
| `forbidden` | bool | `false` | Lo slot NON può essere presente. Mutuamente esclusivo con `required`. |
| `optional` | bool | `false` | Esplicitamente opzionale (default se né required né forbidden). |
| `components` | string[] | `[]` | Slug dei componenti DS validi per questo slot (es. `["Card Detail", "Card Informative"]`). Lookup contro `components/<slug>/`. |
| `type` | enum | — | Atteso `type` del componente: `container` / `display` / `interactive` / `input` / `navigation`. |
| `variant` | string | — | Se richiesto, variant specifica (es. `"Inline, md, Sticky=True"` per Button Group). |
| `constraints` | string[] | `[]` | Vincoli testuali (es. `"max 1 Primary"`, `"Card Detail variant ∈ {caratteristiche di gioco, bonus, custom}"`). |
| `reason` | string | — | Se `forbidden: true`, motivo della proibizione. |
| `description` | string | — | Spiegazione narrative dello slot. |

### Slot canonici (convenzioni di naming)

Usare nomi consistenti per slot ricorrenti:

| Nome slot | Posizione | Tipico componente |
|---|---|---|
| `statusBar` | top OS chrome | Status Bar OS |
| `header` | top app chrome | Header (Top Navigation) |
| `hero` | top body, immersivo | Hero / Hero Detail |
| `quickActions` | sotto hero / userHeader | Square Button Group / Button Circle Navigation |
| `body` | main scrollable content | mix di container + display |
| `userHeader` | menu / account | TextBox "Ciao [Nome]" + Saldo |
| `stickyFooter` | bottom fixed | Button Group sticky |
| `fab` | floating overlay bottom-right | Filter Button, Button Icon Floating |
| `backdrop` | layer modale | Backdrop |
| `drawer` | modale dal basso | Bottom Sheet |
| `dragHandle` | top del drawer | Drag Handle |
| `bottomNav` | bottom system chrome | Navbar |
| `footer` | end of page | Footer regolatorio |

---

## `rules` — quantitative

Oggetto con vincoli numerici/booleani standard:

| Campo | Tipo | Descrizione |
|---|---|---|
| `maxPrimaryCTA` | int | Max numero di Button con `Hierarchy=Primary` visibili. Tipicamente `1`. |
| `maxCardHighlight` | int | Max Card Highlight (regola R7 di CLAUDE.md). Tipicamente `1` o `0`. |
| `maxCardEntrypoint` | int | Max Card Entrypoint. Tipicamente `1` o `0`. |
| `allowedNudgeCardHierarchy` | string[] | Hierarchy permesse per CTA di nudge card (`["Secondary", "Ghost"]` quando il page-type ha già una Primary altrove). |
| `customRules` | string[] | Regole free-text specifiche del pattern. |

---

## `antiPatterns` — array di oggetti

Stessa shape degli antiPatterns dei componenti:

```json
{
  "scenario": "<kebab-case identifier>",
  "reason": "...",
  "alternative": "..."
}
```

Distinzione importante: gli antiPatterns qui sono **specifici della page-type** (es. `header-in-detail` vive in `detail-product-game/composition.json#antiPatterns`), mentre gli regole core in `CLAUDE.md` (R1–R10) sono cross-component (es. `multiple-primary-on-screen`).

---

## `compositionExamples` — array di oggetti

Lista di implementazioni Figma canoniche del pattern. Usate come reference per gli scorer automatici e per l'agente AI come few-shot.

```json
{
  "name": "...",
  "figmaNodeId": "...",
  "figmaUrl": "...",
  "lastVerified": "YYYY-MM-DD",
  "notes": "..."  // optional
}
```

---

## Status flow

Come per i componenti:

- **`scaffold`** — solo skeleton (`slug`, `name`, top-level fields vuoti)
- **`draft`** — UX team sta scrivendo / iterando
- **`full`** — validato e approvato dall'UX team

Promozione `scaffold → draft` può farla chiunque (incluso AI agent). Promozione `draft → full` la fa solo l'UX team owner.

---

## Esempio completo

Vedi `page-patterns/_example/composition.json` per uno scaffold di partenza.

---

## Validazione

Uno script `scripts/validate_patterns.py` (da implementare) può validare che:

- JSON parse-able
- `slug` matcha il folder name
- `slots` ben formati (no `required + forbidden` simultanei)
- `components` referenziano slug esistenti in `components/`
- `compositionExamples[].figmaNodeId` ben formato
- `rules.max*` non negativi
- `type` ∈ enum

Run da CI / pre-commit hook.
