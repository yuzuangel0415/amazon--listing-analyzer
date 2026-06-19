# ===== 关键词SEO分析器 =====
# 统计词频、分类关键词、评估SEO得分
import re
from collections import Counter  # 高效词频统计工具
from models.schemas import (
    KeywordAnalysis, WordFrequency, KeywordCoverage, SeoScore,
)

# ===== 英文停用词表 =====
# 这些词在SEO分析中没有意义，需要过滤掉
STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "can", "shall",
    "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above",
    "below", "between", "out", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "just", "because",
    "about", "up", "down", "this", "that", "these", "those",
    "it", "its", "you", "your", "we", "our", "they", "them",
    "their", "and", "but", "or", "if", "while", "which", "who",
    "what", "also", "any", "every", "per", "get", "got", "put",
    "set", "let", "make", "made", "use", "used", "using",
    "need", "one", "two", "three", "way", "back", "yet",
}

# ===== 技术属性词库 =====
# 识别技术规格类属性词（连接方式、分辨率、协议等）
TECH_ATTRIBUTE_WORDS = {
    "wireless", "bluetooth", "wifi", "usb", "type-c", "usb-c",
    "hdmi", "displayport", "thunderbolt", "lightning",
    "noise-cancelling", "noise-canceling", "anc", "waterproof",
    "water-resistant", "ipx", "ip", "rechargeable", "fast-charging",
    "quick-charge", "wireless-charging", "qi", "magsafe",
    "4k", "8k", "1080p", "uhd", "hdr", "dolby", "atmos",
    "smart", "alexa", "google-assistant", "siri", "homekit",
    "app-controlled", "voice-control", "touch-screen", "led",
    "rgb", "mechanical", "optical", "laser", "infrared",
    "dual-band", "tri-band", "mesh", "gigabit", "10g",
    "5g", "lte", "gps", "nfc",
}

# ===== 生活方式属性词库 =====
# 识别生活品质/设计风格类属性词（便携、环保、奢华等）
LIFESTYLE_ATTRIBUTE_WORDS = {
    "portable", "lightweight", "compact", "foldable", "collapsible",
    "durable", "sturdy", "heavy-duty", "premium", "luxury",
    "elegant", "modern", "minimalist", "vintage", "rustic",
    "organic", "natural", "vegan", "eco-friendly", "sustainable",
    "biodegradable", "recyclable", "reusable", "non-toxic",
    "BPA-free", "phthalate-free", "paraben-free",
    "hypoallergenic", "dermatologist-tested", "clinically-proven",
    "easy-to-use", "user-friendly", "beginner-friendly",
    "professional-grade", "commercial-grade", "industrial-grade",
}

# ===== 场景词库 =====
# 识别使用场景词（这些通常属于长尾关键词）
SCENE_WORDS = {
    "travel", "office", "home-office", "work-from-home", "bedroom",
    "bathroom", "kitchen", "living-room", "outdoor", "indoor",
    "camping", "hiking", "backpacking", "beach", "pool",
    "gym", "workout", "yoga", "running", "cycling", "swimming",
    "gaming", "streaming", "vlogging", "photography",
    "cooking", "baking", "grilling", "bbq",
    "garden", "lawn", "patio", "balcony",
    "car", "truck", "rv", "boat",
    "pet", "dog", "cat", "baby", "toddler", "kids",
}


# ===== 英文分词与清洗 =====
# 将文本拆分为有意义的单词列表，自动过滤停用词
def tokenize(text: str) -> list[str]:
    """英文分词：提取单词，保留连字符复合词，过滤停用词"""
    text = text.lower()  # 统一小写标准化
    words = re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)*", text)  # 提取单词（保留 hyphens 和撇号如 noise-cancelling）
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]  # 过滤停用词和单字符词


# ===== 关键词分类 =====
# 将单词分为核心词、长尾词、属性词三类
def classify_keyword(word: str) -> str:
    """关键词分类：core（核心词）/ long_tail（长尾词）/ attribute（属性词）"""
    if word in TECH_ATTRIBUTE_WORDS or word in LIFESTYLE_ATTRIBUTE_WORDS:
        return "attribute"  # 匹配技术属性或生活方式属性词库 → 属性词
    if word in SCENE_WORDS:
        return "long_tail"  # 匹配场景词库 → 长尾词
    # 启发式规则：长词往往是长尾关键词
    if len(word) > 12:
        return "long_tail"  # 超过12个字符的单词 → 长尾词
    if "-" in word:
        return "long_tail"  # 包含连字符的复合词 → 长尾词
    return "core"  # 其余归为核心词


# ===== 关键词SEO分析主入口 =====
def analyze_keywords(title: str, bullets: list[str]) -> KeywordAnalysis:
    """
    从标题和五点描述中分析关键词密度和SEO质量。
    包括：词频统计、关键词覆盖度、SEO各维度评分。
    """
    # 合并所有文本
    all_text = title + " " + " ".join(bullets)
    title_words = tokenize(title)  # 标题独立分词
    bullet_words = tokenize(" ".join(bullets))  # 五点描述独立分词
    all_words = tokenize(all_text)  # 全文本分词

    # 第1步：词频统计
    word_counts = Counter(all_words)  # 使用Counter统计每个单词出现的次数
    sorted_words = word_counts.most_common(30)  # 取词频最高的30个词

    frequencies = []  # 构建WordFrequency对象列表
    for rank, (word, count) in enumerate(sorted_words, 1):  # rank从1开始
        frequencies.append(WordFrequency(word=word, count=count, rank=rank))

    # 第2步：关键词覆盖度分析（将高频词按类别分组）
    core_words = []  # 核心关键词
    long_tail_words = []  # 长尾关键词
    attribute_words = []  # 属性关键词

    for word, count in sorted_words:
        category = classify_keyword(word)  # 分类判断
        if category == "core":
            core_words.append(word)
        elif category == "long_tail":
            long_tail_words.append(word)
        else:
            attribute_words.append(word)

    # 计算关键词覆盖度比率（长尾词权重最高，核心词次之，属性词较低）
    total_unique = len(sorted_words)
    coverage_ratio = 0.0
    if total_unique > 0:
        coverage_ratio = round(
            (len(core_words) * 1.0 + len(long_tail_words) * 1.5 + len(attribute_words) * 0.8)
            / (total_unique * 1.1), 2  # 加权计算覆盖度
        )
    coverage_ratio = min(1.0, coverage_ratio)  # 上限1.0

    coverage = KeywordCoverage(
        core_words=core_words[:8],  # 最多8个核心词
        long_tail_words=long_tail_words[:8],  # 最多8个长尾词
        attribute_words=attribute_words[:8],  # 最多8个属性词
        coverage_ratio=coverage_ratio,
    )

    # 第3步：SEO评分（三个维度）
    # 维度A：标题长度评分（亚马逊最佳长度80-160字符）
    title_length = len(title)
    title_length_score = 100
    if title_length < 60:
        title_length_score = int(title_length / 60 * 80)  # 过短按比例扣分
    elif title_length > 200:
        title_length_score = max(50, 100 - (title_length - 200) // 2)  # 过长按超出量扣分
    elif 80 <= title_length <= 160:
        title_length_score = 100  # 最佳长度区间满分
    else:
        title_length_score = 90  # 中间区间90分

    # 维度B：关键词位置评分（核心词是否出现在标题中）
    title_word_set = set(title_words)  # 标题分词集合（去重后用于快速查找）
    core_in_title = sum(1 for w in core_words[:10] if w in title_word_set)  # 统计前10核心词在标题中的出现数量
    keyword_position_score = min(100, core_in_title * 20 + 40)  # 基础40分 + 每个出现+20分，上限100

    # 维度C：五点描述关键词分布评分
    bullet_scores = []
    for bullet in bullets:
        bw = tokenize(bullet)  # 每条描述独立分词
        unique_kw = len(set(bw))  # 不重复关键词数量
        bullet_scores.append(min(25, unique_kw * 2))  # 每条最多25分（约12个不重复词即可满分）
    bullet_distribution_score = min(100, sum(bullet_scores))  # 五条总分上限100

    # 加权计算综合SEO得分
    overall = int(
        title_length_score * 0.3  # 标题长度占30%
        + keyword_position_score * 0.4  # 关键词位置占40%（权重最高）
        + bullet_distribution_score * 0.3  # 五点分布占30%
    )

    # 第4步：生成SEO优化建议
    suggestions = []
    if title_length < 60:
        suggestions.append("标题偏短，建议扩充至80-160字符，包含更多核心关键词")
    elif title_length > 200:
        suggestions.append("标题过长，建议精简至160字符以内，移动端会被截断")
    if core_in_title < 3:
        suggestions.append("核心关键词在标题中出现较少，建议将主要搜索词前置")
    if bullet_distribution_score < 50:
        suggestions.append("五点描述关键词覆盖不足，建议每条融入2-3个相关关键词")
    if len(long_tail_words) < 3:
        suggestions.append("长尾关键词较少，建议加入场景/人群/用途相关的长尾词")
    if not suggestions:
        suggestions.append("整体SEO表现良好，关键词布局合理")  # 各项指标均达标

    # 提取Top 10关键词
    top_keywords = [w for w, _ in sorted_words[:10]]

    return KeywordAnalysis(
        word_frequencies=frequencies,  # 词频统计
        coverage=coverage,  # 关键词覆盖度
        seo_score=SeoScore(
            title_length_score=title_length_score,
            keyword_position_score=keyword_position_score,
            bullet_distribution_score=bullet_distribution_score,
            overall_score=overall,  # 综合SEO评分
            suggestions=suggestions,  # 优化建议
        ),
        top_keywords=top_keywords,
    )
