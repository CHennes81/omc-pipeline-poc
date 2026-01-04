import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Generate build-time constants
const buildIso = new Date().toISOString();
const buildDate = new Date(buildIso);
const versionId = `${buildDate.getFullYear()}${String(buildDate.getMonth() + 1).padStart(2, '0')}${String(buildDate.getDate()).padStart(2, '0')}-${String(buildDate.getHours()).padStart(2, '0')}${String(buildDate.getMinutes()).padStart(2, '0')}${String(buildDate.getSeconds()).padStart(2, '0')}`;

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    __BUILD_ISO__: JSON.stringify(buildIso),
    __VERSION_ID__: JSON.stringify(versionId),
  },
});
