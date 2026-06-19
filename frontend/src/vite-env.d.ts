/// <reference types="vite/client" />

// 声明 Vite 环境变量类型
interface ImportMetaEnv {
  readonly VITE_API_BASE: string;  // API 基础地址
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
