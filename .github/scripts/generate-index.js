// .github/scripts/generate-index.js
//
// Legge tutti i metadata.json dentro components/ e produce l'index.json.
// In modalità dry-run (default), stampa il risultato nei log invece di scriverlo su file.
// Per attivare la scrittura, impostare WRITE_TO_FILE=true (verrà fatto al task 22).

const fs = require('fs');
const path = require('path');

// === Configurazione ===
const COMPONENTS_DIR = path.join(process.cwd(), 'components');
const OUTPUT_FILE = path.join(process.cwd(), 'index.json');
const WRITE_TO_FILE = process.env.WRITE_TO_FILE === 'true';

// Cartelle che iniziano con "_" sono esempi/template, non componenti veri
const EXCLUDED_PREFIX = '_';

// === Funzioni di utility ===

function findComponentDirs() {
  if (!fs.existsSync(COMPONENTS_DIR)) {
    console.log(`⚠️  Cartella components/ non trovata in ${COMPONENTS_DIR}`);
    return [];
  }

  return fs.readdirSync(COMPONENTS_DIR, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .filter(d => !d.name.startsWith(EXCLUDED_PREFIX))
    .map(d => d.name);
}

function readMetadata(slug) {
  const metaPath = path.join(COMPONENTS_DIR, slug, 'docs', 'metadata.json');
  if (!fs.existsSync(metaPath)) {
    console.log(`  ⚠️  ${slug}: metadata.json mancante`);
    return null;
  }

  try {
    const raw = fs.readFileSync(metaPath, 'utf-8');
    return JSON.parse(raw);
  } catch (err) {
    console.log(`  ❌ ${slug}: metadata.json non valido (${err.message})`);
    return null;
  }
}

function buildIndexEntry(slug, metadata) {
  if (!metadata) return null;

  // Estrae i campi rilevanti per l'index, mantenendolo leggero
  // N.B. `component` è ora un oggetto con name, category, description, type
  return {
    slug: metadata.slug || slug,
    component: metadata.component?.name || slug,
    category: metadata.component?.category || null,
    type: metadata.component?.type || null,
    description: metadata.component?.description || null,
    status: metadata.status || 'unknown',
    lastUpdated: metadata.lastUpdated || null,
    useCases: (metadata.usage?.useCases || []),
    antiPatternsCount: (metadata.usage?.antiPatterns || []).length,
    commonPatternsCount: (metadata.usage?.commonPatterns || []).length
  };
}

// === Main ===

function main() {
  console.log('🔍 Scansione componenti...\n');

  const slugs = findComponentDirs();
  console.log(`Trovate ${slugs.length} cartelle componenti.\n`);

  if (slugs.length === 0) {
    console.log('Nessun componente da indicizzare. Esco senza errori.');
    return;
  }

  const entries = [];
  let fullCount = 0;
  let scaffoldCount = 0;
  let errorCount = 0;

  for (const slug of slugs) {
    const metadata = readMetadata(slug);
    const entry = buildIndexEntry(slug, metadata);

    if (entry) {
      entries.push(entry);
      if (entry.status === 'full') fullCount++;
      else if (entry.status === 'scaffold') scaffoldCount++;
      console.log(`  ✓ ${slug} [${entry.status}]`);
    } else {
      errorCount++;
    }
  }

  // Costruisce l'index finale
  const index = {
    generatedAt: new Date().toISOString(),
    totalComponents: entries.length,
    full: fullCount,
    scaffold: scaffoldCount,
    components: entries.sort((a, b) => a.slug.localeCompare(b.slug))
  };

  // Output
  console.log('\n📊 Riepilogo:');
  console.log(`   Componenti totali:  ${index.totalComponents}`);
  console.log(`   Full:               ${fullCount}`);
  console.log(`   Scaffold:           ${scaffoldCount}`);
  console.log(`   Errori di lettura:  ${errorCount}`);

  if (WRITE_TO_FILE) {
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(index, null, 2) + '\n', 'utf-8');
    console.log(`\n✅ index.json scritto in ${OUTPUT_FILE}`);
  } else {
    console.log('\n📄 Contenuto index.json (dry-run, non scritto su file):\n');
    console.log(JSON.stringify(index, null, 2));
  }
}

main();