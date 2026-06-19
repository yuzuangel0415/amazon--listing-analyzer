import type { BulletSetAnalysis, BulletType, SentencePattern } from '../types'; // 五点分析相关类型
import { ArrowRight } from 'lucide-react'; // 箭头图标

// ===== 五点描述拆解组件的 Props =====
interface Props {
  data: BulletSetAnalysis; // 五点描述整体分析数据
}

// ===== 卖点类型的中文标签映射 =====
const TYPE_LABELS: Record<BulletType, { label: string; emoji: string }> = {
  function: { label: '功能参数', emoji: '⚙️' },
  emotion: { label: '情感体验', emoji: '❤️' },
  data: { label: '数据支撑', emoji: '📊' },
  scene: { label: '场景描述', emoji: '🎯' },
  social_proof: { label: '社交证明', emoji: '🏆' },
  comparison: { label: '差异化对比', emoji: '⚡' },
};

// ===== 句式类型的中文标签映射 =====
const PATTERN_LABELS: Record<SentencePattern, string> = {
  function_statement: '功能陈述句', // 客观陈述产品功能
  emotional_appeal: '情感诉求句', // 引发情感共鸣
  data_support: '数据支撑句', // 用数据说话
  scene_description: '场景描述句', // 描绘使用场景
  social_proof: '社交证明句', // 引用社会认可
  comparison: '对比句式', // 与竞品对比
};

// ===== 卖点间关系的中文标签和颜色映射 =====
const RELATION_LABELS: Record<string, { label: string; color: string }> = {
  parallel: { label: '并列关系', color: 'bg-gray-100 text-gray-700' },
  progressive: { label: '递进关系', color: 'bg-blue-100 text-blue-700' },
  complementary: { label: '互补关系', color: 'bg-emerald-100 text-emerald-700' },
};

export default function BulletBreakdown({ data }: Props) {
  return (
    <div className="space-y-4">
      {/* ===== 每条卖点的分析卡片列表 ===== */}
      <div className="space-y-3">
        {data.bullets.map((bullet) => (
          <div key={bullet.index} className={`bullet-card bullet-${bullet.bullet_type}`}>
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                {/* 标签行：序号 + 卖点类型 + 句式类型 */}
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  {/* 序号标签 */}
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold bg-gray-100 text-gray-600">
                    #{bullet.index + 1}
                  </span>
                  {/* 卖点类型标签：带图标 */}
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-white/80">
                    {TYPE_LABELS[bullet.bullet_type]?.emoji} {TYPE_LABELS[bullet.bullet_type]?.label}
                  </span>
                  {/* 句式类型标签 */}
                  <span className="inline-flex px-2 py-0.5 rounded-full text-xs bg-white/60 text-gray-600">
                    {PATTERN_LABELS[bullet.sentence_pattern] || bullet.sentence_pattern}
                  </span>
                </div>

                {/* 卖点原文 */}
                <p className="text-sm text-gray-800 leading-relaxed">{bullet.text}</p>

                {/* 提取的关键词列表 */}
                {bullet.keywords.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {bullet.keywords.map((kw, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 bg-white/80 rounded text-xs text-gray-600 border border-gray-200"
                      >
                        {kw}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* ===== 卖点间逻辑关系展示 ===== */}
      {data.relations.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">卖点逻辑关系</p>
          <div className="flex flex-wrap items-center gap-2">
            {data.relations.map((rel, i) => (
              <div key={i} className="flex items-center gap-1.5">
                {/* 来源卖点编号 */}
                <span className="text-xs font-bold text-gray-600">#{rel.from_index + 1}</span>
                <ArrowRight className="w-3 h-3 text-gray-400" /> {/* 箭头表示方向 */}
                {/* 目标卖点编号 */}
                <span className="text-xs font-bold text-gray-600">#{rel.to_index + 1}</span>
                {/* 关系类型标签 */}
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${RELATION_LABELS[rel.relation]?.color}`}>
                  {RELATION_LABELS[rel.relation]?.label}
                </span>
                {/* 多条关系之间用竖线分隔 */}
                {i < data.relations.length - 1 && <span className="text-gray-300 mx-1">|</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ===== 整体结构总结 ===== */}
      <div className="bg-gray-50 rounded-lg p-3 flex items-center gap-2">
        <span className="text-xs text-gray-500 font-semibold">整体结构:</span>
        <span className="text-sm text-gray-700">{data.overall_structure}</span>
      </div>
    </div>
  );
}
