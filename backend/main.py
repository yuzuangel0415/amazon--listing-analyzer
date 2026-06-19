# ===== 导入依赖 =====
from fastapi import FastAPI, UploadFile, File, HTTPException  # FastAPI 核心模块
from fastapi.middleware.cors import CORSMiddleware  # 跨域请求中间件
from models.schemas import (
    AnalyzeRequest, BatchItem, AnalysisResponse, InputMode,  # 数据模型
)
from analyzers.title_analyzer import analyze_title  # 标题分析器
from analyzers.bullet_analyzer import analyze_bullets  # 五点描述分析器
from analyzers.strategy_analyzer import analyze_strategy  # 卖点策略分析器
from analyzers.keyword_analyzer import analyze_keywords  # 关键词SEO分析器
from scrapers.amazon import fetch_product, parse_excel  # 亚马逊爬虫和Excel解析

# ===== 创建 FastAPI 应用实例 =====
app = FastAPI(
    title="Amazon Listing Analyzer",
    description="亚马逊Listing拆解分析工具 - 标题/五点/卖点策略/关键词SEO",  # 中文项目描述
    version="1.0.0",
)

# ===== 配置 CORS 跨域中间件 =====
# 允许所有域名访问API（开发阶段使用，生产环境应限制域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,  # 允许携带凭证（cookies等）
    allow_methods=["*"],  # 允许所有HTTP方法（GET, POST等）
    allow_headers=["*"],  # 允许所有请求头
)


# ===== 健康检查接口 =====
@app.get("/api/health")
async def health():
    """服务健康检查，用于监控系统是否正常运行"""
    return {"status": "ok", "version": "1.0.0"}


# ===== 根路由 — 服务信息 =====
@app.get("/")
async def root():
    """根路径返回服务简介和可用接口列表"""
    return {
        "service": "Amazon Listing Analyzer API",
        "description": "亚马逊Listing拆解分析 — 标题/五点/卖点策略/关键词SEO",
        "version": "1.0.0",
        "endpoints": {
            "/api/health": "健康检查",
            "/api/analyze": "POST — 文本分析",
            "/api/demo": "GET — 获取演示示例数据",
            "/api/upload": "POST — Excel批量上传分析",
        },
    }


# ===== 演示示例数据接口 =====
# 提供预装的3组产品示例，方便面试展示时一键体验
@app.get("/api/demo")
async def demo():
    """返回3组预置的示例产品数据（蓝牙耳机/厨房用品/宠物用品）"""
    samples = [
        {
            "name": "高端降噪耳机",
            "title": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones, 30H Battery, Quick Charge, Crystal Clear Calls, Premium Comfort for Travel Office, Black",
            "bullets": [
                "INDUSTRY-LEADING NOISE CANCELLATION: 8 microphones and Auto NC Optimizer reduce noise across all frequencies for a truly immersive listening experience",
                "CRYSTAL CLEAR CALLS: Precise Voice Pickup Technology uses 4 beamforming microphones and AI-based noise reduction to perfectly isolate your voice in any environment",
                "30-HOUR BATTERY WITH QUICK CHARGING: Up to 30 hours of playback, with just 3 minutes of quick charging giving you 3 hours of listening time",
                "ULTIMATE COMFORT: Soft fit leather headband and lightweight 250g design engineered for all-day wear during travel, work, or relaxation",
                "MULTIPOINT CONNECTION: Seamlessly switch between two devices at once. Compatible with iOS, Android, Windows, and Mac via Bluetooth 5.2",
            ],
        },
        {
            "name": "不锈钢保温杯",
            "title": "Hydro Flask 32oz Wide Mouth Vacuum Insulated Stainless Steel Water Bottle, BPA-Free, Leakproof, TempShield Double-Wall, Keeps Cold 24hrs Hot 12hrs, Mountain White",
            "bullets": [
                "TEMP-SHIELD INSULATION: Double-wall vacuum insulation keeps beverages cold up to 24 hours and hot up to 12 hours, perfect for all-day hydration",
                "PREMIUM 18/8 STAINLESS STEEL: Professional-grade stainless steel construction ensures pure taste with no metallic flavor transfer and lasting durability",
                "BPA-FREE & TOXIC-FREE: All materials are 100% BPA-free, phthalate-free, and toxin-free for safe, healthy hydration every day",
                "LEAKPROOF DESIGN: Honeycomb insulated cap with flexible strap provides a secure, leakproof seal — toss it in your bag without worry",
                "LIFETIME WARRANTY: Backed by Hydro Flask's lifetime warranty. Dishwasher safe for easy cleaning. Fits most standard cup holders",
            ],
        },
        {
            "name": "宠物饮水机",
            "title": "PetSafe Drinkwell Platinum Pet Fountain, 168oz Large Capacity, Carbon Filter, Free-Falling Stream, Dishwasher Safe, for Cats and Dogs, White",
            "bullets": [
                "168 OZ LARGE CAPACITY: Extra-large water reservoir means less frequent refills, perfect for multi-pet households or extended trips away from home",
                "FREE-FALLING STREAM: Aerated falling water stream encourages pets to drink more, supporting kidney health and preventing dehydration",
                "REPLACEABLE CARBON FILTER: Active carbon filter removes bad tastes and odors, keeping water fresh and appealing to picky drinkers",
                "DISHWASHER SAFE: All plastic parts (excluding the pump) are top-rack dishwasher safe, making weekly cleaning quick and hassle-free",
                "WHISPER-QUIET PUMP: Submersible pump operates at near-silent levels, won't disturb your sleep or startle nervous pets",
            ],
        },
    ]

    demo_results = []
    for sample in samples:
        analysis = _run_analysis(sample["title"], sample["bullets"])
        result = vars(analysis)
        result["sample_name"] = sample["name"]
        demo_results.append(result)

    return {"total": len(demo_results), "results": demo_results}


# ===== 单条文本分析接口 =====
# 用户手动输入标题和五点描述，直接进行分析
@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalyzeRequest):
    """分析单条Listing：用户粘贴标题和五点描述文本"""
    title = request.title  # 从请求体中提取标题
    bullets = request.bullets  # 从请求体中提取五点描述列表

    if not title:
        raise HTTPException(status_code=400, detail="Title is required")  # 标题不能为空
    if not bullets:
        raise HTTPException(status_code=400, detail="At least one bullet point is required")  # 至少需要一条描述

    return _run_analysis(title, [b for b in bullets if b.strip()])  # 过滤空字符串后分析


# ===== URL/ASIN抓取分析接口 =====
# 根据亚马逊商品链接或ASIN码抓取页面并分析
@app.post("/api/fetch")
async def fetch_and_analyze(url: str = "", asin: str = "", marketplace: str = "com", proxy: str = ""):
    """抓取亚马逊产品页面并分析其Listing"""
    if not url and not asin:
        raise HTTPException(status_code=400, detail="Either url or asin is required")  # url或asin至少提供一个

    try:
        # 调用爬虫模块获取产品信息
        product = await fetch_product(url=url, asin=asin, marketplace=marketplace, proxy=proxy)
    except RuntimeError as e:
        # 将爬虫模块的 RuntimeError 原样传递给前端（如验证码拦截等）
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"抓取失败: {str(e)}")  # 其他异常统一处理

    if not product.title:
        raise HTTPException(
            status_code=422,
            detail="无法从该页面提取产品信息。亚马逊可能返回了验证码页面，建议改用「粘贴文本」模式手动输入标题和五点描述进行分析。"
        )

    # 返回抓取结果和分析结果（将分析字段展开合并到响应中）
    return {
        "fetched": True,
        "asin": product.asin,  # 产品ASIN码
        "price": product.price,  # 商品价格
        "rating": product.rating,  # 评分
        "reviews_count": product.reviews_count,  # 评论数量
        "images": product.images[:5],  # 最多返回5张图片
        **vars(_run_analysis(product.title, product.bullets)),  # 嵌入分析结果
    }


# ===== Excel批量上传分析接口 =====
# 上传包含多条Listing的Excel文件，批量分析
@app.post("/api/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    """上传Excel文件并批量分析所有Listing"""
    if not file.filename.endswith((".xlsx", ".xls")):  # 校验文件扩展名
        raise HTTPException(status_code=400, detail="Only .xlsx and .xls files are supported")

    file_bytes = await file.read()  # 读取文件二进制数据
    try:
        items = parse_excel(file_bytes)  # 解析Excel，提取标题和五点描述
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse Excel: {str(e)}")

    if not items:
        raise HTTPException(status_code=400, detail="No valid listings found in file")  # Excel中没有有效数据

    results = []
    for item in items:
        analysis = _run_analysis(item["title"], item["bullets"])  # 逐条分析
        results.append(vars(analysis))  # 转为字典格式

    return {
        "total": len(results),  # 处理总数
        "results": results,  # 所有分析结果
    }


# ===== 核心分析调度函数 =====
# 聚合四个分析器的结果，生成统一的 AnalysisResponse
def _run_analysis(title: str, bullets: list[str]) -> AnalysisResponse:
    """对单条Listing运行全部四个分析器（标题/五点/策略/关键词）"""
    filtered_bullets = [b for b in bullets if b.strip()]  # 过滤空字符串
    if len(filtered_bullets) > 5:
        filtered_bullets = filtered_bullets[:5]  # 最多保留5条描述（亚马逊标准五点描述）

    return AnalysisResponse(
        title=title,
        bullets=filtered_bullets,
        title_analysis=analyze_title(title),  # 第1步：标题结构化分析
        bullet_analysis=analyze_bullets(filtered_bullets),  # 第2步：五点描述类型分析
        strategy_analysis=analyze_strategy(title, filtered_bullets),  # 第3步：卖点策略分析
        keyword_analysis=analyze_keywords(title, filtered_bullets),  # 第4步：关键词SEO分析
    )


# ===== 开发环境直接启动 =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # 启动在 0.0.0.0:8000，允许外部访问
