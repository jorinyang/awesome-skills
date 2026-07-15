"""
钉钉悟空企业技能路由服务 — FC 函数模板
========================================
FC HTTP 触发器专用 WSGI handler。替换 SKILLS_INDEX_URL 和 SKILLS_ZIP_BASE 后部署。
纯标准库，无外部依赖。

部署配置：
  - 运行时: python3.10  （关键！python3 在某些 region 下 HTTP 触发器行为异常）
  - 内存: 256 MB
  - 超时: 30s
  - 处理器: index.handler
  - HTTP 触发器: 匿名访问, POST/GET

🔴 关键教训（经历 4 次重部署才修好）：
  1. 不能返回 dict → FC 会调用 str(dict) → 输出 "statusCodeheadersbody"
  2. 不能返回 json.dumps 字符串 → Content-Type 变成 octet-stream
  3. 正确做法: python3.10 runtime + WSGI handler + 显式 set Content-Type
"""
import json
import re
import urllib.request
import os
import logging

logger = logging.getLogger()

# ═══════════════════════════════════════════════════
# 配置（通过 FC 环境变量覆盖）
# ═══════════════════════════════════════════════════
SKILLS_INDEX_URL = os.environ.get(
    "SKILLS_INDEX_URL",
    "https://clawshell.online/wukong-skills/skills-index.json"
)
SKILLS_ZIP_BASE = os.environ.get(
    "SKILLS_ZIP_BASE",
    "https://clawshell.online/wukong-skills/zips"
)
MAX_RESULTS = int(os.environ.get("MAX_RESULTS", "10"))
MIN_SCORE = float(os.environ.get("MIN_SCORE", "0.2"))

_skills_cache = None


def load_skills():
    """从 OSS 加载技能索引（冷启动缓存）"""
    global _skills_cache
    if _skills_cache is not None:
        return _skills_cache
    logger.info(f"Loading skills from {SKILLS_INDEX_URL}")
    try:
        req = urllib.request.Request(SKILLS_INDEX_URL)
        with urllib.request.urlopen(req, timeout=10) as resp:
            _skills_cache = json.loads(resp.read().decode("utf-8"))
        logger.info(f"Loaded {len(_skills_cache)} skills")
    except Exception as e:
        logger.error(f"Failed to load skills: {e}")
        _skills_cache = []
    return _skills_cache


def tokenize(text):
    """中英文分词"""
    tokens = set()
    parts = re.split(r'[\s,，。！？、；：""''（）\(\)\[\]【】/\\|@#\$%^&\*+=<>`~\-_]+', text.lower())
    for part in parts:
        part = part.strip()
        if not part: continue
        tokens.add(part)
        sub = re.sub(r'([a-z])([A-Z])', r'\1 \2', part)
        for s in sub.split():
            s = s.strip()
            if s and len(s) > 1: tokens.add(s)
    return tokens


def keyword_score(skill, keywords):
    """多字段加权评分"""
    score = 0.0
    kw_set = set()
    for kw in keywords:
        kw_set.update(tokenize(kw))
        kw_set.add(kw.lower())
    if not kw_set: return 0.0

    name = skill.get("name", "").lower()
    display = skill.get("display_name", "").lower()
    desc = skill.get("description", "").lower()
    tags = " ".join(skill.get("tags", [])).lower()
    triggers = " ".join(skill.get("triggers", [])).lower()
    category = skill.get("category", "").lower()

    name_tokens = tokenize(name)
    display_tokens = tokenize(display)
    desc_tokens = tokenize(desc)
    tag_tokens = tokenize(tags)
    trigger_tokens = tokenize(triggers)
    cat_tokens = tokenize(category)

    for kw in kw_set:
        if kw == name: score += 30
        elif kw in name_tokens: score += 20
        if kw in display or kw in display_tokens: score += 15
        if kw in desc: score += 8
        elif kw in desc_tokens: score += 4
        if kw in triggers or kw in trigger_tokens: score += 6
        if kw in tags or kw in tag_tokens: score += 5
        if kw in category or kw in cat_tokens: score += 3
    return min(score, 100)


def match_skills(keywords, max_results=MAX_RESULTS):
    """主匹配函数"""
    skills = load_skills()
    if not skills: return []
    scored = []
    for skill in skills:
        s = keyword_score(skill, keywords)
        if s >= MIN_SCORE:
            scored.append((s, skill))
    scored.sort(key=lambda x: x[0], reverse=True)
    seen = set()
    results = []
    for s, skill in scored:
        sid = skill["id"]
        if sid in seen: continue
        seen.add(sid)
        version = skill.get("version", "1.0.0")
        results.append({
            "id": skill["id"],
            "name": skill["name"],
            "display_name": skill["display_name"],
            "description": skill.get("description", ""),
            "install_locator": {
                "type": "remote_url",
                "url": f"{SKILLS_ZIP_BASE}/{skill['id']}-v{version}.zip"
            }
        })
        if len(results) >= max_results: break
    return results


# ═══════════════════════════════════════════════════
# WSGI Handler — FC HTTP 触发器正确姿势
# ═══════════════════════════════════════════════════

def handler(environ, start_response):
    """
    FC HTTP 触发器 WSGI handler
    显式设置 Content-Type，避免 FC 将 dict 转成 key 拼接字符串
    """
    method = environ.get("REQUEST_METHOD", "GET")

    # 解析 request body
    body_str = ""
    try:
        length = int(environ.get("CONTENT_LENGTH", "0"))
        if length > 0:
            body_str = environ["wsgi.input"].read(length).decode("utf-8")
    except:
        pass

    try:
        body = json.loads(body_str) if body_str else {}
    except:
        body = {}

    keywords = body.get("keywords", [])
    if isinstance(keywords, str):
        keywords = [keywords]

    matched = match_skills(keywords)
    logger.info(f"Keywords={keywords} → {len(matched)} results")

    result = {"skills": matched}
    result_json = json.dumps(result, ensure_ascii=False)

    status = "200 OK"
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
    ]
    start_response(status, headers)
    return [result_json.encode("utf-8")]
