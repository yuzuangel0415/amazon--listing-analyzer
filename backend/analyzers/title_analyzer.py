# ===== 标题分析器 =====
# 将亚马逊商品标题拆解为品牌、核心产品、属性、场景、功能等结构化信息
import re
from models.schemas import TitleToken, TitleAnalysis, TokenType

# ===== 已知品牌名称库（可扩展） =====
# 匹配标题第一个词是否为已知品牌
KNOWN_BRANDS = {
    "apple", "samsung", "sony", "bose", "anker", "xiaomi", "huawei",
    "ugreen", "baseus", "aukey", "tp-link", "netgear", "dyson",
    "irobot", "philips", "braun", "panasonic", "lg", "dell", "hp",
    "lenovo", "asus", "acer", "logitech", "razer", "corsair",
    "intel", "amd", "nvidia", "gskyer", "celestron", "lego",
    "nike", "adidas", "under armour", "puma", "new balance",
    "kitchenaid", "instant pot", "ninja", "vitamix", "breville",
    "oxo", "pyrex", "thermos", "yeti", "hydro flask", "stanley",
    "apple", "google", "amazon", "ring", "blink", "wyze",
    "fujifilm", "canon", "nikon", "gopro", "dji", "insta360",
}

# ===== 核心产品类型词库 =====
# 如果标题中出现这些词，则识别为核心产品
PRODUCT_INDICATORS = {
    "headphones", "earbuds", "earphones", "speaker", "speakers",
    "camera", "lens", "tripod", "gimbal", "drone",
    "keyboard", "mouse", "monitor", "laptop", "tablet",
    "phone", "smartphone", "charger", "cable", "adapter", "hub",
    "vacuum", "cleaner", "purifier", "fan", "heater", "ac",
    "blender", "mixer", "toaster", "oven", "cooker", "grill",
    "backpack", "bag", "wallet", "purse", "suitcase", "luggage",
    "watch", "band", "tracker", "scale", "thermometer",
    "light", "lamp", "bulb", "strip", "string light",
    "bottle", "mug", "cup", "container", "jar", "lunch box",
    "toy", "game", "puzzle", "block", "doll", "figure",
    "tool", "drill", "saw", "screwdriver", "wrench",
    "supplement", "vitamin", "protein", "powder", "pill",
    "cream", "serum", "oil", "mask", "cleanser", "sunscreen",
    "mat", "dumbbell", "band", "rope", "roller", "yoga",
    "book", "notebook", "journal", "planner", "calendar",
    "case", "cover", "protector", "screen protector",
    "stand", "mount", "holder", "hanger", "hook", "rack",
    "pad", "cushion", "pillow", "mattress", "topper",
    "curtain", "blind", "rug", "carpet", "mat",
    "diffuser", "humidifier", "dehumidifier", "essential oil",
}

# ===== 属性修饰词正则匹配规则 =====
# 通过正则表达式识别属性类词汇（尺寸、颜色、技术规格、材质等）
ATTRIBUTE_PATTERNS = [
    r"(wireless|bluetooth|wired|usb[\s-]?c|usb[\s-]?a|aux)",
    r"(noise\s*cancell?ing|anc|noise\s*reduc)",
    r"(waterproof|water[\s-]resistant|ipx?\d+)",
    r"(portable|compact|mini|small|large|big|slim|thin)",
    r"(rechargeable|battery[\s-]powered|cordless)",
    r"(heavy[\s-]duty|lightweight|durable|sturdy)",
    r"(foldable|collapsible|adjustable|extendable)",
    r"(stainless|aluminum|plastic|wood|glass|metal)",
    r"(organic|natural|vegan|gluten[\s-]free)",
    r"(high[\s-]speed|fast[\s-]charging|quick[\s-]charge)",
    r"(hd|4k|1080p|8k|uhd|full\s*hd)",
    r"(smart|wifi|bluetooth|app[\s-]controlled)",
    r"(automatic|digital|analog|manual|electric)",
    r"(professional|commercial|industrial|home)",
    r"\d+\s*(w|watts?|mah|gb|tb|inch|inches|cm|mm|oz|lbs?)",
]

# ===== 场景/人群正则匹配规则 =====
# 识别使用场景（如 gaming, office）和目标人群（如 men, kids）
SCENE_PATTERNS = [
    r"(for|适合)\s*(running|gaming|office|home|travel|outdoor|camping|hiking|sports?|work|study|kitchen|bedroom|bathroom|living\s*room|cooking|baking|workout|exercise|yoga|fitness|swimming|cycling|driving|car)",
    r"(gift|present)\s*(for|给)",
    r"(men|women|kids?|children|baby|toddler|adult|teen|boy|girl|senior|elderly)",
    r"(mother|father|mom|dad|parent|grandma|grandpa)",
    r"(birthday|christmas|valentine|anniversary|wedding|graduation)",
    r"(indoor|outdoor|both)",
]

# ===== 功能/特性正则匹配规则 =====
# 识别功能描述（如 with mic, supports Bluetooth, easy to use）
FUNCTION_PATTERNS = [
    r"(with|w/|featuring|includes?|built[\s-]in|equipped\s*with)\s*(mic|microphone|remote|timer|display|screen|led|light|speaker|fan|cooling|heating|gps|bluetooth|wifi)",
    r"(supports?|compatible\s*with|works?\s*with)\s*[\w\s]+",
    r"(\d+\s*in\s*1|multi[\s-]function|multipurpose|all[\s-]in[\s-]one)",
    r"(easy[\s-]to[\s-]use|easy[\s-]clean|easy[\s-]install|easy[\s-]setup)",
    r"(washable|removable|detachable|replaceable)",
]


# ===== 语言检测 =====
def detect_language(text: str) -> str:
    """根据中文字符占比粗略判断语言（中文或英文）"""
    chinese_chars = len(re.findall(r"[一-鿿]", text))  # 统计中文字符数量
    if chinese_chars > len(text) * 0.15:  # 超过15%为中文字符则判定为中文
        return "zh"
    return "en"  # 否则按英文处理


# ===== 中文分词 =====
def tokenize_zh(text: str) -> list[str]:
    """中文分词：优先使用 jieba 库，不可用时回退到简单空格分词"""
    try:
        import jieba
        return list(jieba.cut(text))  # jieba 精确模式分词
    except ImportError:
        return text.split()  # 降级方案：按空格简单分割

# ===== 英文分词 =====
def tokenize_en(text: str) -> list[str]:
    """英文分词：按空格和常用分隔符拆分，保留引号内的词组"""
    tokens = re.findall(r'"[^"]*"|\'[^\']*\'|[^\s,\-|/()\[\]{}]+', text)
    return [t.strip('"\'') for t in tokens if t.strip()]  # 去除引号并过滤空字符串


# ===== 复合属性词精确匹配库 =====
# 用于直接匹配已知的属性修饰词（包含颜色、材质、防护等级等）
COMPOSITE_ATTRIBUTE_WORDS = {
    "wireless", "bluetooth", "wired", "noise", "cancelling", "canceling",
    "noise-cancelling", "noise-canceling", "anc", "waterproof",
    "water-resistant", "ipx4", "ipx5", "ipx6", "ipx7", "ipx8",
    "portable", "compact", "mini", "lightweight", "heavy-duty",
    "rechargeable", "cordless", "foldable", "collapsible", "adjustable",
    "premium", "durable", "sturdy", "slim", "thin", "large", "small",
    "high-speed", "fast-charging", "quick-charge", "quick", "rapid",
    "hd", "4k", "1080p", "8k", "uhd", "smart", "wifi", "app-controlled",
    "automatic", "digital", "electric", "professional", "commercial",
    "organic", "natural", "vegan", "eco-friendly", "non-toxic", "bpa-free",
    "stainless", "aluminum", "silicone", "leather", "metal", "wood",
    "ergonomic", "anti-slip", "slip-resistant", "scratch-resistant",
    "rust-resistant", "corrosion-resistant", "heat-resistant",
    "dustproof", "shockproof", "shatterproof", "leakproof",
    "hypoallergenic", "fragrance-free", "unscented",
    "black", "white", "red", "blue", "green", "yellow", "pink", "purple",
    "orange", "grey", "gray", "brown", "silver", "gold", "rose", "navy",
    "beige", "teal", "clear", "transparent", "matte", "glossy",
    "comfort", "comfortable", "soft", "breathable",
}

# ===== 复合功能词精确匹配库 =====
COMPOSITE_FUNCTION_WORDS = {
    "mic", "microphone", "remote", "timer", "display", "screen", "led",
    "speaker", "fan", "cooling", "heating", "gps", "bluetooth",
    "charging", "charge", "battery", "connectivity", "connection",
    "compatible", "supports", "multi-device", "multipoint",
}

# ===== 复合场景/人群词精确匹配库 =====
COMPOSITE_SCENE_WORDS = {
    "running", "gaming", "office", "home", "travel", "outdoor", "camping",
    "hiking", "sports", "work", "study", "kitchen", "bedroom", "bathroom",
    "living-room", "workout", "exercise", "yoga", "fitness", "swimming",
    "cycling", "driving", "car", "everyday", "daily", "indoor",
    "gift", "men", "women", "kids", "child", "children", "baby",
    "toddler", "adult", "teen", "boy", "girl", "senior",
    "birthday", "christmas", "valentine", "anniversary", "wedding",
    "school", "dorm", "apartment", "beach", "pool", "garden", "party",
    "trip", "vacation", "commuting", "backpacking", "fishing",
    "home-office", "desk", "table", "counter", "wall",
}


# ===== Token分类核心函数 =====
# 根据单词内容、位置和上下文，判断该词属于哪种类型
def classify_token(token: str, position: int, total: int, first_token: str = "") -> TokenType:
    """将单个Token分类为品牌/核心产品/属性/场景/功能/其他"""
    lower = token.lower().strip(",.!;:()[]{}'\"- ")  # 清洗标点符号

    if not lower:
        return TokenType.OTHER  # 空字符串直接归为其他

    # 短连接词（介词、冠词、连词）—— 始终归为 OTHER
    if lower in {"with", "for", "and", "or", "the", "a", "an", "in", "on",
                  "at", "to", "of", "by", "&", "-", "/", "|", "no", "not"}:
        return TokenType.OTHER

    # 品牌识别：仅当位于第0位且匹配已知品牌库时才判定为品牌
    if position == 0 and lower in {b.lower() for b in KNOWN_BRANDS}:
        return TokenType.BRAND

    # 核心产品识别——优先级最高，因为最具体
    if lower in PRODUCT_INDICATORS:
        return TokenType.CORE_PRODUCT

    # 兼容复数形式（如 headphones -> headphone）
    singular = lower.rstrip("s")
    if singular in PRODUCT_INDICATORS:
        return TokenType.CORE_PRODUCT

    # 复合属性词精确匹配
    if lower in COMPOSITE_ATTRIBUTE_WORDS:
        return TokenType.ATTRIBUTE

    # 属性正则匹配
    for pat in ATTRIBUTE_PATTERNS:
        if re.match(pat, lower):
            return TokenType.ATTRIBUTE

    # 复合功能词精确匹配
    if lower in COMPOSITE_FUNCTION_WORDS:
        return TokenType.FUNCTION

    # 功能正则匹配
    for pat in FUNCTION_PATTERNS:
        if re.match(pat, lower):
            return TokenType.FUNCTION

    # 场景/人群精确匹配
    if lower in COMPOSITE_SCENE_WORDS:
        return TokenType.SCENE_AUDIENCE

    # 场景/人群正则匹配
    for pat in SCENE_PATTERNS:
        if re.match(pat, lower):
            return TokenType.SCENE_AUDIENCE

    # 包含数字的词通常是属性（型号、规格参数）
    if re.search(r"\d", lower):
        return TokenType.ATTRIBUTE

    # 大写字母开头的词（非首位）通常是产品描述符/属性
    if len(lower) > 2 and lower[0].isupper():
        return TokenType.ATTRIBUTE

    return TokenType.OTHER  # 以上都不匹配则归为其他


# ===== 标题分析主入口 =====
def analyze_title(title: str) -> TitleAnalysis:
    """分析商品标题：分词 -> 分类 -> 汇总结构化信息"""
    # 第1步：检测语言并分词
    lang = detect_language(title)
    tokens_raw = tokenize_zh(title) if lang == "zh" else tokenize_en(title)

    total = len(tokens_raw)  # 总词数
    first_token = tokens_raw[0].lower() if tokens_raw else ""  # 首词用于品牌匹配

    # 第2步：遍历每个词，调用 classify_token 进行分类
    tokens: list[TitleToken] = []
    for i, token in enumerate(tokens_raw):
        token = token.strip()
        if not token or token in {",", ".", "!", "?", "-", "–", "—", "/", "|", "&"}:
            continue  # 跳过纯标点符号
        tt = classify_token(token, i, total, first_token)  # 核心分类调用
        tokens.append(TitleToken(word=token, type=tt, position=i))

    # 第3步：按类型汇总提取信息
    brand = next((t.word for t in tokens if t.type == TokenType.BRAND), None)  # 提取品牌名
    core = next((t.word for t in tokens if t.type == TokenType.CORE_PRODUCT), None)  # 提取核心产品
    attrs = [t.word for t in tokens if t.type == TokenType.ATTRIBUTE]  # 所有属性描述
    scenes = [t.word for t in tokens if t.type == TokenType.SCENE_AUDIENCE]  # 所有场景/人群
    funcs = [t.word for t in tokens if t.type == TokenType.FUNCTION]  # 所有功能描述

    # 第4步：生成中文结构摘要
    parts = []
    if brand:
        parts.append(f"品牌: {brand}")
    if core:
        parts.append(f"核心产品: {core}")
    if attrs:
        parts.append(f"属性: {', '.join(attrs)}")
    if scenes:
        parts.append(f"场景/人群: {', '.join(scenes)}")
    if funcs:
        parts.append(f"功能: {', '.join(funcs)}")
    summary = " | ".join(parts) if parts else "无法识别标题结构"  # 合成最终摘要

    return TitleAnalysis(
        tokens=tokens,
        brand=brand,
        core_product=core,
        attributes=attrs,
        scenes=scenes,
        functions=funcs,
        structure_summary=summary,
    )
