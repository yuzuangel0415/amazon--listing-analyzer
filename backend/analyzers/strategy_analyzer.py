# ===== 卖点策略分析器 =====
# 判断Listing的整体营销策略类型，评估各维度覆盖情况
import re
from models.schemas import StrategyAnalysis, StrategyType

# ===== Listing覆盖维度定义 =====
# 一个优秀的Listing应该在以下维度都有所体现
COVERAGE_DIMENSIONS = [
    "产品功能/参数",
    "材质/工艺",
    "尺寸/重量",
    "使用场景",
    "兼容性",
    "耐久性/质量",
    "设计/外观",
    "便携性",
    "易用性",
    "安全性",
    "环保/健康",
    "售后/保修",
    "性价比",
    "品牌/信任",
]

# ===== 各维度的关键词映射 =====
# 如果文本中出现以下关键词，则认为该维度已被覆盖
DIMENSION_KEYWORDS = {
    "产品功能/参数": ["function", "feature", "spec", "parameter", "功能", "参数", "规格",
                     "built-in", "equipped", "支持", "配备", "内置"],
    "材质/工艺": ["material", "made of", "premium", "fabric", "材质", "工艺", "材料",
                  "stainless", "aluminum", "silicone", "leather"],
    "尺寸/重量": ["size", "weight", "dimension", "compact", "lightweight", "尺寸", "重量",
                  "inch", "cm", "mm", "lbs", "kg", "oz"],
    "使用场景": ["use for", "perfect for", "ideal for", "场景", "适用", "适合",
                 "travel", "office", "home", "outdoor", "gym"],
    "兼容性": ["compatible", "works with", "支持", "兼容", "适用于",
               "ios", "android", "windows", "mac", "bluetooth"],
    "耐久性/质量": ["durable", "sturdy", "quality", "long-lasting", "耐磨", "耐用",
                    "质量", "reinforced", "heavy-duty"],
    "设计/外观": ["design", "style", "look", "color", "设计", "外观", "颜值",
                  "sleek", "elegant", "modern", "minimalist"],
    "便携性": ["portable", "foldable", "collapsible", "便携", "折叠", "轻便",
               "carry", "travel-friendly"],
    "易用性": ["easy to use", "easy setup", "simple", "convenient", "易用", "方便",
               "user-friendly", "intuitive", "plug and play"],
    "安全性": ["safe", "safety", "protection", "安全", "保护", "防护",
               "certified", "tested", "non-toxic", "BPA-free"],
    "环保/健康": ["eco-friendly", "organic", "natural", "环保", "有机", "天然",
                  "recyclable", "biodegradable", "sustainable"],
    "售后/保修": ["warranty", "guarantee", "return", "refund", "保修", "售后", "退换",
                  "customer service", "lifetime", "support"],
    "性价比": ["value", "affordable", "price", "cost", "性价比", "实惠", "划算",
               "budget-friendly", "worth", "save"],
    "品牌/信任": ["brand", "trusted", "reliable", "品牌", "信赖", "可靠",
                  "professional", "certified", "years of experience"],
}

# ===== 策略类型判定正则库 =====
# 通过正则匹配来判断Listing采用的是哪种营销策略
STRATEGY_PATTERNS = {
    StrategyType.FUNCTION_PARAM: [
        r"(specs?|parameter|specification|technical|feature|功能|参数|规格|技术)",
        r"(\d+\s*(w|watts?|mah|gb|tb|hz|ghz|inch|mm|cm|kg|g|lbs?|oz|ml|l))",
        r"(built[\s-]in|equipped|includes?|comes?\s*with|offers?|features?)",
        r"(performance|powerful|efficient|fast|speed|quick|rapid)",
    ],
    StrategyType.EMOTIONAL_EXPERIENCE: [
        r"(feel|experience|enjoy|love|comfortable|relax|calm|peace)",
        r"(luxury|luxurious|elegant|beautiful|stunning|premium|exquisite)",
        r"(transform|elevate|enhance|upgrade|improve)\s*(your|the)",
        r"(imagine|picture|dream|fantasy)",
    ],
    StrategyType.PAIN_POINT: [
        r"(tired\s*of|sick\s*of|frustrated|struggle|problem|issue|hassle)",
        r"(solve|solution|fix|eliminate|reduce|prevent|stop|end)",
        r"(no\s*more|never\s*again|finally|at\s*last)",
        r"(without|free\s*from|no)\s*(worry|stress|pain|mess|noise|clutter)",
    ],
    StrategyType.SOCIAL_PROOF: [
        r"(\d+[\s,]*\d*\s*(review|rating|customer|user|people|sold))",
        r"(best[\s-]seller|#\d+|top[\s-]rated|award|recommended|favorite)",
        r"(thousands|millions|countless|many)\s*(of|customers|users|people)",
        r"(trusted|proven|tested|verified|certified)",
    ],
    StrategyType.DIFFERENTIATION: [
        r"(unlike|compared?\s*to|better\s*than|superior|vs\.?|versus)",
        r"(unique|exclusive|patented|proprietary|only|first|innovative)",
        r"(no\s*other|nothing\s*else|don't\s*settle)",
        r"(difference|different|advantage|edge|outperform|outlast)",
        r"(revolutionary|game[\s-]changer|breakthrough|next[\s-]gen)",
    ],
}


# ===== 卖点策略分析主入口 =====
def analyze_strategy(title: str, bullets: list[str]) -> StrategyAnalysis:
    """
    从标题和五点描述中分析整体卖点策略。
    判断主策略/辅策略，计算差异化评分，分析维度覆盖。
    """
    combined = title + " " + " ".join(bullets)  # 合并标题和五点描述为完整文本
    lower = combined.lower()  # 统一转小写

    # 第1步：对五种策略类型分别打分（按正则匹配次数累加）
    scores: dict[StrategyType, int] = {}
    for stype, patterns in STRATEGY_PATTERNS.items():
        score = 0
        for pat in patterns:
            matches = re.findall(pat, lower)  # 在全文搜索匹配
            score += len(matches)  # 匹配次数作为得分
        scores[stype] = score

    # 第2步：按得分排序，确定主要策略和辅助策略
    sorted_strategies = sorted(scores.items(), key=lambda x: x[1], reverse=True)  # 降序排列
    primary = sorted_strategies[0][0] if sorted_strategies else StrategyType.FUNCTION_PARAM  # 得分最高的为主策略
    secondary = [s for s, score in sorted_strategies[1:3] if score > 0]  # 得分第2-3名且>0的为辅策略

    # 第3步：计算差异化评分
    # 高分 = 使用了更多独特/差异化的语言表达
    diff_indicators = len(re.findall(
        r"(unique|exclusive|patented|proprietary|only|first|innovative|"
        r"revolutionary|game[\s-]changer|breakthrough|unlike|better\s*than|"
        r"superior|outperform|outlast|no\s*other|don't\s*settle|"
        r"独家|专利|唯一|首创|创新|革命性)",  # 中英文差异化关键词
        lower
    ))
    diff_score = min(100, diff_indicators * 15 + 20)  # 基础分20 + 每个差异化词+15，上限100

    # 如果完全没有差异化表达，扣分
    if scores[StrategyType.DIFFERENTIATION] == 0:
        diff_score = max(10, diff_score - 25)  # 最少保留10分

    # 第4步：检查覆盖维度
    covered = []  # 已覆盖的维度
    missing = []  # 缺失的维度
    for dim, keywords in DIMENSION_KEYWORDS.items():
        if any(re.search(rf"\b{re.escape(kw)}\b", lower) for kw in keywords):  # 精确词边界匹配
            covered.append(dim)  # 有任一关键词匹配即视为覆盖
        else:
            missing.append(dim)  # 没有关键词匹配则为缺失

    # 第5步：生成中文摘要
    strategy_labels = {
        StrategyType.FUNCTION_PARAM: "功能参数型",
        StrategyType.EMOTIONAL_EXPERIENCE: "情感体验型",
        StrategyType.PAIN_POINT: "场景痛点型",
        StrategyType.SOCIAL_PROOF: "社交证明型",
        StrategyType.DIFFERENTIATION: "差异化对比型",
    }
    summary_parts = [f"主策略: {strategy_labels.get(primary, '其他')}"]
    if secondary:
        sec_labels = [strategy_labels.get(s, s.value) for s in secondary]
        summary_parts.append(f"辅策略: {', '.join(sec_labels)}")
    summary_parts.append(f"差异化评分: {diff_score}/100")
    if missing:
        summary_parts.append(f"缺失维度: {len(missing)}个")  # 提示维度覆盖不足

    return StrategyAnalysis(
        primary_strategy=primary,
        secondary_strategies=secondary,
        differentiation_score=diff_score,
        coverage_dimensions=covered,
        missing_dimensions=missing,
        strategy_summary=" | ".join(summary_parts),
    )
