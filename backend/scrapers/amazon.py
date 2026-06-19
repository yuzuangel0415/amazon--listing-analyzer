# ===== 亚马逊产品页面抓取器 =====
"""
使用 Playwright 无头浏览器抓取亚马逊商品页面。
支持代理IP配置以绕过反爬虫检测。
"""
import re
import os
import asyncio
import random
from urllib.parse import urlparse  # URL解析工具
from dataclasses import dataclass, field  # 数据类装饰器

# ===== 产品信息数据模型 =====
@dataclass
class ProductInfo:
    title: str  # 商品标题
    bullets: list[str] = field(default_factory=list)  # 五点描述列表
    images: list[str] = field(default_factory=list)  # 商品图片URL列表
    price: str = ""  # 商品价格文本
    rating: str = ""  # 评分文本
    reviews_count: str = ""  # 评论数量文本
    asin: str = ""  # 亚马逊标准识别码
    marketplace: str = ""  # 市场站点（如 com, co.jp）


# ===== HTML内容解析 =====
# 使用 BeautifulSoup 从亚马逊页面HTML中提取关键信息
def _extract_from_html(html: str) -> dict:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")  # 创建BeautifulSoup解析对象
    result = {"title": "", "bullets": [], "price": "", "rating": "", "images": []}

    # 提取标题：尝试多个CSS选择器（适配不同页面结构）
    for sel in ["span#productTitle", "span#title", "h1#title"]:
        elem = soup.select_one(sel)
        if elem:
            result["title"] = elem.get_text(strip=True)
            break
    if not result["title"]:
        # 如果上面的选择器都没匹配到，尝试从meta标签获取
        meta = soup.find("meta", {"property": "og:title"})
        if meta and meta.get("content"):
            result["title"] = meta["content"].strip()

    # 提取五点描述（feature bullets）
    area = soup.find("div", {"id": "feature-bullets"}) or soup.find("div", {"id": "featurebullets_feature_div"})
    if area:
        for li in area.find_all("li"):
            text = li.get_text(" ", strip=True)
            if text and len(text) > 5 and not text.startswith("{"):  # 过滤太短的和以{开头的非纯文本
                result["bullets"].append(text)

    # 提取价格
    price_elem = soup.select_one("span.a-price span.a-offscreen") or \
                 soup.select_one(".a-price .a-offscreen")
    if price_elem:
        result["price"] = price_elem.get_text(strip=True)

    # 提取评分
    rating_elem = soup.find("span", {"data-hook": "rating-out-of-text"}) or \
                  soup.find("span", class_="a-icon-alt")
    if rating_elem:
        result["rating"] = rating_elem.get_text(strip=True)

    # 提取高清图片URL（从页面内嵌的JSON脚本数据中解析）
    for script in soup.find_all("script", string=re.compile(r'"hiRes":')):
        if script.string:
            result["images"].extend(re.findall(r'"hiRes":"(https://[^"]+)"', script.string))

    return result


# ===== 代理配置获取 =====
def _get_proxy() -> str:
    """从环境变量读取代理设置，优先使用 AMAZON_PROXY，其次 HTTP_PROXY"""
    return os.environ.get("AMAZON_PROXY", os.environ.get("HTTP_PROXY", ""))


# ===== Playwright 无头浏览器抓取 =====
# 使用 Chromium 无头模式访问亚马逊页面，绕过反爬虫检测
async def _scrape_with_playwright(url: str, proxy: str = "") -> dict:
    from playwright.async_api import async_playwright

    if not proxy:
        proxy = _get_proxy()  # 如果未传入代理，从环境变量获取

    async with async_playwright() as p:
        # 浏览器启动参数：隐藏自动化特征、禁用沙箱（适配Docker环境）
        browser_args = [
            "--disable-blink-features=AutomationControlled",  # 禁用 Chrome 自动化检测标记
            "--no-sandbox",  # 禁用沙箱（Docker/CI环境中需要）
            "--disable-dev-shm-usage",  # 使用 /tmp 而非 /dev/shm（避免内存不足）
        ]
        if proxy:
            browser_args.append(f"--proxy-server={proxy}")  # 配置代理服务器

        browser = await p.chromium.launch(headless=True, args=browser_args)  # 启动无头Chrome

        # 创建浏览器上下文，模拟真实用户环境
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},  # 全高清分辨率
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"  # 使用常见Chrome UA
            ),
            locale="en-US",  # 美国英语地区
            timezone_id="America/New_York",  # 美东时区
        )

        # 注入反检测脚本：隐藏 webdriver 等自动化标记
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        page = await context.new_page()

        # 如果安装了 playwright-stealth，额外应用隐身补丁
        try:
            from playwright_stealth import Stealth
            stealth = Stealth()
            await stealth.apply_stealth_async(page)
        except ImportError:
            pass  # 未安装则跳过，不影响主流程

        try:
            await asyncio.sleep(random.uniform(0.5, 1.5))  # 随机延迟，模拟人类阅读速度
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)  # 访问目标URL

            # 检查是否被亚马逊拦截（验证码页面 / 机器人检测页面）
            content = await page.content()
            if "opfcaptcha.amazon.com" in content or "Robot Check" in content:
                if proxy:
                    raise RuntimeError(f"使用代理 {proxy} 仍被 Amazon 拦截，请更换代理IP")
                raise RuntimeError(
                    "Amazon 拦截了当前IP的请求。\n"
                    "解决方案：设置代理环境变量 AMAZON_PROXY=http://user:pass@ip:port\n"
                    "或在「粘贴文本」模式下手动输入标题和五点描述进行分析。"
                )

            # 模拟滚动浏览行为（分3次向下滚动，触发懒加载内容）
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 300)")  # 每次滚动300像素
                await asyncio.sleep(random.uniform(0.3, 0.7))  # 随机等待

            # 等待标题元素加载
            try:
                await page.wait_for_selector("#productTitle, #title, [property='og:title']", timeout=10000)
            except Exception:
                pass  # 超时也不中断，可能页面结构特殊但内容已加载

            await asyncio.sleep(random.uniform(0.3, 0.8))  # 最后等待确保内容渲染完毕
            html = await page.content()  # 获取完整HTML
            return _extract_from_html(html)  # 解析提取结构化数据
        finally:
            await browser.close()  # 无论如何确保关闭浏览器，释放资源


# ===== 抓取产品信息主入口 =====
# 支持通过URL或ASIN码抓取亚马逊商品页面
async def fetch_product(url: str = "", asin: str = "", marketplace: str = "com", proxy: str = "") -> ProductInfo:
    if asin and not url:
        # 如果只提供了ASIN，自动拼接为完整URL
        url = f"https://www.amazon.{marketplace}/dp/{asin}"
    if not url:
        raise ValueError("Either url or asin must be provided")  # 至少需要一个输入

    # 从URL中提取ASIN码（格式：/dp/B0XXXXXXXXX）
    asin_match = re.search(r"/dp/([A-Z0-9]{10})", url)
    if asin_match:
        asin = asin_match.group(1)  # 提取10位ASIN码

    # 从URL中解析市场站点（从域名 amazon.xxx 提取后缀）
    parsed = urlparse(url)
    mkt = marketplace
    if "amazon." in parsed.netloc:
        mkt = parsed.netloc.split("amazon.")[-1].split("/")[0]  # 提取 .com / .co.jp 等

    # 尝试使用 Playwright 进行抓取
    try:
        data = await _scrape_with_playwright(url, proxy=proxy)
    except ImportError:
        # Playwright 未安装的提示信息
        raise RuntimeError(
            "Playwright 未安装。请运行:\n"
            "  pip install playwright playwright-stealth\n"
            "  playwright install chromium\n"
            "或使用「粘贴文本」模式。"
        )
    except RuntimeError:
        raise  # RuntimeError 直接向上抛出（如验证码拦截等）
    except Exception as e:
        raise RuntimeError(f"抓取异常: {e}")  # 其他未知异常统一包装

    if not data.get("title"):
        # 解析失败（可能是页面结构更新）
        raise RuntimeError("无法提取产品标题，Amazon 可能更新了页面结构。请使用「粘贴文本」模式。")

    return ProductInfo(
        title=data["title"],
        bullets=data.get("bullets", []),
        images=data.get("images", []),
        price=data.get("price", ""),
        rating=data.get("rating", ""),
        reviews_count="",
        asin=asin or "",  # 如果从URL解析到了ASIN则填入
        marketplace=mkt,  # 从URL中解析的市场站点
    )


# ===== Excel文件解析 =====
# 从Excel批量导入中提取标题和五点描述
def parse_excel(file_bytes: bytes) -> list[dict]:
    import pandas as pd
    from io import BytesIO

    df = pd.read_excel(BytesIO(file_bytes))  # 使用pandas读取Excel文件
    items = []

    for _, row in df.iterrows():
        # 读取标题列
        title = str(row.get("title", "")).strip() if pd.notna(row.get("title")) else ""
        bullets = []

        # 尝试按独立列读取五点描述（bullet1 到 bullet5）
        for col in ["bullet1", "bullet2", "bullet3", "bullet4", "bullet5"]:
            if col in df.columns:
                val = str(row[col]).strip() if pd.notna(row[col]) else ""
                if val and val != "nan":  # 过滤pandas空值标记
                    bullets.append(val)

        # 如果没有独立列，尝试从合并的 "bullets" 列读取
        if not bullets and "bullets" in df.columns:
            raw = str(row["bullets"]).strip() if pd.notna(row["bullets"]) else ""
            if raw and raw != "nan":
                # 按换行符、分号或数字编号拆分
                parts = re.split(r"[\n\r]+|\s*;\s*|\s*\d+[\.\)]\s*", raw)
                bullets = [p.strip() for p in parts if p.strip()]  # 清理空白

        if title and title != "nan":
            items.append({"title": title, "bullets": bullets})  # 仅添加有效标题的条目

    return items
