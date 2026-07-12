import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { fileURLToPath } from "url";

const appDir = fileURLToPath(new URL(".", import.meta.url));
const reactSystemDir = fileURLToPath(new URL("..", import.meta.url));

export default defineConfig({
  plugins: [react()],
  root: appDir,
  resolve: {
    alias: {
      "@app": appDir,
      "@react-system": reactSystemDir,
      "@design-systems": path.resolve(reactSystemDir, "../design-systems"),
    },
  },
});
