# ===== 五点描述分析器 =====
# 对亚马逊商品页的每条五点描述进行分类（内容类型 + 句式类型）并分析关系
import re
from models.schemas import (
    BulletAnalysis, BulletSetAnalysis, BulletType,
    SentencePattern, BulletRelation,
)

# ===== 功能参数型正则匹配 =====
FUNCTION_PATTERNS = [
    (r"(built[\s-]in|equipped|features?|comes?\s*with|includes?|offers?|provides?)",
     BulletType.FUNCTION),
    (r"(material|made\s*of|constructed|fabric|premium|high[\s-]quality|durable|sturdy)",
     BulletType.FUNCTION),
    (r"(dimensions?|size|weight|measures?|weighs?|length|width|height|diameter)",
     BulletType.FUNCTION),
    (r"(battery|charge|power|capacity|voltage|watt|mah|hours?\s*of)",
     BulletType.FUNCTION),
    (r"(compatible|works?\s*with|supports?|connect|pair)",
     BulletType.FUNCTION),
    (r"(waterproof|water[\s-]resistant|ipx?\d+|dustproof|shockproof)",
     BulletType.FUNCTION),
    (r"(adjustable|foldable|collapsible|detachable|removable|replaceable|rotatable)",
     BulletType.FUNCTION),
    (r"(usb|bluetooth|wifi|wireless|wired|port|jack|aux|hdmi)",
     BulletType.FUNCTION),
]

# ===== 情感体验型正则匹配 =====
EMOTION_PATTERNS = [
    (r"(feel|feeling|experience|enjoy|comfortable|comfort|cozy|relax|relaxing)",
     BulletType.EMOTION),
    (r"(love|like|adore|delight|pleasure|satisfaction|happy)",
     BulletType.EMOTION),
    (r"(luxury|luxurious|elegant|beautiful|stunning|gorgeous|stylish|sleek)",
     BulletType.EMOTION),
    (r"(peace|calm|quiet|serene|tranquil|soothe|soothing)",
     BulletType.EMOTION),
    (r"(confidence|confident|proud|pride|impress|impressive)",
     BulletType.EMOTION),
]

# ===== 数据支撑型正则匹配 =====
DATA_PATTERNS = [
    (r"(\d+\s*(%|percent|times?|x|hours?|mins?|minutes?|days?|weeks?|months?|years?))",
     BulletType.DATA),
    (r"(up\s*to\s*\d+|over\s*\d+|more\s*than\s*\d+|less\s*than\s*\d+|at\s*least\s*\d+)",
     BulletType.DATA),
    (r"(\d+\s*(w|watts?|mah|gb|tb|mb|kb|oz|lbs?|pounds?|kg|grams?|inches?|inch|feet|ft|cm|mm|ml|l))",
     BulletType.DATA),
    (r"(tested|proven|rated|certified|guaranteed|warranty)",
     BulletType.DATA),
]

# ===== 场景描述型正则匹配 =====
SCENE_PATTERNS = [
    (r"(perfect\s*for|ideal\s*for|great\s*for|suitable\s*for|designed\s*for|made\s*for)",
     BulletType.SCENE),
    (r"(use\s*(it|this)\s*(for|in|at|when|while|during)|(for|in|at|when|while|during)\s*(your|the))",
     BulletType.SCENE),
    (r"(travel|office|home|kitchen|bedroom|bathroom|outdoor|gym|garden|camping|hiking|beach|party)",
     BulletType.SCENE),
    (r"(everyday|daily|routine|morning|night|weekend|vacation|holiday|trips?)",
     BulletType.SCENE),
    (r"(gift|present|birthday|christmas|wedding|anniversary|valentine)",
     BulletType.SCENE),
]

# ===== 社交证明型正则匹配 =====
SOCIAL_PROOF_PATTERNS = [
    (r"(\d+[\s,]*\d*\s*(review|rating|star|customer|buyer|user|people|sold|purchased))",
     BulletType.SOCIAL_PROOF),
    (r"(best[\s-]seller|#\d+|top[\s-]rated|award|recommended|favorite|popular|trusted)",
     BulletType.SOCIAL_PROOF),
    (r"(amazon|choice|prime|fba|fulfilled)",
     BulletType.SOCIAL_PROOF),
    (r"(certified|approved|tested|verified|guaranteed|warranty|lifetime)",
     BulletType.SOCIAL_PROOF),
    (r"(doctor|dentist|veterinarian|chef|professional|expert|recommended)",
     BulletType.SOCIAL_PROOF),
]

# ===== 差异化对比型正则匹配 =====
COMPARISON_PATTERNS = [
    (r"(unlike|compared?\s*to|better\s*than|superior|vs\.?|versus|instead\s*of)",
     BulletType.COMPARISON),
    (r"(other|traditional|ordinary|regular|standard|conventional|competitor)",
     BulletType.COMPARISON),
    (r"(unique|exclusive|patented|proprietary|only|first|original|innovative)",
     BulletType.COMPARISON),
    (r"(no\s*other|nothing\s*else|no\s*one\s*else|don't\s*settle)",
     BulletType.COMPARISON),
    (r"(difference|different|advantage|edge|outperform|outlast|outshine)",
     BulletType.COMPARISON),
]

# ===== 句式分类正则匹配（根据语法结构） =====
SENTENCE_PATTERNS = {
    SentencePattern.FUNCTION_STATEMENT: [
        r"^(built|equipped|features?|comes?\s*with|includes?|offers?|provides?|has|have|made\s*of|constructed)",
    ],
    SentencePattern.EMOTIONAL_APPEAL: [
        r"^(feel|imagine|experience|enjoy|love|you'll|you\s*will)",
        r"!(?!\s*$)",
    ],
    SentencePattern.DATA_SUPPORT: [
        r"\d+[\s]*(%|percent|times?|x|hours?|mins?|days?|weeks?|months?)",
        r"(up\s*to|over|more\s*than|less\s*than|approximately|about|nearly)\s*\d+",
    ],
    SentencePattern.SCENE_DESCRIPTION: [
        r"^(perfect\s*for|ideal\s*for|great\s*for|designed\s*for|made\s*for|use\s*(it|this))",
    ],
    SentencePattern.SOCIAL_PROOF: [
        r"(\d+[\s,]*\d*\s*(review|rating|star|customer|buyer|people))",
        r"(best[\s-]seller|#\d+|top[\s-]rated|award|recommended|favorite|popular|trusted)",
    ],
    SentencePattern.COMPARISON: [
        r"^(unlike|compared?\s*to|better\s*than|superior|while\s*other)",
    ],
}


# ===== 关键词提取 =====
# 从描述文本中提取有意义的关键词，去除停用词
def extract_keywords(text: str) -> list[str]:
    """从五点描述文本中提取关键词（去除停用词和短词）"""
    # 英文常见停用词表（冠词、介词、代词等无实际意义的词）
    stop_words = {
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
        "their", "and", "but", "or", "if", "while",
    }
    words = re.findall(r"[a-zA-Z0-9]+(?:[-'][a-zA-Z0-9]+)*", text.lower())  # 正则提取单词（保留连字符连接词）
    keywords = [w for w in words if w not in stop_words and len(w) > 1]  # 过滤停用词和单字符词
    return list(dict.fromkeys(keywords))[:8]  # 去重后最多返回8个关键词


# ===== 五点描述分类核心函数 =====
# 根据文本内容同时判定内容类型和句式类型
def classify_bullet(text: str) -> tuple[BulletType, SentencePattern]:
    """将一条五点描述分类为内容类型 + 句式类型"""
    lower = text.lower()  # 统一转小写便于匹配
    scores: dict[BulletType, int] = {bt: 0 for bt in BulletType}  # 内容类型得分初始化
    pattern_scores: dict[SentencePattern, int] = {sp: 0 for sp in SentencePattern}  # 句式类型得分初始化

    # 第1步：对六种内容类型分别打分（每条正则匹配到就加1分）
    for patterns, btype in [
        (FUNCTION_PATTERNS, BulletType.FUNCTION),
        (EMOTION_PATTERNS, BulletType.EMOTION),
        (DATA_PATTERNS, BulletType.DATA),
        (SCENE_PATTERNS, BulletType.SCENE),
        (SOCIAL_PROOF_PATTERNS, BulletType.SOCIAL_PROOF),
        (COMPARISON_PATTERNS, BulletType.COMPARISON),
    ]:
        for pat, bt in patterns:
            if re.search(pat, lower):
                scores[bt] += 1  # 匹配成功，对应类型得分+1

    # 第2步：对六种句式分别打分
    for sp, patterns in SENTENCE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, lower):
                pattern_scores[sp] += 1

    # 确定最佳内容类型（得分最高的类型）
    best_type = max(scores, key=scores.get)
    if scores[best_type] == 0:
        best_type = BulletType.FUNCTION  # 所有类型都无匹配时，默认功能型

    # 确定句式类型（优先选择数据/社交/对比等强句式，功能陈述句作为兜底）
    data_priority = [SentencePattern.DATA_SUPPORT, SentencePattern.SOCIAL_PROOF,
                      SentencePattern.COMPARISON, SentencePattern.EMOTIONAL_APPEAL,
                      SentencePattern.SCENE_DESCRIPTION, SentencePattern.FUNCTION_STATEMENT]
    best_pattern = SentencePattern.FUNCTION_STATEMENT  # 默认句式
    for sp in data_priority:
        if pattern_scores[sp] > 0:
            best_pattern = sp  # 按优先级取第一个有得分的句式
            break

    # 特殊情况：如果内容类型强烈指向数据型，句式也强制设为数据支撑句
    if best_type == BulletType.DATA and pattern_scores[SentencePattern.DATA_SUPPORT] > 0:
        best_pattern = SentencePattern.DATA_SUPPORT

    return best_type, best_pattern


# ===== 五点描述关系分析 =====
# 分析相邻两条描述之间的逻辑关系
def analyze_relations(bullets: list[BulletAnalysis]) -> list[dict]:
    """分析相邻五点描述之间的关系（并列/递进/互补）"""
    relations = []
    for i in range(len(bullets) - 1):
        a, b = bullets[i], bullets[i + 1]  # 取出相邻的两条
        # 类型相同 → 并列关系
        if a.bullet_type == b.bullet_type:
            rel = BulletRelation.PARALLEL
        # 功能型后面跟数据型 → 互补关系（数据为功能提供证据）
        elif a.bullet_type == BulletType.FUNCTION and b.bullet_type == BulletType.DATA:
            rel = BulletRelation.COMPLEMENTARY
        # 功能型后面跟场景型 → 互补关系
        elif a.bullet_type == BulletType.FUNCTION and b.bullet_type == BulletType.SCENE:
            rel = BulletRelation.COMPLEMENTARY
        # 不同类型 → 递进关系（逐步展开论述）
        else:
            rel = BulletRelation.PROGRESSIVE
        relations.append({
            "from_index": i,  # 前一条的索引
            "to_index": i + 1,  # 后一条的索引
            "relation": rel.value,  # 关系类型字符串值
        })
    return relations


# ===== 五点描述分析主入口 =====
# 对五条描述逐条分类，分析关系，评估整体结构
def analyze_bullets(bullets: list[str]) -> BulletSetAnalysis:
    results: list[BulletAnalysis] = []
    for i, text in enumerate(bullets):
        if not text.strip():
            continue  # 跳过空行
        btype, spattern = classify_bullet(text)  # 对每条描述做内容和句式分类
        keywords = extract_keywords(text)  # 提取关键词
        # 中文标签映射，用于生成摘要
        type_labels = {
            BulletType.FUNCTION: "功能参数",
            BulletType.EMOTION: "情感体验",
            BulletType.DATA: "数据支撑",
            BulletType.SCENE: "场景描述",
            BulletType.SOCIAL_PROOF: "社交证明",
            BulletType.COMPARISON: "差异化对比",
        }
        pattern_labels = {
            SentencePattern.FUNCTION_STATEMENT: "功能陈述句",
            SentencePattern.EMOTIONAL_APPEAL: "情感诉求句",
            SentencePattern.DATA_SUPPORT: "数据支撑句",
            SentencePattern.SCENE_DESCRIPTION: "场景描述句",
            SentencePattern.SOCIAL_PROOF: "社交证明句",
            SentencePattern.COMPARISON: "对比句式",
        }
        summary = f"[{type_labels.get(btype, '其他')}] {pattern_labels.get(spattern, '')}"  # 组装中文摘要标签
        results.append(BulletAnalysis(
            index=i,
            text=text,
            bullet_type=btype,
            sentence_pattern=spattern,
            keywords=keywords,
            summary=summary,
        ))

    relations = analyze_relations(results)  # 分析相邻描述关系

    # 统计各类型出现次数，判断整体结构
    type_counts = {}
    for r in results:
        type_counts[r.bullet_type.value] = type_counts.get(r.bullet_type.value, 0) + 1
    dominant = max(type_counts, key=type_counts.get) if type_counts else "function"  # 最多出现的类型即为整体结构

    # 整体结构中文评估
    structure_desc = {
        "function": "以功能参数为主导，适合功能性产品",
        "emotion": "以情感体验为主导，适合生活方式产品",
        "data": "以数据支撑为主导，强调可量化优势",
        "scene": "以场景描述为主导，帮助用户想象使用场景",
        "social_proof": "以社交证明为主导，利用从众心理",
        "comparison": "以差异化对比为主导，突出竞争优势",
    }

    return BulletSetAnalysis(
        bullets=results,
        relations=relations,
        overall_structure=structure_desc.get(dominant, "混合结构"),  # 返回整体结构描述
    )
