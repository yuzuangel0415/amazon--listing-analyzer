import { useState } from 'react'; // React 状态管理 Hook
import type { AnalysisResponse, FetchResponse, UploadResponse } from './types'; // 类型定义
import { analyzeText, fetchAndAnalyze, uploadAndAnalyze, fetchDemo } from './api'; // API 请求函数
import InputPanel from './components/InputPanel'; // 输入面板组件
import AnalysisResult from './components/AnalysisResult'; // 分析结果组件
import Landing from './components/Landing'; // 欢迎页组件

// ===== 视图状态类型：欢迎页 | 输入 | 加载中 | 结果 | 错误 =====
type ViewState = 'landing' | 'input' | 'loading' | 'result' | 'error';

export default function App() {
  // ===== 全局状态管理 =====
  const [viewState, setViewState] = useState<ViewState>('landing'); // 默认显示欢迎页
  const [error, setError] = useState(''); // 错误信息
  const [results, setResults] = useState<AnalysisResponse[]>([]); // 分析结果数组（支持批量）
  const [currentIndex, setCurrentIndex] = useState(0); // 当前查看的结果索引
  const [fetchMeta, setFetchMeta] = useState<Partial<FetchResponse> | null>(null); // 抓取到的商品元数据
  const [demoNames, setDemoNames] = useState<string[]>([]); // 演示产品的名称列表

  // ===== 一键演示：加载后端预置的3组示例数据 =====
  const handleDemo = async () => {
    setViewState('loading'); // 切换到加载状态
    setError(''); // 清除之前的错误
    setFetchMeta(null); // 演示模式无抓取元数据
    try {
      const res = await fetchDemo(); // 调用演示数据 API
      setResults(res.results as AnalysisResponse[]);
      setDemoNames(res.results.map((r: any) => r.sample_name || ''));
      setCurrentIndex(0);
      setViewState('result');
    } catch (e: any) {
      setError(e.message);
      setViewState('error');
    }
  };

  // ===== 处理文本提交：用户手动输入标题和五点描述 =====
  const handleTextSubmit = async (title: string, bullets: string[]) => {
    setViewState('loading');
    setError('');
    setFetchMeta(null);
    setDemoNames([]);
    try {
      const res = await analyzeText(title, bullets);
      setResults([res]);
      setCurrentIndex(0);
      setViewState('result');
    } catch (e: any) {
      setError(e.message);
      setViewState('error');
    }
  };

  // ===== 处理 URL/ASIN 提交：从 Amazon 抓取商品信息并分析 =====
  const handleUrlSubmit = async (url: string, asin: string, marketplace: string, proxy: string) => {
    setViewState('loading');
    setError('');
    setDemoNames([]);
    try {
      const res = await fetchAndAnalyze(url, asin, marketplace, proxy);
      setResults([res]);
      setCurrentIndex(0);
      setFetchMeta({
        asin: res.asin,
        price: res.price,
        rating: res.rating,
        reviews_count: res.reviews_count,
        images: res.images,
      });
      setViewState('result');
    } catch (e: any) {
      setError(e.message);
      setViewState('error');
    }
  };

  // ===== 处理文件上传：上传 Excel 文件进行批量分析 =====
  const handleFileUpload = async (file: File) => {
    setViewState('loading');
    setError('');
    setFetchMeta(null);
    setDemoNames([]);
    try {
      const res: UploadResponse = await uploadAndAnalyze(file);
      setResults(res.results as AnalysisResponse[]);
      setCurrentIndex(0);
      setViewState('result');
    } catch (e: any) {
      setError(e.message);
      setViewState('error');
    }
  };

  // ===== 返回欢迎页 =====
  const handleGoHome = () => {
    setViewState('landing');
    setError('');
    setResults([]);
    setCurrentIndex(0);
    setFetchMeta(null);
    setDemoNames([]);
  };

  // ===== 返回输入页 =====
  const handleReset = () => {
    setViewState('input');
    setError('');
    setResults([]);
    setCurrentIndex(0);
    setFetchMeta(null);
    setDemoNames([]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* ===== 顶部导航栏：吸顶固定 ===== */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          {/* Logo 区域：点击返回欢迎页 */}
          <button onClick={handleGoHome} className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div className="w-10 h-10 rounded-xl bg-brand flex items-center justify-center text-white font-bold text-lg">
              A
            </div>
            <div className="text-left">
              <h1 className="text-xl font-bold text-gray-900">Amazon Listing 拆解工具</h1>
              <p className="text-xs text-gray-500">标题分析 · 五点拆解 · 卖点策略 · SEO评分</p>
            </div>
          </button>
          {/* 导航按钮 */}
          <div className="flex items-center gap-2">
            {viewState === 'result' && (
              <button
                onClick={handleReset}
                className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                重新分析
              </button>
            )}
            {viewState !== 'landing' && (
              <button
                onClick={handleGoHome}
                className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
              >
                首页
              </button>
            )}
          </div>
        </div>
      </header>

      {/* ===== 主内容区域 ===== */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* 欢迎页 */}
        {viewState === 'landing' && (
          <Landing
            onStartAnalysis={() => setViewState('input')}
            onDemo={handleDemo}
            loading={false}
          />
        )}

        {/* 输入视图 — 非landing状态下显示 */}
        {(viewState === 'input' || viewState === 'loading') && (
          <div className="max-w-3xl mx-auto mt-8">
            <InputPanel
              onTextSubmit={handleTextSubmit}
              onUrlSubmit={handleUrlSubmit}
              onFileUpload={handleFileUpload}
              loading={viewState === 'loading'}
            />
          </div>
        )}

        {/* 加载中视图 */}
        {viewState === 'loading' && (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="w-12 h-12 border-4 border-brand border-t-transparent rounded-full animate-spin" />
            <p className="mt-4 text-gray-500 font-medium">正在分析中...</p>
          </div>
        )}

        {/* 错误视图 */}
        {viewState === 'error' && (
          <div className="max-w-xl mx-auto mt-12">
            <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
              <div className="w-12 h-12 rounded-full bg-red-100 mx-auto flex items-center justify-center mb-3">
                <span className="text-red-500 text-2xl">!</span>
              </div>
              <h3 className="text-lg font-semibold text-red-800 mb-2">分析出错</h3>
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={handleReset}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
              >
                返回重试
              </button>
            </div>
          </div>
        )}

        {/* 结果视图 */}
        {viewState === 'result' && results.length > 0 && (
          <div>
            {/* 批量结果选择器 */}
            {results.length > 1 && (
              <div className="flex items-center gap-2 mb-6 flex-wrap">
                <span className="text-sm font-medium text-gray-500">分析结果:</span>
                {results.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentIndex(i)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      i === currentIndex
                        ? 'bg-brand text-white shadow-sm'
                        : 'bg-white text-gray-600 hover:bg-gray-100 border'
                    }`}
                  >
                    {demoNames[i] || `产品 ${i + 1}`}
                  </button>
                ))}
              </div>
            )}

            <AnalysisResult
              data={results[currentIndex]}
              fetchMeta={fetchMeta}
            />
          </div>
        )}
      </main>

      {/* ===== 页脚 ===== */}
      <footer className="border-t border-gray-200 py-4 text-center text-xs text-gray-400">
        Amazon Listing Analyzer — 仅供学习与研究用途
      </footer>
    </div>
  );
}
