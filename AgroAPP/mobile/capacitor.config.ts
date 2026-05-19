import type { CapacitorConfig } from "@capacitor/cli";

/**
 * URL dell'app Streamlit pubblicata (HTTPS obbligatorio per iOS).
 * Modifica con: npm run config:url -- https://tuo-account.streamlit.app
 * Oppure imposta la variabile AGROAPP_SERVER_URL prima di `npx cap sync`.
 */
/** Sostituisci con l'URL pubblico Streamlit (HTTPS) prima di compilare l'app nativa */
const DEFAULT_SERVER_URL = "https://REPLACE_WITH_YOUR_STREAMLIT_URL.streamlit.app";

const serverUrl = process.env.AGROAPP_SERVER_URL || DEFAULT_SERVER_URL;

const config: CapacitorConfig = {
  appId: "it.agroapp.gestionale",
  appName: "AgroApp",
  webDir: "www",
  server: {
    url: serverUrl,
    cleartext: false,
    androidScheme: "https",
  },
  android: {
    allowMixedContent: false,
  },
  ios: {
    contentInset: "automatic",
    scrollEnabled: true,
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: "#2d6a4f",
      showSpinner: false,
    },
    StatusBar: {
      style: "LIGHT",
      backgroundColor: "#2d6a4f",
    },
  },
};

export default config;
