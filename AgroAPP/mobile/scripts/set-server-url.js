/**
 * Imposta l'URL Streamlit in capacitor.config.ts
 * Uso: node scripts/set-server-url.js https://tuo-app.streamlit.app
 */
const fs = require("fs");
const path = require("path");

const url = process.argv[2];
if (!url || !url.startsWith("https://")) {
  console.error("Uso: node scripts/set-server-url.js https://tuo-app.streamlit.app");
  process.exit(1);
}

const configPath = path.join(__dirname, "..", "capacitor.config.ts");
let content = fs.readFileSync(configPath, "utf8");
const marker = 'const DEFAULT_SERVER_URL = "';
const start = content.indexOf(marker);
if (start === -1) {
  console.error("Impossibile trovare DEFAULT_SERVER_URL in capacitor.config.ts");
  process.exit(1);
}
const valueStart = start + marker.length;
const valueEnd = content.indexOf('";', valueStart);
content = content.slice(0, valueStart) + url + content.slice(valueEnd);
fs.writeFileSync(configPath, content);
console.log("URL server impostato:", url);
console.log("Esegui: npx cap sync");
