import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  define: {
    // Support both VITE_API_URL (preferred) and NEXT_PUBLIC_API_URL for Vercel compatibility.
    // Leaving blank when unset so the frontend correctly falls back to mock data.
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
  },
});
