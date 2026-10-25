import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // Forward any request starting with /api to the FastAPI server.
    // The browser only ever talks to localhost:5173, so there are no CORS errors.
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
