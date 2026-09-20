import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  define: {
    // VITE_API_URL is the preferred env var (set it in Vercel project settings).
    // NEXT_PUBLIC_API_URL is kept for backward compatibility.
    // Both default to "" so the frontend calls relative /api/* paths in
    // production, which Vercel rewrites proxy to the Render backend.
    "import.meta.env.VITE_API_URL": JSON.stringify(process.env.VITE_API_URL || ""),
    "import.meta.env.NEXT_PUBLIC_API_URL": JSON.stringify(process.env.NEXT_PUBLIC_API_URL || ""),
    "import.meta.env.NEXT_PUBLIC_USE_MOCK_DATA": JSON.stringify(process.env.NEXT_PUBLIC_USE_MOCK_DATA || "false"),
  },
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "client", "src"),
      "@shared": path.resolve(import.meta.dirname, "shared"),
    },
  },
  root: path.resolve(import.meta.dirname, "client"),
  build: {
    outDir: path.resolve(import.meta.dirname, "dist/public"),
    emptyOutDir: true,
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      // Proxy /api/* and related paths to the FastAPI backend during local dev.
      // This eliminates CORS issues and makes the frontend behave identically
      // in dev (port 3000) and in production (Vercel rewrites).
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/health": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/docs": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/openapi.json": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
