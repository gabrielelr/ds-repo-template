# CLAUDE.md — Regole e processo per la doc-repo del Design System

> Questo file viene caricato automaticamente da Claude Code (e da qualsiasi LLM che apre la repo) all'inizio di ogni sessione di lavoro su questo progetto. Le regole qui sono **vincolanti** — non opzionali.
>
> **Per i mantainer del template:** sostituisci i placeholder `<...>` (es. `<nome del tuo DS>`, `<target platform>`) con i valori specifici del tuo progetto prima di considerare attiva questa guida.

---

## Cos'è questa repo

Knowledge base del **Design System `<nome del tuo DS>`**, target platform `<es. mobile-native iOS / Android>`. Non contiene codice runtime — è documentazione strutturata, machine-readable, scritta perché un LLM possa:

1. **Comporre schermate** rispettose delle regole del DS
2. **Rispondere a domande** sui componenti, varianti, regole
3. **Fare review** di schermate (Figma o codice) verificando aderenza

---

## Ordine di lettura per un LLM (DA SEGUIRE)

Quando avvii una sessione su questa repo, **leggi i file in questo ordine** prima di fare qualsiasi cosa:

1. **Questo file (`CLAUDE.md`)** — regole e processo (lo stai leggendo)
2. **`index.toon`** — overview di tutti i componenti in ~4k token (slug, name, type, status, useCases, antiPattern aggregati, dependency graph). **Per la maggior parte delle domande sul DS questo basta.** Aprilo come secondo file, sempre.
3. **`SCHEMA.md`** — schema del `metadata.json` dei componenti (solo se devi creare/modificare un componente)
4. **`page-patterns/SCHEMA-PATTERN.md`** — schema del `composition.json` dei page-pattern
5. **`page-patterns/README.md`** — indice di tutti i page-pattern disponibili
6. **Il `pattern.md` + `composition.json` del page-pattern coinvolto** — SOLO quando devi comporre/recensire una schermata di una specifica tipologia
7. **I `metadata.json` dei singoli componenti coinvolti** — SOLO se hai bisogno di dettagli che `index.toon` non contiene (composition completa, behavior states, accessibility, rationale)

**Regola di efficienza.** `index.toon` è generato automaticamente da `scripts/build_index.py` ad ogni push e aggrega i campi essenziali di tutti i `metadata.json`. Non leggere i metadata individualmente per rispondere a domande di overview ("esiste il componente X?", "quali sono gli antiPattern di Y?", "quali componenti compongono Z?") — `index.toon` ha già quelle risposte. Apri il `metadata.json` del singolo solo per dettagli profondi.

---

## Regole core (non negoziabili)

### R1 — Figma è source of truth

Documenta SOLO quello che è realmente in Figma. **Non inventare** stati, varianti, slot, o "comportamenti standard" che pensi un componente dovrebbe avere. Se non è in Figma, non esiste nel DS. *Why:* la documentazione che descrive cose non esistenti porta a generazioni sbagliate.

### R2 — Token, mai hex

Se il DS è multibrand (più temi via build), nei metadata, nei pattern, nei commenti, e quando descrivi colori: **usa sempre il nome del token** (es. `button/color/brand/primary/bg/default`), **mai il valore hex risolto** (es. `#5fa747`). *Why:* gli hex sono validi solo per un brand alla volta — usarli rompe la portabilità.

### R3 — Non inventare designDecisions

Il campo `rationale.designDecisions` nei `metadata.json` **resta `""`** finché l'utente/designer non fornisce il razionale reale. *Why:* inventare razionali plausibili contamina la documentazione con motivazioni che il team non ha mai espresso.

### R4 — Rispetta il target di piattaforma

Definisci nei `metadata.json` (`platforms`) le piattaforme supportate e mantienile coerenti. Se ti viene chiesto qualcosa fuori target (es. desktop su un DS mobile-only), segnala il mismatch invece di adattare silenziosamente.

### R5 — Page-patterns sono il primo step per comporre / recensire

**Prima di comporre o recensire una schermata, identifica la sua page-type e apri `page-patterns/<slug>/`** (sia `pattern.md` per il contesto narrativo, sia `composition.json` per la slot map machine-readable). Questo è non opzionale.

I page-pattern dicono:
- Quali slot la pagina DEVE avere
- Quali slot la pagina NON PUÒ avere (e perché)
- Quali componenti sono validi per ogni slot
- Quali regole quantitative valgono (max 1 Primary, max 1 Card Highlight, ecc.)
- Quali anti-pattern specifici della page-type evitare

Se la page-type richiesta **non ha ancora un pattern documentato**, fermati e proponi di crearlo prima di procedere — non inventare la composizione.

### R6 — I page-pattern DEVONO essere descritti narrativamente (anti-allucinazione)

⚠️ **Critico.** Il `composition.json` da solo non basta. Ogni page-pattern DEVE avere un `pattern.md` che descrive in linguaggio naturale:

- **Quando usare** quel pattern (use case concreti)
- **Quando NON usarlo** (page-type alternative)
- **Perché ogni slot esiste** (razionale UX)
- **Perché certe regole sono come sono** (motivazione)
- **Esempi reali** (Figma node ID di implementazioni canoniche)

*Why:* uno schema strutturato senza contesto narrativo causa allucinazioni — l'LLM riempie i buchi con assunzioni plausibili ma sbagliate. La narrative descrive l'**intento**, lo schema solo i **vincoli**. Servono entrambi.

Quando crei o aggiorni un page-pattern, scrivi **prima** il `pattern.md` (narrative), **poi** il `composition.json` (struttura). Mai il contrario.

### R7 — Max 1 Button Primary per schermata

Una sola `Hierarchy=Primary` visibile per viewport. Le azioni concorrenti vanno `Secondary` o `Ghost`. La regola è di **schermata intera**, non di Button Group locale. *Source:* `components/<button-slug>/docs/metadata.json` antiPattern `multiple-primary-on-screen` (da definire nel tuo DS).

### R8 — Container del riferimento → Container del DS

Quando ricomponi una schermata di riferimento, **preserva la container hierarchy**: se il riferimento ha una card (container) che wrappa contenuto, usa un componente *container* del DS + display nested, MAI sostituire il container con il solo display flat. *Why:* il container porta semantica visiva (bordo, padding, raggruppamento) — sostituirlo con un display perde la struttura.

### R9 — `type` guida la scelta del componente

Ogni componente DS ha un `component.type` nel metadata: `container`, `display`, `interactive`, `input`, `navigation`. **Prima decidi il type che serve in ogni slot, poi scegli il componente concreto.** Mai usare un `display` dove serve un `container` o viceversa.

| `type` | Ruolo | Esempi tipici |
|---|---|---|
| `container` | wrap / struttura visiva di altri componenti | Card, Hero, Bottom Sheet, Modal, Accordion |
| `display` | contenuto visivo passivo (no interazione) | TextBox, Heading, Badge, Avatar, Divider, Loader |
| `interactive` | affordance d'azione utente | Button, Button Group, Button Icon, Chip, Toggle, Link |
| `input` | raccolta dati | TextField, Radio, Checkbox, Dropdown, Search Bar |
| `navigation` | chrome di pagina / sistema di navigazione | Header, Navbar, Tab Navigation, Page Navigation |

### R10 — Cerca template ready-to-use **prima** di comporre da atomi

Se esiste un template ready-to-use specifico per il contesto (es. `Card Product Grid Template - <vertical>`), **usalo come base** invece di costruire la struttura da atomi singoli. *Why:* i template di contesto incorporano già metadata, size, palette e gerarchia ottimali per quella vertical — comporre da atomi produce un mismatch sottile ma significativo.

---

## Processo: comporre una schermata

1. **Identifica la page-type** (detail / form / menu / homepage / bottom-sheet-modal / settings / listing / login / signup / …)
2. **Apri `page-patterns/<slug>/`**:
   - Leggi `pattern.md` per capire il contesto, le motivazioni, gli anti-pattern
   - Leggi `composition.json` per la slot map strutturata
   - Se il pattern non esiste, **fermati e segnalalo** all'utente (non inventarlo da zero)
3. **Per ogni slot del pattern**:
   - Verifica `required` / `forbidden` / `optional`
   - Identifica il `type` atteso (R9)
   - Scegli il componente concreto fra quelli ammessi in `slots[].components`
   - Se serve un container e non c'è un componente specifico, usa **una Card + display nested** (R8)
4. **Cerca template ready-to-use** se applicabile (R10)
5. **Verifica le regole quantitative** del pattern (`rules.maxPrimaryCTA`, ecc.) e le regole core (R7)
6. **Verifica gli anti-pattern** del pattern e dei singoli componenti coinvolti
7. **Componi via Figma MCP** (`use_figma` + `search_design_system`)
8. **Pre-flight finale** — vedi checklist sotto

---

## Processo: documentare un nuovo componente

Lo schema del `metadata.json` è definito dalla skill **`ai-component-metadata`** (in `skills/ai-component-metadata/`) — il nostro `SCHEMA.md` ne è la versione estesa con campi aggiuntivi (`figmaNodeIds`, `lastUpdated`, `platforms`, `status`, `content`). Usala come template di partenza.

Se i designer ti consegnano un frame Figma con la spec già scritta (template `Purpose & Usage` + `Behavior`), **la mappa univoca *sezione del frame → campo dello schema* è in [`SCHEMA.md` §5](SCHEMA.md)** — include anche la regola di riconoscimento template multi-DS (colonne app `iOS/Android/Liquid Glass` vs colonne web `Mobile/Desktop`) e i punti d'attenzione operativi.

1. **Fetch dati Figma**: `get_metadata`, `get_design_context`, `get_variable_defs`, `get_screenshot`
2. **Crea `components/<slug>/docs/metadata.json`**:
   - Se hai accesso a un componente in codice (`.tsx`): `python skills/ai-component-metadata/scripts/generate_metadata.py path/to/Component.tsx` come bootstrap, poi rifinisci con dati Figma
   - Se hai solo Figma: copia il template `skills/ai-component-metadata/assets/metadata-template.tsx` come riferimento di shape, poi compila manualmente seguendo `SCHEMA.md`
3. **Three-way naming**: slug kebab-case (`card-product`), frame Figma camelCase (`cardProduct`), namespace token camelCase (`cardProduct/*`)
4. **Vincoli da rispettare**: R1, R2, R3, R9 (`type` corretto)
5. **Aggiorna `changelog.md`** del componente con riga datata
6. **Validazione**: JSON parse + grep hex (nessun match)
7. **Se la regola è di pagina o cross-component** invece che di singolo componente → aggiornare il page-pattern corrispondente o questo file (CLAUDE.md), non solo il metadata del componente

---

## Processo: recensire una schermata

1. **Identifica la page-type** della schermata (osserva struttura, header, slot dominanti)
2. **Apri `page-patterns/<slug>/composition.json`** del pattern corrispondente
3. **Verifica ogni slot del pattern**: presente se `required`, assente se `forbidden`, componente corretto se ammesso
4. **Verifica le regole** del pattern (max Primary, max Card Highlight, ecc.)
5. **Verifica gli anti-pattern** del pattern e dei componenti
6. **Verifica le regole core** (R1–R10)
7. **Output del report**:
   - ✅ Cosa è conforme
   - ❌ Violazioni (regola fonte + alternativa proposta)
   - ⚠️ Da verificare (gap di documentazione)
   - 📚 Discrepanze doc vs design

---

## Pre-flight checklist (PRIMA di generare/recensire)

- [ ] Ho identificato la page-type e letto il `page-patterns/<slug>/pattern.md` + `composition.json` corrispondente?
- [ ] Se il pattern non esiste, ho fermato il task e lo sto segnalando?
- [ ] Quanti Button `Hierarchy=Primary` visibili? → **Max 1**
- [ ] Quante Card Highlight? → **Max 1 per pagina**
- [ ] Quante Card Entrypoint? → **Max 1 per layout**
- [ ] Tutti i colori via token name, mai hex?
- [ ] Coerente con il target di piattaforma del DS?
- [ ] Radio per single-select, Checkbox per multi-select?
- [ ] Per ogni slot, il `type` del componente è coerente col ruolo compositivo?
- [ ] Se ricomponi, ogni container del riferimento → container DS (no flatten)?
- [ ] Se la page-type ha un template ready-to-use, l'ho usato come base?

> **Mantainer:** aggiungi qui le checkbox specifiche del tuo DS (regole su Header, Button Group, balance trailing, ecc.) man mano che le consolidi.

---

## Quando questa guida non basta

Per qualcosa non coperto qui:
1. `page-patterns/<slug>/pattern.md` per il contesto della page-type
2. `components/<slug>/docs/metadata.json` (sezione `usage.antiPatterns`, `composition.parentConstraints`)
3. **Se manca proprio**: chiedi all'utente, non inventare

Quando scopri una regola nuova che dovrebbe vivere qui (perché è cross-component) o in un page-pattern (perché è specifica di una page-type): **aggiungila al file appropriato** prima di considerare chiuso il task.
