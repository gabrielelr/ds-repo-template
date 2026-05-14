# SCHEMA — Documentazione design system

Questo documento definisce la struttura della documentazione per ogni componente di un design system gestito con questo sistema. È il riferimento per chiunque scriva, legga o processi la documentazione: team UX, team DS, script automatici, agenti LLM.

Tutte le regole qui descritte sono **vincolanti**. Una documentazione che non rispetta lo schema non viene processata correttamente dagli strumenti automatici (pipeline di conversione, generazione `index.json`, modalità di chat e check).

---

## 1. Struttura cartelle

Ogni componente vive in una cartella sotto `components/`, identificata dal proprio slug.

```
components/
└── {slug}/
    └── docs/
        ├── metadata.json          Obbligatorio
        ├── rationale-note.md      Obbligatorio
        ├── changelog.md           Obbligatorio (sincronizzato da Changelog Master)
        └── images/                Obbligatoria, può essere vuota
            └── *.png
```

**Regole.**

- I nomi dei file sono fissi e case-sensitive: `metadata.json`, `rationale-note.md`, `changelog.md`.
- Tutti i file esistono sempre, anche per i componenti in stato `scaffold`.
- La cartella `images/` esiste sempre. Se vuota, contiene un file `.gitkeep` per essere versionata da Git.
- Niente sottocartelle dentro `docs/` oltre a `images/`.
- Il file `changelog.md` non viene mai modificato a mano: è sincronizzato automaticamente dal plugin Changelog Master di Figma (vedi sezione 4).

**File aggiuntivi consentiti** (non gestiti dagli script automatici, ma utili al team):

- `notes.md` — appunti interni del team UX, non parte della documentazione pubblica
- Sotto-cartelle dentro `images/` (es. `images/light/`, `images/dark/`) se servono varianti tematiche

---

## 2. Convenzione slug

Lo slug è l'identificativo "tecnico" del componente, usato come nome cartella e come chiave nei JSON.

**Regole di derivazione dal nome leggibile.**

1. Tutto minuscolo
2. Spazi sostituiti da trattini singoli (`-`)
3. Niente caratteri speciali, accenti o simboli (no `&`, `'`, `/`, `.`, `:`)
4. Niente prefissi, suffissi o numeri all'inizio dello slug
5. Numeri di versione/ordine vanno in fondo
6. Sigle si scrivono attaccate, senza trattini interni

**Tabella esempi.**

| Nome leggibile      | Slug                | Note                              |
|---------------------|---------------------|-----------------------------------|
| Button              | `button`            | Caso base                         |
| Bottom Sheet        | `bottom-sheet`      | Spazi → trattino                  |
| Form Field          | `form-field`        |                                   |
| H1 Heading          | `heading-h1`        | Numero in fondo, non all'inizio   |
| CTA Button          | `cta-button`        | Sigla attaccata                   |
| List Item Compact   | `list-item-compact` |                                   |
| Tab Bar             | `tab-bar`           |                                   |
| Icon Button         | `icon-button`       |                                   |
| Modal/Dialog        | `modal`             | Slash rimosso, scelto un solo nome |

**Casi limite e aliases.**

Quando un componente ha nomi commerciali specifici del cliente, nomi storici diversi tra loro, o varianti che potrebbero essere confuse con altri componenti, si usa il file `aliases.json` alla radice della repo.

`aliases.json` mappa nomi alternativi al loro slug canonico:

```json
{
  "Botton": "button",
  "Action Button": "button",
  "Foglio Inferiore": "bottom-sheet"
}
```

Lo script di estrazione del node tree (in fase di check) consulta `aliases.json` per normalizzare i nomi che trova in Figma verso lo slug corretto.

---

## 3. `rationale-note.md` — Perché è così

Risponde alle domande: *"Perché è progettato in questo modo? Quali decisioni di design ci sono dietro? Quali eccezioni esistono?"*

**Frontmatter.**

```yaml
---
slug: button
component: Button
lastUpdated: 2026-05-09
status: full
---
```

| Campo         | Tipo   | Valori ammessi                                           |
|---------------|--------|----------------------------------------------------------|
| `slug`        | string | Slug del componente, conforme alla sezione 2             |
| `component`   | string | Nome leggibile del componente                            |
| `lastUpdated` | string | Data ISO `YYYY-MM-DD` dell'ultima modifica significativa |
| `status`      | enum   | `full` o `scaffold`                                      |

Campi opzionali: `version` (semver), `author`, `reviewer`.

**Sezioni interne.**

- `## Decisioni di design` — perché certe scelte sono state fatte
- `## Eccezioni` — casi in cui il componente si discosta dalle regole standard del DS
- `## Note storiche` — evoluzione del componente, deprecazioni, migrazioni
- `## Componenti correlati` — link ad altri componenti che interagiscono con questo, con relazione esplicita ("usato dentro X", "alternativa a Y", "compone Z")

**Regola.** Questo file è il più "discorsivo". Serve sia ai designer (per capire il *perché*) sia agli LLM (per disambiguare casi d'uso simili a partire dal contesto storico/progettuale).

---

## 4. `changelog.md` — Storico delle modifiche del componente

Il file `changelog.md` traccia l'evoluzione del componente nel tempo: nuove varianti, modifiche comportamentali, fix, deprecazioni. È sincronizzato automaticamente dal plugin **Changelog Master** di Figma e non va mai modificato a mano.

**Workflow di aggiornamento.**

1. Il team DS modifica il componente direttamente in Figma (nuova variante, modifica di proprietà, deprecazione)
2. All'interno del plugin Changelog Master, il team DS registra la modifica indicando tipo, descrizione, autore ed eventuale progetto/revisore
3. La modifica entra nella **Sync Queue** del plugin, dove può essere ancora corretta o cancellata prima dell'invio
4. Al sync, il plugin scrive l'aggiornamento al file `components/{slug}/docs/changelog.md` della repo, in append rispetto allo storico precedente, e aggiorna il campo `last_updated` del frontmatter
5. Eventuali documenti correlati (`rationale-note.md`, `metadata.json`) vanno aggiornati a mano dal team UX se la modifica impatta la documentazione

Il path template del plugin è configurabile dalle impostazioni; per questa repo è `components/{component}/docs/changelog.md`, dove `{component}` viene risolto sostituendo lo slug del frame Figma (es. `"Icon Button"` → `"icon-button"`).

**Formato del file.**

Il file inizia con un frontmatter YAML che identifica il componente, seguito da un'entry per ogni data in cui sono state registrate modifiche. Le entry sono raggruppate sotto un heading data nel formato `### DD/MM/YYYY` e ordinate cronologicamente in ordine inverso (la più recente in alto). Esempio reale prodotto dal plugin:

```markdown
---
component: Checkbox
figma_id: ""
last_updated: 2026-04-27
---

### 27/04/2026
- **Updated** · Aggiunto lo stato error disabled in quanto questa casistica capita in Full responsive durante la selezione delle scommesse — *Gabriele La Rosa* · Alessandra Saccani
- **New** · Il componente è stato aggiunto al design system — *Gabriele La Rosa*
```

**Frontmatter.**

| Campo          | Tipo   | Note                                                                                |
|----------------|--------|-------------------------------------------------------------------------------------|
| `component`    | string | Nome leggibile del componente                                                       |
| `figma_id`     | string | ID del nodo Figma associato (può essere stringa vuota se non risolto)               |
| `last_updated` | string | Data ISO `YYYY-MM-DD` dell'ultima entry registrata; aggiornata in automatico al sync |

**Formato di una entry.**

```
- **{Tipo}** · {descrizione} — *{autore}* · {progetto}
```

- `{Tipo}` — categoria della modifica scelta nel plugin (es. `New`, `Updated`); la lista esatta dipende dalla versione del plugin Changelog Master
- `{descrizione}` — testo libero che spiega cosa è cambiato e perché
- `{autore}` — chi ha effettuato la modifica in Figma (auto-compilato dal plugin con `figma.currentUser.name`), in corsivo
- `{progetto}` — opzionale, separato da `·`; reso opzionale dal flag "Fix team DS" del plugin per modifiche interne di manutenzione

**Regole.**

- Il file è gestito esclusivamente dal plugin Changelog Master: non va mai modificato a mano, nemmeno per correggere refusi nelle entry esistenti (vanno corretti dall'edit in-place del plugin).
- Le entry sono ordinate cronologicamente in ordine inverso (data più recente in alto).
- Il sync per componente è indipendente: se il sync di un componente fallisce, gli altri proseguono — solo gli hash delle righe scritte con successo vengono marcati come sincronizzati.
- Il file viene letto dagli strumenti automatici per:
  - Aggiornare il campo `lastUpdated` nei `metadata.json` quando rileva un nuovo cambiamento
  - Generare il report settimanale Slack via GitHub Action (diff sui changelog modificati dall'ultimo tag `report-*`)
  - Fornire contesto storico all'LLM nella modalità Chiedi (es. *"questa variante esiste da febbraio 2026"*)

**Cosa NON va nel changelog.**

- Modifiche alla documentazione (typo, riformulazioni): vanno tracciate dai commit Git della repo, non dal changelog
- Cambiamenti di solo layout in Figma che non modificano il comportamento o le proprietà del componente
- Esperimenti o varianti in working session non promosse nel DS ufficiale

---

## 5. Struttura del `metadata.json`

Il `metadata.json` è la fonte di verità strutturata per ogni componente. Contiene tutte le informazioni su cosa è il componente, quando usarlo, come si comporta e come è composto. È quello che alimenta il sistema di check di aderenza, la generazione dell'`index.json` e il contesto caricato dall'LLM per rispondere alle domande sul DS.

Lo schema del `metadata.json` segue esattamente il formato della skill **AI Component Metadata** (`skills/ai-component-metadata`), con l'aggiunta di tre campi di repo-level (`slug`, `lastUpdated`, `status`) necessari per il tooling automatico.

**Schema di riferimento completo.**

```json
{
  "slug": "button",
  "lastUpdated": "2026-05-09",
  "status": "full",

  "component": {
    "name": "Button",
    "category": "atoms",
    "description": "Interactive element for triggering user actions",
    "type": "interactive"
  },

  "usage": {
    "useCases": [
      "primary-actions",
      "form-submission",
      "navigation-triggers",
      "dialog-confirmations"
    ],
    "requiredProps": [],
    "commonPatterns": [
      {
        "name": "primary-action",
        "description": "Azione principale di una schermata o flusso",
        "composition": "<Button variant=\"solid_primary\"><Button.Text>Conferma</Button.Text></Button>"
      },
      {
        "name": "secondary-action",
        "description": "Azione alternativa o di annullamento",
        "composition": "<Button variant=\"outline_default\"><Button.Text>Annulla</Button.Text></Button>"
      }
    ],
    "antiPatterns": [
      {
        "scenario": "multiple-primary-buttons",
        "reason": "Confuses user decision-making and visual hierarchy",
        "alternative": "Use one primary button, others as secondary or tertiary"
      }
    ]
  },

  "composition": {
    "slots": {
      "Text": {
        "required": false,
        "description": "Button label text"
      },
      "Icon": {
        "required": false,
        "description": "Icon element for visual enhancement"
      }
    },
    "nestedComponents": ["Button.Text", "Button.Icon"],
    "commonPartners": ["Form", "Card", "Modal", "Dialog"],
    "parentConstraints": []
  },

  "behavior": {
    "states": ["default", "hover", "pressed", "focused", "disabled", "loading"],
    "interactions": {
      "click": "Executes primary action",
      "hover": "Shows interactive state",
      "focus": "Keyboard focus indicator",
      "space": "Activates when focused",
      "enter": "Activates when focused"
    },
    "responsive": {
      "mobile": "Full width in narrow containers",
      "tablet": "Adapts to container width",
      "desktop": "Inline with auto width"
    }
  },

  "accessibility": {
    "role": "button",
    "keyboardSupport": "Full keyboard navigation with Space/Enter activation",
    "screenReader": "Announces button label and state",
    "focusManagement": "Visible focus ring, follows focus order",
    "wcag": "AA"
  },

  "aiHints": {
    "priority": "high",
    "keywords": ["button", "action", "click", "submit", "cta", "trigger"],
    "context": "Use for any interactive action that changes state or triggers behavior"
  }
}
```

**Campi di repo-level** (non presenti nella skill, necessari per il tooling).

| Campo         | Tipo   | Obbligatorio | Note                                                     |
|---------------|--------|--------------|----------------------------------------------------------|
| `slug`        | string | Sì           | Identificativo tecnico, conforme alla sezione 2          |
| `lastUpdated` | string | Sì           | ISO `YYYY-MM-DD` dell'ultima modifica significativa      |
| `status`      | enum   | Sì           | `full` o `scaffold`                                      |

**Campi della skill** (struttura completa documentata in `skills/ai-component-metadata/SKILL.md`).

| Campo                            | Tipo            | Obbligatorio | Note                                                                 |
|----------------------------------|-----------------|--------------|----------------------------------------------------------------------|
| `component.name`                 | string          | Sì           | Nome leggibile del componente                                        |
| `component.category`             | enum            | Sì           | `atoms`, `molecules`, `organisms`                                    |
| `component.description`          | string          | Sì se `full` | Descrizione breve in 1 frase                                         |
| `component.type`                 | enum            | Sì           | `interactive`, `display`, `container`, `input`, `navigation`        |
| `usage.useCases[]`               | array di string | Sì se `full` | Casi d'uso semantici, almeno 1 per componenti `full`                 |
| `usage.requiredProps[]`          | array di string | No           | Props obbligatorie da passare sempre                                 |
| `usage.commonPatterns[]`         | array di object | No           | Pattern d'uso comuni con `name`, `description`, `composition`        |
| `usage.antiPatterns[]`           | array di object | No           | Con `scenario`, `reason`, `alternative`                              |
| `composition.slots`              | object          | No           | Slot/subcomponenti con `required` e `description`                    |
| `composition.nestedComponents[]` | array di string | No           | Componenti figli usati internamente                                  |
| `composition.commonPartners[]`   | array di string | No           | Componenti con cui viene spesso combinato                            |
| `composition.parentConstraints[]`| array di string | No           | Vincoli di posizionamento                                            |
| `behavior.states[]`              | array di string | No           | Stati interattivi supportati                                         |
| `behavior.interactions`          | object          | No           | Chiave → descrizione comportamento (click, hover, focus, space…)    |
| `behavior.responsive`            | object          | No           | Chiavi: `mobile`, `tablet`, `desktop`. Valore: stringa descrittiva  |
| `accessibility.role`             | string          | No           | Ruolo ARIA                                                           |
| `accessibility.keyboardSupport`  | string          | No           | Descrizione del supporto keyboard                                    |
| `accessibility.screenReader`     | string          | No           | Comportamento con screen reader                                      |
| `accessibility.focusManagement`  | string          | No           | Strategia di gestione del focus                                      |
| `accessibility.wcag`             | string          | No           | Livello WCAG (`AA`, `AAA`)                                           |
| `aiHints.priority`               | enum            | No           | `high`, `medium`, `low`                                              |
| `aiHints.keywords[]`             | array di string | No           | Keyword che triggerano l'uso di questo componente                    |
| `aiHints.context`                | string          | No           | Quando l'AI deve scegliere questo componente                         |

---

## 6. Naming delle immagini

Le immagini in `components/{slug}/docs/images/` seguono un naming convenzionale che permette agli script di identificarle automaticamente.

**Formato base.**

```
{slug}-{variant?}-{do|dont}-{n}.{ext}
```

Dove:

- `{slug}` — slug del componente (sempre presente)
- `{variant}` — nome della variante (opzionale, ometti se l'immagine non è specifica di una variante)
- `do|dont` — indica se l'immagine mostra un esempio corretto (`do`) o un anti-pattern (`dont`)
- `{n}` — numero progressivo (1, 2, 3...) per distinguere più immagini dello stesso tipo
- `{ext}` — estensione del file: `png` (preferito), `jpg`, `webp`

**Esempi.**

```
button-primary-do-1.png       → Button variante primary, esempio corretto #1
button-primary-dont-1.png     → Button variante primary, anti-pattern #1
button-do-1.png               → Button generico, esempio corretto #1
bottom-sheet-do-1.png         → Bottom Sheet generico, esempio corretto #1
modal-confirmation-dont-2.png → Modal variante confirmation, anti-pattern #2
```

**Specifiche tecniche.**

- Risoluzione minima: 800px sul lato lungo
- Formato preferito: PNG su sfondo trasparente o sfondo che riproduce la canvas reale
- Peso massimo per file: 500 KB (oltre, comprimere o ridurre risoluzione)
- Nessun watermark, nessuna annotazione visiva sovrapposta — le note vanno nel testo del `rationale-note.md`

**Riferimenti alle immagini nel testo.**

Ogni immagine Do/Don't presente in `images/` deve essere referenziata e descritta nel `metadata.json` (in `usage.antiPatterns` o `usage.useCases`) oppure in `rationale-note.md`. Un'immagine senza descrizione testuale è invisibile all'LLM.

---

## 7. File a livello di repo

Oltre alle cartelle dei singoli componenti, la repo contiene questi file alla radice:

| File              | Generato   | Scopo                                                                  |
|-------------------|------------|------------------------------------------------------------------------|
| `README.md`       | Manuale    | Introduzione alla repo e istruzioni di utilizzo                        |
| `SCHEMA.md`       | Manuale    | Questo documento                                                       |
| `WRITING-GUIDE.md`| Manuale    | Guida alla scrittura di `rationale-note.md` per il team UX             |
| `inventory.md`    | Manuale    | Inventario di tutti i componenti del DS, con stato di documentazione   |
| `aliases.json`    | Manuale    | Mappa di nomi alternativi → slug canonici                              |
| `index.json`      | Automatico | Indice strutturato di tutti i componenti, generato dalla GitHub Action |

`index.json` viene rigenerato a ogni push su `main` da una GitHub Action. Non va mai modificato a mano.

---

## 8. Stato `scaffold` vs `full`

Un componente in stato `scaffold` ha la struttura prevista dallo schema ma il contenuto è incompleto. Serve a tracciare nell'inventario quali componenti sono ancora da documentare in profondità.

**Cosa deve esserci in un componente `scaffold`.**

- Tutti i file (`metadata.json`, `rationale-note.md`, `changelog.md`) esistono
- Il frontmatter di `rationale-note.md` è compilato
- Il `metadata.json` contiene i campi di repo-level (`slug`, `lastUpdated`, `status: scaffold`) e i campi della skill (`component.name`, `component.category`, `component.type`) con gli array `useCases` e `antiPatterns` vuoti
- Il `changelog.md` contiene **solo il frontmatter YAML** (`component`, `figma_id`, `last_updated`); il plugin Changelog Master appende le entry quando il team DS registra le prime modifiche

**Cosa deve esserci in più in un componente `full`.**

- `metadata.json` completamente compilato, inclusi `component.description`, almeno 1 `useCases[]`, `behavior` e `accessibility`
- `rationale-note.md` compilato con contenuto reale, niente TODO residui
- Idealmente almeno 1 elemento in `usage.antiPatterns[]`
- Le immagini Do/Don't sono presenti e referenziate nel testo

**Transizione da scaffold a full.**

Quando un componente viene completato:

1. Compilare tutti i campi mancanti di `metadata.json` e di `rationale-note.md`
2. Aggiornare `status: scaffold` → `status: full` nel JSON e nel frontmatter del Markdown
3. Aggiornare `lastUpdated` con la data corrente
4. Eseguire la pipeline di conversione per validare la consistenza
5. Commit con messaggio convenzionale: `docs({slug}): promote to full`

---

## 9. Versioning dello schema

Questo schema può evolvere. Quando viene modificato in modo non retrocompatibile (campi obbligatori aggiunti, campi rinominati, struttura cambiata), va incrementata la versione dello schema e va comunicata la modifica.

La versione corrente dello schema è documentata qui:

```
SCHEMA_VERSION: 2.0
```

In caso di modifiche, aggiornare la versione e aggiungere una nota nel `CHANGELOG.md` della repo template.

---

*SCHEMA v2.1 — Schema `metadata.json` allineato alla skill AI Component Metadata (`skills/ai-component-metadata`). La struttura JSON segue esattamente il formato della skill; i soli campi aggiuntivi sono `slug`, `lastUpdated` e `status` (necessari per il tooling della repo).*
