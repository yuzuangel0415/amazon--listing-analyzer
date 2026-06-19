import type { KeywordAnalysis } from '../types'; // 关键词分析类型
import { TrendingUp, Target, BarChart3, Lightbulb, CheckCircle } from 'lucide-react'; // 图标库

// ===== 关键词云组件的 Props =====
interface Props {
  data: KeywordAnalysis; // 关键词分析数据
  title: string; // 原始标题（备用）
  bullets: string[]; // 原始五点描述（备用）
}

// ===== 评分进度条子组件 =====
// 用于展示各维度 SEO 评分，包含标签、分数、进度条和说明
function ScoreBar({ label, score, description }: { label: string; score: number; description: string }) {
  // 根据分数决定进度条颜色：>=80绿，>=60黄，<60红
  const color = score >= 80 ? 'bg-emerald-500' : score >= 60 ? 'bg-amber-500' : 'bg-red-500';
  const textColor = score >= 80 ? 'text-emerald-700' : score >= 60 ? 'text-amber-700' : 'text-red-700';

  return (
    <div className="space-y-1.5">
      {/* 标签和分数 */}
      <div className="flex justify-between items-center">
        <span className="text-xs font-medium text-gray-600">{label}</span>
        <span className={`text-xs font-bold ${textColor}`}>{score}</span> {/* 分数颜色随值变化 */}
      </div>
      {/* 进度条：宽度百分比由 score 决定 */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className={`h-2 rounded-full transition-all duration-500 ${color}`} style={{ width: `${score}%` }} />
      </div>
      {/* 评分说明 */}
      <p className="text-xs text-gray-400">{description}</p>
    </div>
  );
}

export default function KeywordCloud({ data }: Props) {
  // 解构关键词分析数据
  const { seo_score, word_frequencies, top_keywords, coverage } = data;

  return (
    <div className="space-y-4">
      {/* ===== 综合 SEO 评分：圆环进度图 + 文字 ===== */}
      <div className="bg-gradient-to-br from-emerald-50 to-blue-50 rounded-xl p-4 flex items-center justify-between">
        <div>
          <p className="text-sm font-bold text-gray-800">综合 SEO 评分</p>
          <p className="text-xs text-gray-500 mt-0.5">标题 + 五点 关键词优化评估</p>
        </div>
        {/* SVG 圆环进度：通过 strokeDasharray 控制弧长 */}
        <div className="relative w-20 h-20 flex items-center justify-center">
          <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80"> {/* -90度旋转让进度从顶部开始 */}
            <circle cx="40" cy="40" r="34" fill="none" stroke="#e5e7eb" strokeWidth="6" /> {/* 灰色底环 */}
            <circle
              cx="40" cy="40" r="34"
              fill="none"
              stroke={seo_score.overall_score >= 80 ? '#10b981' : seo_score.overall_score >= 60 ? '#f59e0b' : '#ef4444'} // 颜色根据分数
              strokeWidth="6"
              strokeLinecap="round" // 圆角端点
              strokeDasharray={`${seo_score.overall_score * 2.14} 214`} // 2.14 = 圆周长214/100，转换为百分比
            />
          </svg>
          {/* 评分数字 */}
          <span className={`absolute text-lg font-bold ${
            seo_score.overall_score >= 80 ? 'text-emerald-600' : seo_score.overall_score >= 60 ? 'text-amber-600' : 'text-red-600'
          }`}>
            {seo_score.overall_score}
          </span>
        </div>
      </div>

      {/* ===== SEO 评分明细：三个维度的进度条 ===== */}
      <div className="space-y-3">
        <div className="flex items-center gap-1.5">
          <BarChart3 className="w-4 h-4 text-gray-500" /> {/* 柱状图图标 */}
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">评分明细</span>
        </div>
        {/* 标题长度评分 */}
        <ScoreBar label="标题长度" score={seo_score.title_length_score} description="80-160字符为最佳范围" />
        {/* 关键词位置评分 */}
        <ScoreBar label="关键词位置" score={seo_score.keyword_position_score} description="核心词在标题中的前置程度" />
        {/* 关键词分布评分 */}
        <ScoreBar label="关键词分布" score={seo_score.bullet_distribution_score} description="五点描述的关键词覆盖密度" />
      </div>

      {/* ===== 高频关键词标签云 ===== */}
      <div>
        <div className="flex items-center gap-1.5 mb-2">
          <Target className="w-4 h-4 text-gray-500" /> {/* 靶心图标 */}
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">高频关键词</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {/* 取前15个高频词展示 */}
          {word_frequencies.slice(0, 15).map((wf) => {
            // 根据出现次数决定字体大小：>5次用大号，>2次用中号
            const size = wf.count > 5 ? 'text-base font-bold' : wf.count > 2 ? 'text-sm font-semibold' : 'text-xs';
            // 根据出现次数决定透明度（出现越多越不透明）
            const opacity = Math.min(1, 0.4 + wf.count * 0.1);
            return (
              <span
                key={wf.word}
                className={`px-2.5 py-1 bg-gray-100 rounded-full ${size} text-gray-700 hover:bg-brand/10 hover:text-brand transition-colors cursor-default`}
                style={{ opacity }} // 动态透明度
                title={`出现 ${wf.count} 次`} // 悬停提示
              >
                {wf.word}
                <span className="ml-1 text-xs text-gray-400">×{wf.count}</span> {/* 出现次数 */}
              </span>
            );
          })}
        </div>
      </div>

      {/* ===== 关键词覆盖度统计：核心词/长尾词/属性词 ===== */}
      <div className="grid grid-cols-3 gap-2">
        {/* 核心词数量 */}
        <div className="bg-blue-50 rounded-lg p-2.5 text-center">
          <p className="text-xs text-blue-500 font-semibold">核心词</p>
          <p className="text-lg font-bold text-blue-700">{coverage.core_words.length}</p>
        </div>
        {/* 长尾词数量 */}
        <div className="bg-purple-50 rounded-lg p-2.5 text-center">
          <p className="text-xs text-purple-500 font-semibold">长尾词</p>
          <p className="text-lg font-bold text-purple-700">{coverage.long_tail_words.length}</p>
        </div>
        {/* 属性词数量 */}
        <div className="bg-emerald-50 rounded-lg p-2.5 text-center">
          <p className="text-xs text-emerald-500 font-semibold">属性词</p>
          <p className="text-lg font-bold text-emerald-700">{coverage.attribute_words.length}</p>
        </div>
      </div>

      {/* ===== 关键词覆盖度比例进度条 ===== */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-xs text-gray-500">关键词覆盖度:</span>
        <div className="flex-1 bg-gray-200 rounded-full h-2">
          <div
            className="h-2 rounded-full bg-gradient-to-r from-blue-400 to-purple-500 transition-all" // 渐变色进度条
            style={{ width: `${coverage.coverage_ratio * 100}%` }} // coverage_ratio 是0-1，转百分比
          />
        </div>
        <span className="text-xs font-bold text-gray-700">{Math.round(coverage.coverage_ratio * 100)}%</span>
      </div>

      {/* ===== SEO 优化建议列表 ===== */}
      <div>
        <div className="flex items-center gap-1.5 mb-2">
          <Lightbulb className="w-4 h-4 text-amber-500" /> {/* 灯泡图标 */}
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">优化建议</span>
        </div>
        <div className="space-y-1.5">
          {seo_score.suggestions.map((suggestion, i) => (
            <div key={i} className="flex items-start gap-2 text-sm bg-amber-50 rounded-lg p-2.5">
              <CheckCircle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" /> {/* 勾选图标 */}
              <span className="text-amber-800">{suggestion}</span> {/* 建议文字 */}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
