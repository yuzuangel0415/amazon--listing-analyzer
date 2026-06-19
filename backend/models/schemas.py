# ===== 导入依赖 =====
from pydantic import BaseModel, Field  # Pydantic 数据验证和序列化
from typing import Optional  # 可选字段类型
from enum import Enum  # 枚举基类

# ===== 输入模式枚举 =====
class InputMode(str, Enum):
    TEXT = "text"  # 手动粘贴文本模式
    URL = "url"  # 亚马逊商品链接抓取模式
    ASIN = "asin"  # 根据ASIN码抓取模式
    EXCEL = "excel"  # 批量上传Excel模式

# ===== API 请求模型 =====
class AnalyzeRequest(BaseModel):
    mode: InputMode  # 输入模式（text/url/asin/excel）
    title: Optional[str] = ""  # 手动输入的标题文本
    bullets: Optional[list[str]] = []  # 手动输入的五点描述列表
    url: Optional[str] = ""  # 亚马逊商品页面URL
    asin: Optional[str] = ""  # 亚马逊商品ASIN码
    marketplace: str = "com"  # 亚马逊市场站点（默认美国站 .com）

class BatchItem(BaseModel):
    title: str  # Excel批量导入的单条标题
    bullets: list[str] = []  # Excel批量导入的单条五点描述

class UploadResponse(BaseModel):
    total: int  # Excel解析出的总条数
    items: list[dict]  # 解析出的原始条目列表


# ===== 标题分析数据模型 =====
# 标题Token类型枚举：将标题中每个词分类为品牌/核心产品/属性/场景/功能/其他
class TokenType(str, Enum):
    BRAND = "brand"  # 品牌词（如 Apple, Anker）
    CORE_PRODUCT = "core_product"  # 核心产品词（如 headphones, charger）
    ATTRIBUTE = "attribute"  # 属性修饰词（如 wireless, waterproof）
    SCENE_AUDIENCE = "scene_audience"  # 场景/人群词（如 gaming, for kids）
    FUNCTION = "function"  # 功能词（如 with mic, noise cancelling）
    OTHER = "other"  # 其他未分类词汇

class TitleToken(BaseModel):
    word: str  # 单词原文
    type: TokenType  # 分类类型
    position: int  # 在标题中的位置序号（从0开始）

class TitleAnalysis(BaseModel):
    tokens: list[TitleToken]  # 所有分词及分类结果
    brand: Optional[str] = None  # 识别出的品牌名
    core_product: Optional[str] = None  # 识别出的核心产品
    attributes: list[str] = []  # 识别出的属性描述列表
    scenes: list[str] = []  # 识别出的场景/人群列表
    functions: list[str] = []  # 识别出的功能描述列表
    structure_summary: str = ""  # 标题结构中文摘要


# ===== 五点描述分析数据模型 =====
# 五点描述的类型分类：每条描述归类为功能/情感/数据/场景/社交证明/对比
class BulletType(str, Enum):
    FUNCTION = "function"  # 功能参数型（材质、尺寸、电池、兼容性等）
    EMOTION = "emotion"  # 情感体验型（舒适、享受、奢华等）
    DATA = "data"  # 数据支撑型（具体数字、百分比、测试认证等）
    SCENE = "scene"  # 场景描述型（送礼、旅行、办公等使用场景）
    SOCIAL_PROOF = "social_proof"  # 社交证明型（好评、销量、获奖、推荐等）
    COMPARISON = "comparison"  # 差异化对比型（优于竞品、独家专利等）

# 句子句式枚举：根据语法结构和修辞手法分类
class SentencePattern(str, Enum):
    FUNCTION_STATEMENT = "function_statement"  # 功能陈述句（直述参数特点）
    EMOTIONAL_APPEAL = "emotional_appeal"  # 情感诉求句（唤起情绪感受）
    DATA_SUPPORT = "data_support"  # 数据支撑句（引用数据证据）
    SCENE_DESCRIPTION = "scene_description"  # 场景描述句（描绘使用场景）
    SOCIAL_PROOF = "social_proof"  # 社交证明句（引用他人认可）
    COMPARISON = "comparison"  # 对比句式（与竞品或传统方案对比）

class BulletAnalysis(BaseModel):
    index: int  # 描述的位置序号（0-4）
    text: str  # 描述的原文内容
    bullet_type: BulletType  # 内容类型
    sentence_pattern: SentencePattern  # 句式类型
    keywords: list[str]  # 提取的关键词
    summary: str = ""  # 摘要（中文标签）

# 五点描述之间的关系类型
class BulletRelation(str, Enum):
    PARALLEL = "parallel"  # 并列关系：相邻两条类型相同
    PROGRESSIVE = "progressive"  # 递进关系：不同类型的描述内容
    COMPLEMENTARY = "complementary"  # 互补关系：数据描述对功能描述做补充

class BulletSetAnalysis(BaseModel):
    bullets: list[BulletAnalysis]  # 五条描述各自的详细分析
    relations: list[dict] = []  # 相邻描述之间的关系
    overall_structure: str = ""  # 整体结构评估（如"以功能参数为主导"）


# ===== 卖点策略分析数据模型 =====
# Listing整体采用的主要卖点策略
class StrategyType(str, Enum):
    FUNCTION_PARAM = "function_param"  # 功能参数型：以产品参数/功能打动用户
    EMOTIONAL_EXPERIENCE = "emotional_experience"  # 情感体验型：唤起用户的情感和向往
    PAIN_POINT = "pain_point"  # 场景痛点型：先指出痛点，再给解决方案
    SOCIAL_PROOF = "social_proof"  # 社交证明型：利用销量/好评/推荐建立信任
    DIFFERENTIATION = "differentiation"  # 差异化对比型：突出与竞品的不同

class StrategyAnalysis(BaseModel):
    primary_strategy: StrategyType  # 主要策略（得分最高的策略类型）
    secondary_strategies: list[StrategyType] = []  # 辅助策略（得分次高的1-2种）
    differentiation_score: int = Field(ge=0, le=100)  # 差异化程度评分（0-100分）
    coverage_dimensions: list[str] = []  # 已覆盖的维度（如功能、材质、场景等）
    missing_dimensions: list[str] = []  # 缺失的维度（建议补充的方面）
    strategy_summary: str = ""  # 策略摘要中文描述


# ===== 关键词SEO分析数据模型 =====
# 单词词频统计
class WordFrequency(BaseModel):
    word: str  # 单词
    count: int  # 出现次数
    rank: int  # 频率排名（1为最高频）

# 关键词覆盖度分类（核心词/长尾词/属性词）
class KeywordCoverage(BaseModel):
    core_words: list[str] = []  # 核心关键词（短词、产品通用词）
    long_tail_words: list[str] = []  # 长尾关键词（场景/人群组合词）
    attribute_words: list[str] = []  # 属性关键词（技术规格/材质等）
    coverage_ratio: float = 0.0  # 综合覆盖度比率（0.0 ~ 1.0）

# SEO评分维度
class SeoScore(BaseModel):
    title_length_score: int = Field(ge=0, le=100)  # 标题长度得分
    keyword_position_score: int = Field(ge=0, le=100)  # 关键词位置得分
    bullet_distribution_score: int = Field(ge=0, le=100)  # 五点关键词分布得分
    overall_score: int = Field(ge=0, le=100)  # 综合SEO评分
    suggestions: list[str] = []  # 优化建议列表

class KeywordAnalysis(BaseModel):
    word_frequencies: list[WordFrequency] = []  # 词频统计列表
    coverage: KeywordCoverage  # 关键词覆盖度
    seo_score: SeoScore  # SEO评分
    top_keywords: list[str] = []  # 排名前10的Top关键词


# ===== 统一分析响应模型 =====
# 将四个分析维度的结果打包成一个完整响应
class AnalysisResponse(BaseModel):
    title: str  # 原始标题
    bullets: list[str]  # 原始五点描述
    title_analysis: TitleAnalysis  # 标题结构化分析结果
    bullet_analysis: BulletSetAnalysis  # 五点描述类型分析结果
    strategy_analysis: StrategyAnalysis  # 卖点策略分析结果
    keyword_analysis: KeywordAnalysis  # 关键词SEO分析结果
