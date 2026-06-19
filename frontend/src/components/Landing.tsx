import { Sparkles, ArrowRight, Play, Search, FileText, BarChart3, Globe } from 'lucide-react';

interface Props {
  onStartAnalysis: () => void;  // 进入分析工具
  onDemo: () => void;           // 一键演示
  loading: boolean;             // 正在加载演示数据
}

export default function Landing({ onStartAnalysis, onDemo, loading }: Props) {
  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center px-4">
      {/* 主标题 */}
      <div className="text-center max-w-3xl">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-brand/10 text-brand rounded-full text-sm font-medium mb-6">
          <Sparkles className="w-4 h-4" />
          Amazon Listing 分析工具
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 tracking-tight leading-tight">
          一眼看穿竞品 Listing
          <br />
          <span className="text-brand">找到你的优化方向</span>
        </h1>

        <p className="mt-4 text-lg text-gray-500 max-w-xl mx-auto leading-relaxed">
          输入任意亚马逊产品标题和五点描述，自动拆解标题结构、分析卖点策略、
          评估关键词布局与 SEO 得分，帮助运营人员快速优化 Listing。
        </p>

        {/* 核心功能标签 */}
        <div className="flex flex-wrap justify-center gap-3 mt-6">
          {[
            { icon: Search, label: '标题结构拆解' },
            { icon: FileText, label: '五点卖点分析' },
            { icon: BarChart3, label: '卖点策略评估' },
            { icon: Globe, label: '关键词SEO评分' },
          ].map(({ icon: Icon, label }) => (
            <span
              key={label}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 rounded-lg text-sm text-gray-600 font-medium"
            >
              <Icon className="w-4 h-4" />
              {label}
            </span>
          ))}
        </div>

        {/* 操作按钮 */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-8">
          <button
            onClick={onDemo}
            disabled={loading}
            className="w-full sm:w-auto px-8 py-3.5 bg-brand hover:bg-brand-dark disabled:bg-gray-400 text-white font-bold rounded-xl transition-all shadow-lg shadow-brand/25 hover:shadow-brand/40 flex items-center justify-center gap-2 text-base"
          >
            {loading ? (
              <><div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> 加载演示中...</>
            ) : (
              <><Play className="w-5 h-5" /> 一键演示</>
            )}
          </button>
          <button
            onClick={onStartAnalysis}
            className="w-full sm:w-auto px-8 py-3.5 bg-white hover:bg-gray-50 text-gray-700 font-semibold rounded-xl border-2 border-gray-200 hover:border-gray-300 transition-all flex items-center justify-center gap-2 text-base"
          >
            手动输入分析
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-3">
          无需注册 · 免费使用 · 数据不上传服务器
        </p>
      </div>

      {/* 技术栈标签 */}
      <div className="mt-12 text-center">
        <p className="text-xs text-gray-400 mb-3 uppercase tracking-wider">Built with</p>
        <div className="flex flex-wrap justify-center gap-2">
          {[
            'React', 'TypeScript', 'TailwindCSS', 'FastAPI', 'Python',
            'Recharts', 'jieba 分词', 'BeautifulSoup',
          ].map((tech) => (
            <span
              key={tech}
              className="px-2.5 py-1 bg-white border border-gray-200 rounded-md text-xs text-gray-500 font-medium shadow-sm"
            >
              {tech}
            </span>
          ))}
        </div>
      </div>

      {/* 底部信息（可自定义） */}
      <div className="mt-12 text-center text-xs text-gray-400 space-y-1">
        <p>此工具仅用于学习与研究用途</p>
        <p>
          <a href="#" className="hover:text-gray-600 underline underline-offset-2">
            GitHub
          </a>
          <span className="mx-2">·</span>
          <a href="#" className="hover:text-gray-600 underline underline-offset-2">
            关于作者
          </a>
        </p>
      </div>
    </div>
  );
}
