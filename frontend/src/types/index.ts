// ===== 枚举类型：与后端 Python 枚举一一对应 =====

// 标题词汇分类：品牌词 / 核心产品词 / 属性词 / 场景/人群词 / 功能词 / 其他
export type TokenType = 'brand' | 'core_product' | 'attribute' | 'scene_audience' | 'function' | 'other';
// 五点描述类型：功能参数 / 情感体验 / 数据支撑 / 场景描述 / 社交证明 / 差异化对比
export type BulletType = 'function' | 'emotion' | 'data' | 'scene' | 'social_proof' | 'comparison';
// 句式类型：功能陈述句 / 情感诉求句 / 数据支撑句 / 场景描述句 / 社交证明句 / 对比句式
export type SentencePattern = 'function_statement' | 'emotional_appeal' | 'data_support' | 'scene_description' | 'social_proof' | 'comparison';
// 卖点策略类型：功能参数型 / 情感体验型 / 场景痛点型 / 社交证明型 / 差异化对比型
export type StrategyType = 'function_param' | 'emotional_experience' | 'pain_point' | 'social_proof' | 'differentiation';
// 卖点之间的关系：并列 / 递进 / 互补
export type BulletRelation = 'parallel' | 'progressive' | 'complementary';
// 输入模式：文本 / URL链接 / ASIN码 / Excel文件
export type InputMode = 'text' | 'url' | 'asin' | 'excel';

// ===== 标题分析相关类型 =====

// 标题分词结果中的单个词汇及其分类
export interface TitleToken {
  word: string; // 词汇文本
  type: TokenType; // 词汇类型
  position: number; // 在标题中的位置索引
}

// 标题整体分析结果
export interface TitleAnalysis {
  tokens: TitleToken[]; // 所有分词结果
  brand: string | null; // 品牌词
  core_product: string | null; // 核心产品词
  attributes: string[]; // 属性词列表
  scenes: string[]; // 场景/人群词列表
  functions: string[]; // 功能词列表
  structure_summary: string; // 标题结构总结文字
}

// ===== 五点描述分析相关类型 =====

// 单条卖点 Bullet 的分析结果
export interface BulletAnalysisItem {
  index: number; // 在五点描述中的序号（从0开始）
  text: string; // 原始文本
  bullet_type: BulletType; // 卖点类型
  sentence_pattern: SentencePattern; // 句式类型
  keywords: string[]; // 提取的关键词
  summary: string; // 该条卖点的总结
}

// 两条卖点之间的关系
export interface BulletRelationItem {
  from_index: number; // 来源卖点序号
  to_index: number; // 目标卖点序号
  relation: BulletRelation; // 关系类型
}

// 五点描述的整体分析结果
export interface BulletSetAnalysis {
  bullets: BulletAnalysisItem[]; // 每条卖点的分析
  relations: BulletRelationItem[]; // 卖点之间的逻辑关系
  overall_structure: string; // 整体结构描述
}

// ===== 卖点策略分析相关类型 =====

// 策略分析结果
export interface StrategyAnalysis {
  primary_strategy: StrategyType; // 主导策略（最突出的一个）
  secondary_strategies: StrategyType[]; // 辅助策略（次要的多个）
  differentiation_score: number; // 差异化程度评分（0-100）
  coverage_dimensions: string[]; // 已覆盖的卖点维度
  missing_dimensions: string[]; // 缺失的卖点维度
  strategy_summary: string; // 策略总结文字
}

// ===== 关键词与 SEO 分析相关类型 =====

// 单个词汇的出现频率
export interface WordFrequency {
  word: string; // 词汇
  count: number; // 出现次数
  rank: number; // 频率排名
}

// 关键词覆盖度分析
export interface KeywordCoverage {
  core_words: string[]; // 核心词列表
  long_tail_words: string[]; // 长尾词列表
  attribute_words: string[]; // 属性词列表
  coverage_ratio: number; // 覆盖度比例（0-1）
}

// SEO 评分明细
export interface SeoScore {
  title_length_score: number; // 标题长度评分（0-100）
  keyword_position_score: number; // 关键词位置评分（0-100）
  bullet_distribution_score: number; // 关键词分布评分（0-100）
  overall_score: number; // 综合 SEO 评分（0-100）
  suggestions: string[]; // 优化建议列表
}

// 关键词分析整体结果
export interface KeywordAnalysis {
  word_frequencies: WordFrequency[]; // 词频统计
  coverage: KeywordCoverage; // 覆盖度
  seo_score: SeoScore; // SEO 评分
  top_keywords: string[]; // 排名最高的关键词
}

// ===== 统一响应类型 =====

// 标准分析响应（文本输入和文件上传共用）
export interface AnalysisResponse {
  title: string; // 产品标题
  bullets: string[]; // 五点描述列表
  title_analysis: TitleAnalysis; // 标题分析结果
  bullet_analysis: BulletSetAnalysis; // 五点描述分析结果
  strategy_analysis: StrategyAnalysis; // 策略分析结果
  keyword_analysis: KeywordAnalysis; // 关键词分析结果
}

// URL/ASIN 抓取分析的响应——继承标准分析结果，额外包含商品元数据
export interface FetchResponse extends AnalysisResponse {
  fetched: boolean; // 是否成功抓取
  asin: string; // 商品 ASIN 码
  price: string; // 价格
  rating: string; // 评分
  reviews_count: string; // 评论数量
  images: string[]; // 商品图片 URL 列表
}

// Excel 批量上传的响应
export interface UploadResponse {
  total: number; // 总共分析的产品数量
  results: AnalysisResponse[]; // 每个产品的分析结果数组
}
