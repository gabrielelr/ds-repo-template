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
        ├── purpose-usage.md       Obbligatorio
        ├── behavior.md            Obbligatorio
        ├── rationale-note.md      Obbligatorio
        ├── changelog.md           Obbligatorio (sincronizzato da Changelog Master)
        ├── metadata.json          Obbligatorio
        └── images/                Obbligatoria, può essere vuota
            └── *.png
```

**Regole.**

- I nomi dei file sono fissi e case-sensitive: `purpose-usage.md`, non `purpose.md` né `Purpose-Usage.md`.
- Tutti i file (quattro Markdown + un JSON) esistono sempre, anche per i componenti in stato `scaffold`.
- La cartella `images/` esiste sempre. Se vuota, contiene un file `.gitkeep` per essere versionata da Git.
- Niente sottocartelle dentro `docs/` oltre a `images/`.
- Il file `changelog.md` non viene mai modificato a mano: è sincronizzato automaticamente dal plugin Changelog Master di Figma (vedi sezione 5).

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

## 3. Frontmatter dei Markdown

Ogni file Markdown inizia con un blocco YAML racchiuso tra `---`. Il frontmatter è la fonte di verità per i metadati, anche più del contenuto del file.

**Esempio in cima a `purpose-usage.md`.**

```yaml
---
slug: button
section: purpose-usage
component: Button
version: 1.0.0
lastUpdated: 2026-05-09
status: full
---

# Button

Il button è...
```

**Campi obbligatori.**

| Campo         | Tipo   | Valori ammessi                                         |
|---------------|--------|--------------------------------------------------------|
| `slug`        | string | Slug del componente, conforme alla sezione 2           |
| `section`     | enum   | `purpose-usage`, `behavior`, `rationale-note`          |
| `component`   | string | Nome leggibile del componente                          |
| `lastUpdated` | string | Data ISO `YYYY-MM-DD` dell'ultima modifica significativa |
| `status`      | enum   | `full` o `scaffold`                                    |

**Campi opzionali.**

| Campo     | Tipo   | Note                                                |
|-----------|--------|-----------------------------------------------------|
| `version` | string | Semver del componente nel design system             |
| `author`  | string | Chi ha scritto la sezione (utile in team grandi)    |
| `reviewer`| string | Chi ha validato la documentazione                   |

**Regole.**

- `lastUpdated` si aggiorna a ogni modifica di contenuto, non a ogni commit.
- Quando un componente passa da `scaffold` a `full`, lo `status` va aggiornato in tutti e tre i Markdown.
- Lo `slug` nel frontmatter deve corrispondere al nome della cartella che contiene il file.

---

## 4. Contenuto dei tre file Markdown

I tre file coprono ognuno un aspetto diverso del componente. La separazione non è opzionale: serve a tenere distinte le informazioni di tipo diverso, in modo che il sistema di chat possa recuperare la sezione giusta in base alla domanda.

### 4.1 `purpose-usage.md` — A cosa serve, quando si usa

Risponde alle domande: *"Cos'è questo componente? Quando lo uso? Quando NON lo uso?"*

**Sezioni interne.**

- `## Cos'è` — definizione in 1-2 frasi
- `## Quando usarlo` — casi d'uso espliciti, in elenco descrittivo
- `## Quando NON usarlo` — anti-pattern, ognuno con motivo e alternativa
- `## Varianti` — elenco delle varianti del componente con la regola di scelta tra loro
- `## Esempi visivi` — riferimenti alle immagini nella cartella `images/`, con descrizione testuale di ogni esempio

**Regola critica.** Ogni immagine Do/Don't presente in `images/` deve essere accompagnata da almeno una frase descrittiva nel testo. Una documentazione che mostra un Don't solo come immagine è incompleta — l'immagine non viene letta dall'LLM.

### 4.2 `behavior.md` — Come si comporta

Risponde alle domande: *"Come reagisce all'interazione? Quali stati ha? Come cambia tra dispositivi?"*

**Sezioni interne.**

- `## Stati` — elenco degli stati interattivi (default, hover, pressed, disabled, focus, loading, error)
- `## Interazioni` — comportamento al tap, swipe, keyboard, eventuali gesture specifiche
- `## Animazioni` — transizioni e tempi, se rilevanti
- `## Responsive` — comportamento su mobile, tablet, desktop (se applicabile)
- `## Accessibilità` — ruolo ARIA, label richieste, comportamento con screen reader, gestione focus

**Regola.** Le specifiche visive precise (pixel, colori esatti, font-size) **non** vanno qui. Stanno in Figma. Qui va il *comportamento*, non la *resa visiva*.

### 4.3 `rationale-note.md` — Perché è così

Risponde alle domande: *"Perché è progettato in questo modo? Quali decisioni di design ci sono dietro? Quali eccezioni esistono?"*

**Sezioni interne.**

- `## Decisioni di design` — perché certe scelte sono state fatte
- `## Eccezioni` — casi in cui il componente si discosta dalle regole standard del DS
- `## Note storiche` — evoluzione del componente, deprecazioni, migrazioni
- `## Componenti correlati` — link ad altri componenti che interagiscono con questo, con relazione esplicita ("usato dentro X", "alternativa a Y", "compone Z")

**Regola.** Questo file è il più "discorsivo" dei tre. Serve sia ai designer (per capire il *perché*) sia agli LLM (per disambiguare casi d'uso simili a partire dal contesto storico/progettuale).

---

## 5. `changelog.md` — Storico delle modifiche del componente

Il file `changelog.md` traccia l'evoluzione del componente nel tempo: nuove varianti, modifiche comportamentali, fix, deprecazioni. È sincronizzato automaticamente dal plugin **Changelog Master** di Figma e non va mai modificato a mano.

**Workflow di aggiornamento.**

1. Il team DS modifica il componente direttamente in Figma (nuova variante, modifica di proprietà, deprecazione)
2. All'interno del plugin Changelog Master, il team DS registra la modifica indicando tipo, descrizione, autore ed eventuale progetto/revisore
3. La modifica entra nella **Sync Queue** del plugin, dove può essere ancora corretta o cancellata prima dell'invio
4. Al sync, il plugin scrive l'aggiornamento al file `components/{slug}/docs/changelog.md` della repo, in append rispetto allo storico precedente, e aggiorna il campo `last_updated` del frontmatter
5. Eventuali documenti correlati (`purpose-usage.md`, `behavior.md`, `metadata.json`) vanno aggiornati a mano dal team UX se la modifica impatta la documentazione

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

## 6. Struttura del `metadata.json`

Il `metadata.json` è la versione strutturata della stessa informazione contenuta nei Markdown. È quello che alimenta il sistema di check di aderenza e che viene caricato dall'LLM quando deve dare risposte precise sulle regole.

**Schema di riferimento completo.**

```json
{
  "component": "Button",
  "slug": "button",
  "version": "1.0.0",
  "lastUpdated": "2026-05-09",
  "status": "full",

  "usage": {
    "useCases": [
      {
        "name": "Azione primaria di una schermata",
        "description": "Il button primary identifica l'azione principale che l'utente deve compiere in un determinato contesto.",
        "example": "Conferma del checkout, invio di un form, prosecuzione di un flusso."
      }
    ],
    "antiPatterns": [
      {
        "scenario": "Più di un button primary nella stessa schermata",
        "reason": "La gerarchia visiva si annulla e l'utente non capisce qual è l'azione primaria.",
        "alternative": "Usare un solo primary; gli altri button diventano secondary o tertiary.",
        "severity": "critical"
      }
    ]
  },

  "variants": [
    {
      "name": "primary",
      "whenToUse": "Per l'azione principale di una schermata o di un flusso.",
      "whenNotToUse": "Per azioni distruttive (usa la variante destructive) o secondarie (usa secondary)."
    },
    {
      "name": "secondary",
      "whenToUse": "Per azioni alternative o di supporto, sempre presenti accanto a un primary.",
      "whenNotToUse": "Da solo in una schermata: se è l'unica azione, dovrebbe essere primary."
    }
  ],

  "behavior": {
    "states": ["default", "hover", "pressed", "disabled", "focus", "loading"],
    "platforms": {
      "mobile": [
        "Touch target minimo 44x44pt",
        "Bottom navigation: layout flex row, bottoni affiancati al 50/50"
      ],
      "tablet": [
        "Touch target minimo 44x44pt",
        "Bottom navigation: layout flex row con padding orizzontale aumentato"
      ]
    },
    "accessibility": {
      "role": "button",
      "requiredLabel": true,
      "keyboardSupport": ["Enter", "Space"]
    }
  },

  "aiHints": {
    "contextMapping": {
      "modal": "Usare button-group con primary + secondary",
      "form": "Primary in fondo al form, allineato a destra su desktop"
    },
    "commonQuestions": [
      "Quando uso primary vs secondary?",
      "Posso avere due primary?",
      "Come gestisco lo stato loading?"
    ]
  },

  "relatedComponents": [
    { "slug": "button-group", "relation": "compone" },
    { "slug": "icon-button", "relation": "alternativa-per-azioni-icona-only" },
    { "slug": "link", "relation": "alternativa-per-navigazione" }
  ]
}
```

**Specifica dei campi.**

| Campo                           | Tipo            | Obbligatorio | Note                                                                          |
|---------------------------------|-----------------|--------------|-------------------------------------------------------------------------------|
| `component`                     | string          | Sì           | Nome leggibile                                                                |
| `slug`                          | string          | Sì           | Conforme alla sezione 2                                                       |
| `version`                       | string          | No           | Semver                                                                        |
| `lastUpdated`                   | string          | Sì           | ISO `YYYY-MM-DD`                                                              |
| `status`                        | enum            | Sì           | `full` o `scaffold`                                                           |
| `usage.useCases[]`              | array di object | Sì se `full` | Almeno 1 elemento per componenti `full`                                       |
| `usage.useCases[].name`         | string          | Sì           | Titolo del caso d'uso, max 80 caratteri                                       |
| `usage.useCases[].description`  | string          | Sì           | Descrizione discorsiva del caso d'uso                                         |
| `usage.useCases[].example`      | string          | No           | Esempio concreto                                                              |
| `usage.antiPatterns[]`          | array di object | No           | Può essere vuoto, ma più ne ha più il check è efficace                        |
| `usage.antiPatterns[].scenario` | string          | Sì           | Descrizione della violazione                                                  |
| `usage.antiPatterns[].reason`   | string          | Sì           | Spiegazione del perché è sbagliato                                            |
| `usage.antiPatterns[].alternative`| string         | Sì           | Cosa fare al suo posto                                                        |
| `usage.antiPatterns[].severity` | enum            | Sì           | `critical`, `warning`, `suggestion`                                           |
| `variants[]`                    | array di object | No           | Solo se il componente ha varianti formali                                     |
| `variants[].name`               | string          | Sì           | Nome della variante come definita nel DS                                      |
| `variants[].whenToUse`          | string          | Sì           | Regola di scelta della variante                                               |
| `variants[].whenNotToUse`       | string          | Sì           | Quando NON sceglierla                                                         |
| `behavior.states[]`             | array di string | No           | Stati interattivi supportati                                                  |
| `behavior.platforms`            | object          | No           | Chiavi: `mobile`, `tablet`, `desktop`. Valori: array di regole comportamentali |
| `behavior.accessibility`        | object          | No           | `role`, `requiredLabel`, `keyboardSupport[]`                                  |
| `aiHints.contextMapping`        | object          | No           | Mappa contesti d'uso → regole specifiche, utile al sistema di chat            |
| `aiHints.commonQuestions[]`     | array di string | No           | Domande tipiche, usate per migliorare il routing nelle query LLM              |
| `relatedComponents[]`           | array di object | No           | Link ad altri componenti                                                      |
| `relatedComponents[].slug`      | string          | Sì           | Slug del componente correlato                                                 |
| `relatedComponents[].relation`  | string          | Sì           | Tipo di relazione: `compone`, `composto-da`, `alternativa-a`, `usato-dentro`  |

**Regole sulla severity degli antiPatterns.**

- `critical` — viola una regola fondamentale del DS, va sempre corretto. Genera un errore nel check.
- `warning` — è probabilmente sbagliato ma può avere eccezioni legittime. Genera un avviso.
- `suggestion` — è una raccomandazione di miglioramento, non una violazione. Genera una nota informativa.

---

## 7. Naming delle immagini

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
- Nessun watermark, nessuna annotazione visiva sovrapposta — le note vanno nel testo del Markdown

---

## 8. File a livello di repo

Oltre alle cartelle dei singoli componenti, la repo contiene questi file alla radice:

| File              | Generato | Scopo                                                                  |
|-------------------|----------|------------------------------------------------------------------------|
| `README.md`       | Manuale  | Introduzione alla repo e istruzioni di utilizzo                        |
| `SCHEMA.md`       | Manuale  | Questo documento                                                       |
| `WRITING-GUIDE.md`| Manuale  | Guida alla scrittura dei Markdown per il team UX                       |
| `inventory.md`    | Manuale  | Inventario di tutti i componenti del DS, con stato di documentazione   |
| `aliases.json`    | Manuale  | Mappa di nomi alternativi → slug canonici                              |
| `index.json`      | Automatico | Indice strutturato di tutti i componenti, generato dalla GitHub Action |

`index.json` viene rigenerato a ogni push su `main` da una GitHub Action. Non va mai modificato a mano.

---

## 9. Stato `scaffold` vs `full`

Un componente in stato `scaffold` ha la struttura prevista dallo schema ma il contenuto è incompleto. Serve a tracciare nell'inventario quali componenti sono ancora da documentare in profondità.

**Cosa deve esserci in un componente `scaffold`.**

- Tutti i file (Markdown + JSON) esistono
- Il frontmatter dei tre Markdown principali è compilato (slug, section, component, lastUpdated, `status: scaffold`)
- I tre Markdown principali contengono almeno un titolo H1 e i nomi delle sezioni previste, con commenti `<!-- TODO: ... -->` per indicare cosa manca
- Il `metadata.json` contiene i campi obbligatori a livello root (`component`, `slug`, `version`, `lastUpdated`, `status: scaffold`) e gli array `useCases` e `antiPatterns` vuoti
- Il `changelog.md` contiene **solo il frontmatter YAML** (`component`, `figma_id`, `last_updated`); il plugin Changelog Master appende le entry quando il team DS registra le prime modifiche

**Cosa deve esserci in più in un componente `full`.**

- Tutti i Markdown sono compilati con contenuto reale, niente TODO residui
- `metadata.json` ha almeno 1 elemento in `usage.useCases[]`
- Idealmente almeno 1 elemento in `usage.antiPatterns[]` (la qualità del check di aderenza dipende dalla loro completezza)
- Le immagini Do/Don't sono presenti e referenziate nel testo

**Transizione da scaffold a full.**

Quando un componente viene completato:

1. Compilare tutti i campi mancanti dei Markdown e del JSON
2. Aggiornare `status: scaffold` → `status: full` in tutti i Markdown e nel JSON
3. Aggiornare `lastUpdated` con la data corrente
4. Eseguire la pipeline di conversione per validare la consistenza tra Markdown e JSON
5. Commit con messaggio convenzionale: `docs({slug}): promote to full`

---

## 10. Versioning dello schema

Questo schema può evolvere. Quando viene modificato in modo non retrocompatibile (campi obbligatori aggiunti, campi rinominati, struttura cambiata), va incrementata la versione dello schema e va comunicata la modifica.

La versione corrente dello schema è documentata qui:

```
SCHEMA_VERSION: 1.0
```

In caso di modifiche, aggiornare la versione e aggiungere una nota nel `CHANGELOG.md` della repo template.

---

*SCHEMA v1.0 — Bozza iniziale per il sistema di documentazione design system Conflux. Validare e iterare sui primi 2-3 componenti reali del DS Cross-App prima di considerarlo definitivo.*
