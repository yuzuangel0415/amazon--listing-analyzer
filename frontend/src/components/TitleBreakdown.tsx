import type { TitleAnalysis } from '../types'; // 标题分析类型

// ===== 标题拆解组件的 Props =====
interface Props {
  data: TitleAnalysis; // 标题分析数据
  title: string; // 原始标题文本
}

// ===== 分词类型的标签映射：中文标签 + CSS 类名 =====
const TOKEN_LABELS: Record<string, { label: string; className: string }> = {
  brand: { label: '品牌', className: 'token-brand' }, // 品牌词用蓝色标签
  core_product: { label: '核心词', className: 'token-core' }, // 核心产品词
  attribute: { label: '属性', className: 'token-attribute' }, // 属性词
  scene_audience: { label: '场景/人群', className: 'token-scene' }, // 场景/人群词
  function: { label: '功能', className: 'token-function' }, // 功能词
  other: { label: '其他', className: 'token-other' }, // 其他词
};

export default function TitleBreakdown({ data, title }: Props) {
  return (
    <div className="space-y-4">
      {/* 原始标题展示 */}
      <div className="bg-gray-50 rounded-lg p-3">
        <p className="text-sm text-gray-700 leading-relaxed break-words">{title}</p> {/* 支持长词换行 */}
        <p className="text-xs text-gray-400 mt-1">{title.length} 字符</p> {/* 显示标题字符数 */}
      </div>

      {/* 分词归类标签：每个词用不同颜色标记其类型 */}
      <div>
        <p className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">分词归类</p>
        <div className="flex flex-wrap gap-1">
          {data.tokens.map((token, i) => (
            <span
              key={i}
              className={`token-tag ${TOKEN_LABELS[token.type]?.className || 'token-other'}`} // 根据类型应用颜色
              title={`${TOKEN_LABELS[token.type]?.label || token.type} (位置: ${token.position})`} // 悬停提示
            >
              {token.word}
            </span>
          ))}
        </div>
      </div>

      {/* 标题结构分解：5个维度的统计卡片 */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {/* 品牌词卡片 */}
        <div className="bg-amber-50 rounded-lg p-3 text-center">
          <p className="text-xs text-amber-600 font-semibold mb-1">品牌</p>
          <p className="text-sm font-bold text-amber-900">{data.brand || '—'}</p> {/* 无品牌则显示 — */}
        </div>
        {/* 核心产品词卡片 */}
        <div className="bg-blue-50 rounded-lg p-3 text-center">
          <p className="text-xs text-blue-600 font-semibold mb-1">核心产品词</p>
          <p className="text-sm font-bold text-blue-900">{data.core_product || '—'}</p>
        </div>
        {/* 属性词数量卡片 */}
        <div className="bg-emerald-50 rounded-lg p-3 text-center">
          <p className="text-xs text-emerald-600 font-semibold mb-1">属性词</p>
          <p className="text-sm font-bold text-emerald-900">{data.attributes.length || '—'}</p> {/* 显示数量 */}
        </div>
        {/* 场景/人群词数量卡片 */}
        <div className="bg-purple-50 rounded-lg p-3 text-center">
          <p className="text-xs text-purple-600 font-semibold mb-1">场景/人群</p>
          <p className="text-sm font-bold text-purple-900">{data.scenes.length || '—'}</p>
        </div>
        {/* 功能词数量卡片 */}
        <div className="bg-rose-50 rounded-lg p-3 text-center">
          <p className="text-xs text-rose-600 font-semibold mb-1">功能词</p>
          <p className="text-sm font-bold text-rose-900">{data.functions.length || '—'}</p>
        </div>
      </div>

      {/* AI 生成的结构总结 */}
      <div className="bg-gray-50 rounded-lg p-3">
        <p className="text-xs text-gray-500 font-semibold mb-1">结构总结</p>
        <p className="text-sm text-gray-700">{data.structure_summary}</p>
      </div>
    </div>
  );
}
