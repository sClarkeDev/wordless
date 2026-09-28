/// <reference types="vite/client" />

interface ImportMetaEnv {
  // owner/name, injected by vite.config.ts
  readonly VITE_REPO: string
  readonly VITE_RESULTS_URL?: string
}
