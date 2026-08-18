/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE?: string
  readonly VITE_BASE_PATH?: string
  readonly VITE_DEATH_RECORDS_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
