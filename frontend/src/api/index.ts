import type { AnalysisResponse, FetchResponse, UploadResponse } from '../types'; // 导入响应类型定义

// API 基础路径：开发环境用本地代理，生产环境用 Render 部署地址
const BASE = (import.meta.env.VITE_API_BASE as string) || '/api';

// ===== 演示数据接口：获取后端预置的3组示例分析数据 =====
export async function fetchDemo(): Promise<{ total: number; results: any[] }> {
  const res = await fetch(`${BASE}/demo`);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to load demo');
  }
  return res.json();
}

// ===== 文本分析接口：用户手动输入标题和五点描述，直接调用后端分析 =====
export async function analyzeText(title: string, bullets: string[]): Promise<AnalysisResponse> {
  const res = await fetch(`${BASE}/analyze`, {
    method: 'POST', // POST 请求
    headers: { 'Content-Type': 'application/json' }, // JSON 格式
    body: JSON.stringify({ mode: 'text', title, bullets }), // 请求体包含模式、标题和五点描述
  });
  if (!res.ok) {
    const err = await res.json(); // 解析后端返回的错误信息
    throw new Error(err.detail || 'Analysis failed'); // 抛出用户友好的错误
  }
  return res.json(); // 返回分析结果 JSON
}

// ===== URL/ASIN 抓取分析接口：通过 Amazon 商品链接或 ASIN 码抓取并分析 =====
export async function fetchAndAnalyze(url: string, asin: string, marketplace: string = 'com', proxy: string = ''): Promise<FetchResponse> {
  const params = new URLSearchParams(); // 构造查询参数
  if (url) params.set('url', url); // 商品链接（可选）
  if (asin) params.set('asin', asin); // ASIN 码（可选）
  params.set('marketplace', marketplace); // 站点，默认美国
  if (proxy) params.set('proxy', proxy); // 代理设置（可选，用于反爬）

  const res = await fetch(`${BASE}/fetch?${params.toString()}`, { method: 'POST' }); // GET 参数用查询字符串，POST 请求体为空
  if (!res.ok) {
    const err = await res.json(); // 解析后端返回的错误信息
    throw new Error(err.detail || 'Fetch failed'); // 抛出用户友好的错误
  }
  return res.json(); // 返回包含商品元数据的分析结果
}

// ===== Excel 文件上传分析接口：上传 Excel 文件进行批量分析 =====
export async function uploadAndAnalyze(file: File): Promise<UploadResponse> {
  const formData = new FormData(); // 创建表单数据对象
  formData.append('file', file); // 将文件附加到表单数据

  const res = await fetch(`${BASE}/upload`, {
    method: 'POST',
    body: formData, // 使用 FormData 作为请求体（浏览器会自动设置 Content-Type: multipart/form-data）
  });
  if (!res.ok) {
    const err = await res.json(); // 解析后端返回的错误信息
    throw new Error(err.detail || 'Upload failed'); // 抛出用户友好的错误
  }
  return res.json(); // 返回批量分析结果
}
