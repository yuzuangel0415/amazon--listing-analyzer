import type { StrategyAnalysis, StrategyType } from '../types'; // 策略分析类型
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts'; // 雷达图组件
import { TrendingUp, Shield, AlertTriangle } from 'lucide-react'; // 图标库

// ===== 策略雷达图组件的 Props =====
interface Props {
  data: StrategyAnalysis; // 策略分析数据
}

// ===== 5种策略类型的中文标签映射 =====
const STRATEGY_LABELS: Record<StrategyType, string> = {
  function_param: '功能参数型', // 强调产品功能参数
  emotional_experience: '情感体验型', // 强调用户情感体验
  pain_point: '场景痛点型', // 解决使用场景中的痛点
  social_proof: '社交证明型', // 利用社会认可和口碑
  differentiation: '差异化对比型', // 与竞争对手对比突出优势
};

// ===== 5种策略对应的高亮颜色 =====
const STRATEGY_COLORS: Record<StrategyType, string> = {
  function_param: '#3b82f6', // 蓝色
  emotional_experience: '#ec4899', // 粉色
  pain_point: '#f97316', // 橙色
  social_proof: '#eab308', // 黄色
  differentiation: '#ef4444', // 红色
};

// ===== 根据策略分析结果构建雷达图数据 =====
// 评分规则：主导策略90分，辅助策略60分，未使用的策略20分
function buildRadarData(data: StrategyAnalysis) {
  const strategies: StrategyType[] = [
    'function_param', 'emotional_experience', 'pain_point', 'social_proof', 'differentiation',
  ]; // 所有5种策略类型
  return strategies.map(s => ({
    strategy: STRATEGY_LABELS[s], // 中文策略名（雷达图标签）
    score: s === data.primary_strategy ? 90 // 主导策略给最高分
         : data.secondary_strategies.includes(s) ? 60 // 辅助策略给中等分
         : 20, // 未使用策略给最低分
    fullMark: 100, // 满分100
    color: STRATEGY_COLORS[s], // 对应的颜色
  }));
}

// ===== 根据评分返回文字颜色类名 =====
function getScoreColor(score: number): string {
  if (score >= 70) return 'text-emerald-600'; // 高分：绿色
  if (score >= 40) return 'text-amber-600'; // 中等：黄色
  return 'text-red-600'; // 低分：红色
}

// ===== 根据评分返回背景颜色类名 =====
function getScoreBgColor(score: number): string {
  if (score >= 70) return 'bg-emerald-100'; // 高分：浅绿背景
  if (score >= 40) return 'bg-amber-100'; // 中等：浅黄背景
  return 'bg-red-100'; // 低分：浅红背景
}

export default function StrategyRadar({ data }: Props) {
  const radarData = buildRadarData(data); // 生成雷达图数据

  return (
    <div className="space-y-4">
      {/* ===== 雷达图可视化 ===== */}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData}>
            <PolarGrid stroke="#e5e7eb" /> {/* 雷达图的网格线 */}
            <PolarAngleAxis dataKey="strategy" tick={{ fontSize: 12, fill: '#6b7280' }} /> {/* 角度轴：显示策略名称 */}
            <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} /> {/* 半径轴：0-100，隐藏刻度 */}
            <Radar
              name="Strategy"
              dataKey="score" // 绑定的数据字段
              stroke="#8b5cf6" // 边框颜色（紫色）
              fill="#8b5cf6" // 填充颜色
              fillOpacity={0.2} // 填充透明度
              strokeWidth={2} // 边框粗细
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* ===== 主导策略徽章 ===== */}
      <div className="flex items-center gap-3">
        <span className="text-xs font-semibold text-gray-500">主导策略:</span>
        <span
          className="px-3 py-1 rounded-full text-sm font-bold text-white"
          style={{ backgroundColor: STRATEGY_COLORS[data.primary_strategy] }} // 动态颜色背景
        >
          {STRATEGY_LABELS[data.primary_strategy]}
        </span>
      </div>

      {/* ===== 辅助策略标签列表 ===== */}
      {data.secondary_strategies.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-semibold text-gray-500">辅助策略:</span>
          {data.secondary_strategies.map(s => (
            <span
              key={s}
              className="px-2.5 py-0.5 rounded-full text-xs font-medium border"
              style={{ borderColor: STRATEGY_COLORS[s], color: STRATEGY_COLORS[s] }} // 边框和文字同色
            >
              {STRATEGY_LABELS[s]}
            </span>
          ))}
        </div>
      )}

      {/* ===== 差异化程度评分 ===== */}
      <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-purple-500" /> {/* 趋势上升图标 */}
          <span className="text-sm font-semibold text-gray-700">差异化程度</span>
        </div>
        <div className="flex items-center gap-2">
          {/* 评分圆环 */}
          <div className={`score-ring ${getScoreBgColor(data.differentiation_score)}`}>
            <span className={`text-lg ${getScoreColor(data.differentiation_score)}`}>
              {data.differentiation_score}
            </span>
          </div>
          <span className="text-xs text-gray-400">/100</span> {/* 满分100 */}
        </div>
      </div>

      {/* ===== 已覆盖的卖点维度 ===== */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Shield className="w-4 h-4 text-emerald-500" /> {/* 盾牌图标 */}
          <span className="text-xs font-semibold text-gray-500">卖点覆盖维度</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {data.coverage_dimensions.map(dim => (
            <span key={dim} className="px-2 py-1 bg-emerald-50 text-emerald-700 rounded-md text-xs font-medium">
              ✓ {dim} {/* 打勾标记已覆盖 */}
            </span>
          ))}
        </div>
      </div>

      {/* ===== 缺失的卖点维度 ===== */}
      {data.missing_dimensions.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-amber-500" /> {/* 警告三角形图标 */}
            <span className="text-xs font-semibold text-gray-500">缺失维度 ({data.missing_dimensions.length})</span> {/* 缺失数量 */}
          </div>
          <div className="flex flex-wrap gap-1.5">
            {data.missing_dimensions.map(dim => (
              <span key={dim} className="px-2 py-1 bg-amber-50 text-amber-700 rounded-md text-xs font-medium">
                ✗ {dim} {/* 叉号标记缺失 */}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* ===== 策略分析总结文字 ===== */}
      <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-600">
        {data.strategy_summary}
      </div>
    </div>
  );
}
