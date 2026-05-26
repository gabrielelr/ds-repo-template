---
slug: _example
name: Example Page Pattern
status: scaffold
lastUpdated: ""
---

# Example Page Pattern

> **Scaffold neutro.** Duplica questa cartella (`cp -r _example <new-slug>`) come punto di partenza per un nuovo page-pattern e compila ogni sezione qui sotto.

## Quando usare

Descrivi gli use case concreti per cui questo pattern è appropriato. Esempi: "pagina dettaglio prodotto", "form di onboarding", "modal di conferma azione distruttiva".

## Quando NON usare

Elenca le page-type alternative che sembrano simili ma che richiedono un pattern diverso, spiegando il motivo della distinzione.

## Slot e razionale

Per ogni slot definito in `composition.json`, spiega **perché esiste** (non solo "esiste"). Es. "Il `header` è obbligatorio perché l'utente arriva qui da deep-link e ha bisogno di un punto di orientamento immediato".

## Regole e motivazioni

Per ogni regola in `rules` di `composition.json`, spiega il motivo:
- *maxPrimaryCTA: 1* — perché due primary su una pagina dettaglio competono per l'attenzione e diluiscono la conversione.
- *maxCardHighlight: 1* — …

## Anti-pattern

Lista anti-pattern **reali** osservati (non ipotetici): cosa è andato storto in passato e perché è proibito ora.

| Scenario | Reason | Alternative |
|---|---|---|
| `…` | … | … |

## Esempi canonici

Riferimenti a implementazioni Figma validate dall'UX team (con `figmaNodeId`):

- *Nome esempio* — `figmaNodeId` — note
