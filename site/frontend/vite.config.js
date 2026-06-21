import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Encaminha /api para o backend FastAPI (porta 8000) durante o desenvolvimento.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
});
