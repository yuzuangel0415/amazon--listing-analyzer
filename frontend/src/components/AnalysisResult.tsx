import type { AnalysisResponse, FetchResponse } from '../types'; // 类型定义
import TitleBreakdown from './TitleBreakdown'; // 标题拆解子组件
import BulletBreakdown from './BulletBreakdown'; // 五点描述拆解子组件
import StrategyRadar from './StrategyRadar'; // 策略雷达图子组件
import KeywordCloud from './KeywordCloud'; // 关键词云子组件
import { Star, DollarSign, MessageSquare, Package } from 'lucide-react'; // 图标库

// ===== 分析结果面板的 Props 类型 =====
interface Props {
  data: AnalysisResponse; // 核心分析数据
  fetchMeta: Partial<FetchResponse> | null; // 商品元数据（仅 URL/ASIN 抓取时有值）
}

export default function AnalysisResult({ data, fetchMeta }: Props) {
  return (
    <div className="space-y-6">
      {/* ===== 商品信息栏：仅当通过 URL/ASIN 抓取时显示 ===== */}
      {fetchMeta && (
        <div className="bg-white rounded-xl shadow-sm border p-4 flex flex-wrap items-center gap-4">
          {/* 商品主图：加载失败时隐藏 */}
          {fetchMeta.images && fetchMeta.images[0] && (
            <img
              src={fetchMeta.images[0]}
              alt={data.title}
              className="w-16 h-16 object-contain rounded-lg border bg-gray-50"
              onError={e => { (e.target as HTMLImageElement).style.display = 'none'; }} // 图片加载失败时隐藏
            />
          )}
          <div className="flex-1 min-w-0">
            {/* 商品标题：超长时截断显示 */}
            <h2 className="text-sm font-medium text-gray-900 truncate">{data.title}</h2>
            {/* 商品元数据行：ASIN / 价格 / 评分 / 评论数 */}
            <div className="flex items-center gap-4 mt-1.5 text-xs text-gray-500">
              {fetchMeta.asin && (
                <span className="flex items-center gap-1">
                  <Package className="w-3 h-3" /> ASIN: {fetchMeta.asin}
                </span>
              )}
              {fetchMeta.price && (
                <span className="flex items-center gap-1">
                  <DollarSign className="w-3 h-3" /> {fetchMeta.price}
                </span>
              )}
              {fetchMeta.rating && (
                <span className="flex items-center gap-1 text-amber-600">
                  <Star className="w-3 h-3 fill-amber-400" /> {fetchMeta.rating} {/* 评分用星形图标 */}
                </span>
              )}
              {fetchMeta.reviews_count && (
                <span className="flex items-center gap-1">
                  <MessageSquare className="w-3 h-3" /> {fetchMeta.reviews_count}
                </span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ===== 分析结果网格：大屏两列，小屏一列 ===== */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 标题拆解板块：横跨整行 */}
        <section className="bg-white rounded-xl shadow-sm border p-5 lg:col-span-2">
          <h3 className="text-base font-bold text-gray-900 mb-3 flex items-center gap-2">
            <span className="w-1.5 h-5 bg-brand rounded-full" /> {/* 左侧彩色指示条 */}
            标题结构拆解
          </h3>
          <TitleBreakdown data={data.title_analysis} title={data.title} />
        </section>

        {/* 五点描述拆解板块：横跨整行 */}
        <section className="bg-white rounded-xl shadow-sm border p-5 lg:col-span-2">
          <h3 className="text-base font-bold text-gray-900 mb-3 flex items-center gap-2">
            <span className="w-1.5 h-5 bg-blue-500 rounded-full" /> {/* 左侧蓝色指示条 */}
            五点描述拆解
          </h3>
          <BulletBreakdown data={data.bullet_analysis} />
        </section>

        {/* 卖点策略分析板块：左侧半宽 */}
        <section className="bg-white rounded-xl shadow-sm border p-5">
          <h3 className="text-base font-bold text-gray-900 mb-3 flex items-center gap-2">
            <span className="w-1.5 h-5 bg-purple-500 rounded-full" /> {/* 左侧紫色指示条 */}
            卖点策略分析
          </h3>
          <StrategyRadar data={data.strategy_analysis} />
        </section>

        {/* 关键词与 SEO 板块：右侧半宽 */}
        <section className="bg-white rounded-xl shadow-sm border p-5">
          <h3 className="text-base font-bold text-gray-900 mb-3 flex items-center gap-2">
            <span className="w-1.5 h-5 bg-emerald-500 rounded-full" /> {/* 左侧绿色指示条 */}
            关键词密度 & SEO评分
          </h3>
          <KeywordCloud data={data.keyword_analysis} title={data.title} bullets={data.bullets} />
        </section>
      </div>
    </div>
  );
}
