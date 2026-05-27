# SCHEMA — Documentazione design system

Questo documento definisce la struttura della documentazione per ogni componente di un design system gestito con questo sistema. È il riferimento per chiunque scriva, legga o processi la documentazione: team UX, team DS, script automatici, agenti LLM.

Tutte le regole qui descritte sono **vincolanti**. Una documentazione che non rispetta lo schema non viene processata correttamente dagli strumenti automatici (pipeline di conversione, generazione `index.json`, modalità di chat e check).

> **Origine dello schema.** Le sezioni base del `metadata.json` (`component`, `usage`, `composition`, `behavior`, `accessibility`, `aiHints`) sono definite dalla skill **`ai-component-metadata`** (in `skills/ai-component-metadata/`). Questo file estende quello schema con campi specifici del progetto (`slug`, `lastUpdated`, `status`, `platforms`, `figmaNodeIds`, `content`, `rationale`). Per documentare un componente nuovo, parti dal template della skill (`skills/ai-component-metadata/assets/metadata-template.tsx`) e aggiungi i campi project-specific definiti qui.

---

## 1. Struttura cartelle

Ogni componente vive in una cartella sotto `components/`, identificata dal proprio slug.

```
components/
└── {slug}/
    └── docs/
        ├── metadata.json          Obbligatorio
        ├── changelog.md           Obbligatorio (sincronizzato da Changelog Master)
        └── images/                Obbligatoria, può essere vuota
            └── *.png
```

**Regole.**

- I nomi dei file sono fissi e case-sensitive: `metadata.json`, `changelog.md`.
- Tutti i file esistono sempre, anche per i componenti in stato `scaffold`.
- La cartella `images/` esiste sempre. Se vuota, contiene un file `.gitkeep` per essere versionata da Git.
- Niente sottocartelle dentro `docs/` oltre a `images/`.
- Il file `changelog.md` non viene mai modificato a mano: è sincronizzato automaticamente dal plugin Changelog Master di Figma (vedi sezione 3).

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

## 3. `changelog.md` — Storico delle modifiche del componente

Il file `changelog.md` traccia l'evoluzione del componente nel tempo: nuove varianti, modifiche comportamentali, fix, deprecazioni. È sincronizzato automaticamente dal plugin **Changelog Master** di Figma e non va mai modificato a mano.

**Workflow di aggiornamento.**

1. Il team DS modifica il componente direttamente in Figma (nuova variante, modifica di proprietà, deprecazione)
2. All'interno del plugin Changelog Master, il team DS registra la modifica indicando tipo, descrizione, autore ed eventuale progetto/revisore
3. La modifica entra nella **Sync Queue** del plugin, dove può essere ancora corretta o cancellata prima dell'invio
4. Al sync, il plugin scrive l'aggiornamento al file `components/{slug}/docs/changelog.md` della repo, in append rispetto allo storico precedente, e aggiorna il campo `last_updated` del frontmatter
5. Eventuali campi correlati nel `metadata.json` (es. il blocco `rationale`) vanno aggiornati a mano dal team UX se la modifica impatta la documentazione

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

## 4. Struttura del `metadata.json`

Il `metadata.json` è la fonte di verità strutturata per ogni componente. Contiene tutte le informazioni su cosa è il componente, quando usarlo, come si comporta, come è composto e **perché** è progettato così. È quello che alimenta il sistema di check di aderenza, la generazione dell'`index.json` e il contesto caricato dall'LLM per rispondere alle domande sul DS.

Lo schema del `metadata.json` segue il formato della skill **AI Component Metadata** (`skills/ai-component-metadata`), con l'aggiunta di campi specifici della repo: tre campi di repo-level (`slug`, `lastUpdated`, `status`) per il tooling automatico, e il blocco `rationale` per le decisioni di design e il contesto storico/progettuale del componente.

**Schema di riferimento completo.**

```json
{
  "slug": "button",
  "lastUpdated": "2026-05-09",
  "status": "full",

  "platforms": ["android", "ios", "ios-liquid-glass"],
  "figmaNodeIds": {
    "android": "5473:10855",
    "ios": "5473:10855",
    "ios-liquid-glass": "8354:2516"
  },

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
        "composition": "<Button variant=\"solid_primary\"><Button.Text>Conferma</Button.Text></Button>",
        "images": ["1.1"]
      },
      {
        "name": "secondary-action",
        "description": "Azione alternativa o di annullamento",
        "composition": "<Button variant=\"outline_default\"><Button.Text>Annulla</Button.Text></Button>",
        "images": ["1.2"]
      }
    ],
    "antiPatterns": [
      {
        "scenario": "multiple-primary-buttons",
        "reason": "Confuses user decision-making and visual hierarchy",
        "alternative": "Use one primary button, others as secondary or tertiary",
        "images": ["2.1"]
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

  "content": {
    "maxLines": { "label": 1 },
    "characterLimits": { "label": 20 },
    "overflow": "ellipsis",
    "rules": [
      "Button label: max 20 characters, always 1 line",
      "If label exceeds 20 chars, truncate with ellipsis instead of wrapping"
    ]
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
  },

  "rationale": {
    "designDecisions": "- Il padding usa token `spacing-3` per coerenza touch (decisione validata in user testing Q1 2026, vedi [1.1]).\n- Lo stato `loading` sostituisce il testo con uno spinner per mantenere stabile l'hit area.\n- La variante `ghost` è stata rimossa a febbraio 2026 dopo che la ricerca ha mostrato bassa discoverability (vedi [3.1])."
  }
}
```

**Campi aggiuntivi della repo** (non presenti nella skill, necessari per il tooling e la documentazione).

| Campo           | Tipo            | Obbligatorio | Note                                                                                       |
|-----------------|-----------------|--------------|--------------------------------------------------------------------------------------------|
| `slug`          | string          | Sì           | Identificativo tecnico, conforme alla sezione 2                                            |
| `lastUpdated`   | string          | Sì           | ISO `YYYY-MM-DD` dell'ultima modifica significativa                                        |
| `status`        | enum            | Sì           | `full` o `scaffold`                                                                        |
| `platforms`     | array di string | Sì           | OS supportati. Valori ammessi: `"android"`, `"ios"`, `"ios-liquid-glass"`. Per scaffold: `[]`. Vedi tabella sotto. |
| `figmaNodeIds`  | object          | Sì           | Mappa platform → ID nodo Figma della variante. Chiavi devono combaciare con `platforms[]`. Quando piattaforme condividono lo stesso nodo, ripetere l'ID esplicitamente. Per scaffold: `{}`. |
| `figmaLayouts`  | object          | No           | Solo se il componente ha più frame Figma per varianti di **layout/placement** (es. Alert `sticky` vs `inline`). Mappa `layoutName` → ID nodo Figma. Le chiavi sono libere, lowercase, kebab-case (`sticky`, `inline`, `top-sheet`, `bottom-sheet`…). Quando presente, ogni `usage.commonPatterns[]` può aggiungere il campo opzionale `layout` con il nome del layout di riferimento. |
| `rationale`     | object          | Sì           | Blocco "Perché è così" — contiene il solo campo `designDecisions`                          |

**Valori ammessi per `platforms[]`.**

| Valore              | Significato                                                                                  |
|---------------------|----------------------------------------------------------------------------------------------|
| `android`           | Versione Android (Material o pattern custom su Android)                                      |
| `ios`               | Versione iOS pre-Liquid Glass (HIG classico o pattern custom su iOS)                         |
| `ios-liquid-glass`  | Versione iOS con linguaggio Liquid Glass — trattata come platform separata, non come variante di `ios` |

Quando un componente esiste su tutte e tre, va elencato in tutte e tre le chiavi di `figmaNodeIds`. Componenti single-platform (es. esclusivi di Liquid Glass) hanno `platforms` e `figmaNodeIds` con una sola chiave.

**Esempio con `figmaLayouts`** (componente con più frame di layout, es. Alert sticky vs inline):

```json
"platforms": ["android", "ios"],
"figmaNodeIds": {
  "android": "6608:11109",
  "ios": "6608:11109"
},
"figmaLayouts": {
  "sticky": "6608:11109",
  "inline": "6608:11431"
},
"usage": {
  "commonPatterns": [
    { "name": "error-feedback", "layout": "sticky", "description": "...", "composition": "..." },
    { "name": "inline-validation", "layout": "inline", "description": "...", "composition": "..." }
  ]
}
```

`figmaNodeIds` punta al layout canonico per ogni platform (di solito il primo o quello più visibile). `figmaLayouts` enumera tutti i layout, layout-specifici. Per i componenti senza layout multipli (Button, Accordion, ecc.) `figmaLayouts` si omette.

**Campi del blocco `rationale`**.

| Campo                       | Tipo            | Obbligatorio | Note                                                                                                                                  |
|-----------------------------|-----------------|--------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `rationale.designDecisions` | string markdown | Sì se `full` | Lista discorsiva delle decisioni di design del componente: razionali, evidenze da user testing/ricerca, eccezioni, note storiche. Per scaffold: stringa vuota (`""`). Markdown ammesso, incluse referenze inline alle immagini in formato `[N.M]` (vedi sezione 5). |

**Campi della skill** (struttura completa documentata in `skills/ai-component-metadata/SKILL.md`).

| Campo                            | Tipo            | Obbligatorio | Note                                                                 |
|----------------------------------|-----------------|--------------|----------------------------------------------------------------------|
| `component.name`                 | string          | Sì           | Nome leggibile del componente                                        |
| `component.category`             | enum            | Sì           | `atoms`, `molecules`, `organisms`                                    |
| `component.description`          | string          | Sì se `full` | Descrizione breve in 1 frase                                         |
| `component.type`                 | enum            | Sì           | `interactive`, `display`, `container`, `input`, `navigation`        |
| `usage.useCases[]`               | array di string | Sì se `full` | Casi d'uso semantici, almeno 1 per componenti `full`                 |
| `usage.requiredProps[]`          | array di string | No           | Props obbligatorie da passare sempre                                 |
| `usage.commonPatterns[]`         | array di object | No           | Pattern d'uso comuni con `name`, `description`, `composition`, opzionale `images` (array di ID immagine, vedi sezione 5), opzionale `layout` (nome di una chiave di `figmaLayouts` quando il pattern è specifico di un layout) |
| `usage.antiPatterns[]`           | array di object | No           | Con `scenario`, `reason`, `alternative`, opzionale `images` (array di ID immagine, vedi sezione 5) |
| `composition.slots`              | object          | No           | Slot/subcomponenti con `required` e `description`                    |
| `composition.nestedComponents[]` | array di string | No           | Componenti figli usati internamente                                  |
| `composition.commonPartners[]`   | array di string | No           | Componenti con cui viene spesso combinato                            |
| `composition.parentConstraints[]`| array di string | No           | Vincoli di posizionamento                                            |
| `behavior.states[]`              | array di string | No           | Stati interattivi supportati                                         |
| `behavior.interactions`          | object          | No           | Chiave → descrizione comportamento (click, hover, focus, space…)    |
| `behavior.responsive`            | object          | No           | Chiavi: `mobile`, `tablet`, `desktop`. Valore: stringa descrittiva  |
| `content.maxLines`               | object          | No           | Mappa elemento-testo → max linee (es. `{"title": 2, "label": 1}`)   |
| `content.characterLimits`        | object          | No           | Mappa elemento-testo → max caratteri (es. `{"label": 20}`)          |
| `content.overflow`               | string          | No           | `ellipsis` / `clamp` / `scroll` / `none` / `mixed`                  |
| `content.rules`                  | array di string | No           | Regole free-text non esprimibili con i campi sopra                  |
| `accessibility.role`             | string          | No           | Ruolo ARIA                                                           |
| `accessibility.keyboardSupport`  | string          | No           | Descrizione del supporto keyboard                                    |
| `accessibility.screenReader`     | string          | No           | Comportamento con screen reader                                      |
| `accessibility.focusManagement`  | string          | No           | Strategia di gestione del focus                                      |
| `accessibility.wcag`             | string          | No           | Livello WCAG (`AA`, `AAA`)                                           |
| `aiHints.priority`               | enum            | No           | `high`, `medium`, `low`                                              |
| `aiHints.keywords[]`             | array di string | No           | Keyword che triggerano l'uso di questo componente                    |
| `aiHints.context`                | string          | No           | Quando l'AI deve scegliere questo componente                         |

---

## 5. Naming delle immagini

Le immagini in `components/{slug}/docs/images/` usano un naming numerico che funge anche da **identificatore univoco** referenziabile dal `metadata.json`.

**Formato base.**

```
{slug}{N}.{M}.{ext}
```

Dove:

- `{slug}` — slug del componente (sempre presente)
- `{N}.{M}` — identificatore dell'immagine in formato dotted (es. `1.1`, `1.2`, `2.3`):
  - `N` è il gruppo logico (es. `1.x` per varianti, `2.x` per stati, `3.x` per anti-pattern — convenzione consigliata, non forzata)
  - `M` è la posizione all'interno del gruppo
- `{ext}` — estensione del file: `png` (preferito), `jpg`, `webp`

L'ID `N.M` deve essere **univoco e stabile per componente**: una volta assegnato non va riusato per immagini diverse, anche se l'originale viene sostituita.

**Esempi.**

```
button1.1.png            → Button — immagine 1.1 (gruppo 1, primo elemento)
button1.2.png            → Button — immagine 1.2
button2.1.png            → Button — immagine 2.1 (gruppo 2)
button-icon1.1.png       → Button Icon — immagine 1.1
modal-feedback3.2.png    → Modal Feedback — immagine 3.2
```

**Specifiche tecniche.**

- Risoluzione minima: 800px sul lato lungo
- Formato preferito: PNG su sfondo trasparente o sfondo che riproduce la canvas reale
- Peso massimo per file: 500 KB (oltre, comprimere o ridurre risoluzione)
- Nessun watermark, nessuna annotazione visiva sovrapposta — le note vanno nel `metadata.json`

**Referenziare un'immagine dal `metadata.json`.**

Gli identificatori `N.M` sono usati come **link logici** tra immagini e contenuto del JSON. Due modi:

1. **Campo `images: ["N.M", ...]`** in qualunque oggetto di `usage.commonPatterns[]`, `usage.antiPatterns[]` (o estensioni future). Esempio:
   ```json
   {
     "scenario": "multiple-primary-buttons",
     "reason": "Confonde la gerarchia visiva",
     "images": ["2.1", "2.2"]
   }
   ```

2. **Reference inline `[N.M]`** dentro stringhe markdown come `rationale.designDecisions`. Esempio:
   ```
   "designDecisions": "Il padding usa spacing-3 dopo user testing (vedi [1.1])."
   ```

Un'immagine **deve** comparire come ID `N.M` almeno una volta nel `metadata.json` (in `images` o inline `[N.M]`): un'immagine non referenziata è invisibile all'LLM e va rimossa o referenziata.

---

## 6. File a livello di repo

Oltre alle cartelle dei singoli componenti, la repo contiene questi file alla radice:

| File              | Generato   | Scopo                                                                       |
|-------------------|------------|-----------------------------------------------------------------------------|
| `README.md`       | Manuale    | Introduzione alla repo e istruzioni di utilizzo                             |
| `SCHEMA.md`       | Manuale    | Questo documento                                                            |
| `WRITING-GUIDE.md`| Manuale    | Guida alla scrittura del blocco `rationale` del `metadata.json` per il team UX |
| `inventory.md`    | Manuale    | Inventario di tutti i componenti del DS, con stato di documentazione        |
| `aliases.json`    | Manuale    | Mappa di nomi alternativi → slug canonici                                   |
| `index.toon`      | Automatico | Indice TOON aggregato di tutti i componenti (token-efficient, ~5k token), generato dalla GitHub Action |

`index.toon` viene rigenerato a ogni push su `main` da una GitHub Action ([`.github/workflows/generate-index.yml`](.github/workflows/generate-index.yml)). Lo script ([`scripts/build_index.py`](scripts/build_index.py)) aggrega `slug/name/category/type/status/lastUpdated` di ogni componente, gli antiPattern globali, e il dependencyGraph (`composition.nestedComponents`). **Non va mai modificato a mano** — è output derivato.

**Perché TOON e non JSON.** TOON è ~40-70% più compatto di JSON sugli stessi dati (formato tabular con header dichiarativo invece di chiavi ripetute), e l'accuracy LLM sul recupero dati è leggermente più alta. Per la doc-repo questo significa caricare tutti i 60+ componenti in un singolo file da ~5k token invece di leggere 60 metadata.json (~200k token). Dettagli in [`skills/codebase-index/SKILL.md`](skills/codebase-index/SKILL.md).

---

## 7. Stato `scaffold` vs `full`

Un componente in stato `scaffold` ha la struttura prevista dallo schema ma il contenuto è incompleto. Serve a tracciare nell'inventario quali componenti sono ancora da documentare in profondità.

**Cosa deve esserci in un componente `scaffold`.**

- Tutti i file (`metadata.json`, `changelog.md`) esistono
- Il `metadata.json` contiene i campi di repo-level (`slug`, `lastUpdated`, `status: scaffold`, `platforms: []`, `figmaNodeIds: {}`), i campi della skill (`component.name`, `component.category`, `component.type`) con gli array `useCases` e `antiPatterns` vuoti, e il blocco `rationale` presente come oggetto con `designDecisions: ""`
- Il `changelog.md` contiene **solo il frontmatter YAML** (`component`, `figma_id`, `last_updated`); il plugin Changelog Master appende le entry quando il team DS registra le prime modifiche

**Cosa deve esserci in più in un componente `full`.**

- `metadata.json` completamente compilato, inclusi `component.description`, almeno 1 `useCases[]`, `behavior`, `accessibility`, `platforms[]` con almeno 1 OS supportato, `figmaNodeIds` con una chiave per ogni platform elencata, e il blocco `rationale` con `designDecisions` valorizzato quando esistono razionali documentati
- Niente TODO residui in `rationale`
- Idealmente almeno 1 elemento in `usage.antiPatterns[]`
- Le immagini Do/Don't sono presenti e referenziate nel testo

**Transizione da scaffold a full.**

Quando un componente viene completato:

1. Compilare tutti i campi mancanti di `metadata.json`, incluso il blocco `rationale`
2. Aggiornare `status: scaffold` → `status: full` nel `metadata.json`
3. Aggiornare `lastUpdated` con la data corrente
4. Eseguire la pipeline di conversione per validare la consistenza
5. Commit con messaggio convenzionale: `docs({slug}): promote to full`

---

## 8. Versioning dello schema

Questo schema può evolvere. Quando viene modificato in modo non retrocompatibile (campi obbligatori aggiunti, campi rinominati, struttura cambiata), va incrementata la versione dello schema e va comunicata la modifica.

La versione corrente dello schema è documentata qui:

```
SCHEMA_VERSION: 3.2
```

In caso di modifiche, aggiornare la versione e aggiungere una nota nel `CHANGELOG.md` della repo template.

---

*SCHEMA v3.2 — Aggiunto campo opzionale `figmaLayouts{}` per componenti con più frame Figma di layout/placement (es. Alert sticky vs inline). Aggiunto campo opzionale `layout` dentro ogni `usage.commonPatterns[]`, che referenzia una chiave di `figmaLayouts`. Retrocompatibile con v3.1: i componenti senza layout multipli omettono `figmaLayouts`.*

*SCHEMA v3.1 — Aggiunti due campi repo-level obbligatori: `platforms[]` (OS supportati: `android`, `ios`, `ios-liquid-glass`) e `figmaNodeIds{}` (mappa platform → ID nodo Figma). Liquid Glass iOS è trattato come platform separata, non come variante di `ios`. Lo schema v3.1 è retrocompatibile con metadata v3.0 a patto di aggiungere i due campi come `[]` e `{}` agli scaffold esistenti.*

*SCHEMA v3.0 — Breaking change: `rationale-note.md` rimosso. Il contenuto "Perché è così" è ora rappresentato dal blocco `rationale` dentro `metadata.json`, con il solo campo `designDecisions` (string markdown). Eccezioni, note storiche e relazioni tra componenti sono state assorbite: eccezioni e note storiche dentro `designDecisions`, relazioni dentro i campi esistenti `composition.*` (`nestedComponents`, `commonPartners`, `parentConstraints`) e `usage.antiPatterns` (alternative). Naming immagini cambiato da `{slug}-{variant?}-{do|dont}-{n}.{ext}` a `{slug}{N}.{M}.{ext}`, con gli ID `N.M` referenziabili dal JSON via campo `images: ["N.M"]` (in commonPatterns/antiPatterns) o reference inline `[N.M]` (in `designDecisions`). I campi aggiuntivi della repo rispetto alla skill AI Component Metadata sono `slug`, `lastUpdated`, `status`, `rationale`.*
