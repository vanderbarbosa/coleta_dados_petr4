import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Em desenvolvimento (`npm run dev`), o Vite encaminha `/api` para o backend
// FastAPI local (porta 8000) e serve o app na raiz.
//
// No BUILD para o GitHub Pages, o app é publicado numa subpasta
// (https://<usuario>.github.io/<repo>/), então `base` precisa apontar para ela.
// O workflow de deploy define VITE_BASE = "/<repo>/". Fora do Actions, o padrão
// abaixo cobre o repositório atual.
export default defineConfig(({ command }) => ({
  plugins: [react()],
  base: command === "build" ? (process.env.VITE_BASE || "/coleta_dados_petr4/") : "/",
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
}));
