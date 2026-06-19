import React from 'react' // React 核心库
import ReactDOM from 'react-dom/client' // React DOM 渲染库（v18 的 createRoot API）
import App from './App' // 根组件
import './index.css' // 全局样式

// ===== 应用入口：将 React 组件挂载到 index.html 的 #root 元素上 =====
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode> {/* 严格模式：在开发环境下进行额外检查，帮助发现潜在问题 */}
    <App />
  </React.StrictMode>,
)
