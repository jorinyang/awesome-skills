#!/usr/bin/env python3
"""
WSL 本地任务轮询器 — 监听飞书 Bitable 任务队列，执行 Chromium Bing 搜索，创建飞书文档
部署: crontab -e 添加 */2 * * * * python3 /home/aorus/.hermes-feishu/scripts/task_poller.py

任务路由：
- 任务名以 "竞品_" 开头 → 文档存入竞品动态节点 (EAMYw1CPoipVWtkObbtcR2oDnNc)
- 其余 → 行业资讯节点 (V0Lhwl7KYiWYDDk1vCncv2GhnYf)
"""
import subprocess, json, os, sys, urllib.parse, time, re

BASE = "DhZcbnof3aj5d6siC1UcgyXtnvb"
TABLE = "tblVKG82oOl3UaNW"
SPACE_ID = "7643710721485753535"
PARENT_KNOWLEDGE = "V0Lhwl7KYiWYDDk1vCncv2GhnYf"
PARENT_MONITOR = "EAMYw1CPoipVWtkObbtcR2oDnNc"
GROUP_CHAT = "oc_40570cc921ca1f645f8667151c1e85e6"
CHROME = os.path.expanduser("~/.chromium/chrome-linux/chrome")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def lark_api(method, path, data=None):
    args = ["lark-cli", "api", method, path, "--as", "bot"]
    if data:
        args += ["--data", json.dumps(data)]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=20)
    out = proc.stderr if proc.stderr else proc.stdout
    try:
        return json.loads(out)
    except:
        return {"code": -1, "msg": out[:100]}

def get_pending_tasks():
    resp = lark_api("GET", f"/open-apis/bitable/v1/apps/{BASE}/tables/{TABLE}/records?page_size=50")
    records = resp.get("data", {}).get("items", [])
    pending = []
    for r in records:
        fields = r.get("fields", {})
        keyword = fields.get("搜索关键词", "")
        if not keyword:
            continue
        result = fields.get("结果摘要", "")
        if not result or result == "pending":
            task_name = fields.get("Text", "")
            task_type = "monitor" if task_name.startswith("竞品_") else "knowledge"
            pending.append({
                "record_id": r["record_id"],
                "task_name": task_name,
                "keyword": keyword,
                "task_type": task_type,
            })
    return pending

def execute_search(task):
    """Chromium --dump-dom Bing 搜索"""
    keyword = task["keyword"]
    for k in list(os.environ.keys()):
        if 'proxy' in k.lower():
            del os.environ[k]
    encoded = urllib.parse.quote(keyword)
    url = f"https://www.bing.com/search?q={encoded}&setlang=zh-Hans"
    proc = subprocess.run(
        [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
         "--no-first-run", "--no-proxy-server", "--dump-dom", url],
        capture_output=True, text=True, timeout=30
    )
    html = proc.stdout
    if not html or len(html) < 1000:
        return []
    results = []
    titles = re.findall(r'<h2[^>]*>.*?<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'<p[^>]*class="[^"]*b_lineclamp[^"]*"[^>]*>(.*?)</p>', html, re.DOTALL)
    seen_urls = set()
    for url, title_raw in titles:
        url = url.strip()
        if url in seen_urls or 'bing.com' in url or 'microsoft.com' in url:
            continue
        title = re.sub(r'<[^>]+>', '', title_raw).strip()
        if len(title) < 8:
            continue
        seen_urls.add(url)
        results.append({"title": title, "url": url, "snippet": ""})
        if len(results) >= 6:
            break
    for i, r in enumerate(results):
        if i < len(snippets):
            r["snippet"] = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:150]
    return results

def update_task(record_id, status, summary=""):
    fields = {"结果摘要": f"{status}: {summary}"[:500]}
    lark_api("PUT",
             f"/open-apis/bitable/v1/apps/{BASE}/tables/{TABLE}/records/{record_id}",
             {"fields": fields})

def create_feishu_doc(task_name, keyword, results, task_type="knowledge"):
    today = time.strftime("%Y-%m-%d")
    title = f"{today}_{task_name}"
    items = ""
    for r in results:
        items += f"<li><b>{r['title']}</b><br/>{r['snippet']}<br/><a href=\"{r['url']}\">原文</a></li>\n"
    xml = f"""<title>{title}</title>
<callout emoji="🤖" background-color="light-blue" border-color="blue">
  <p><b>自动采集 | {today} | 关键词：{keyword}</b></p>
  <p>来源：Chromium Bing 搜索 | 结果数：{len(results)}</p>
</callout>
<h1>搜索结果</h1>
<ul>{items}</ul>
<hr/>
<checkbox done="false">人工复核优先级</checkbox>
<checkbox done="false">标注过期规则</checkbox>"""
    xml_path = os.path.join(SCRIPT_DIR, "tmp", "task_doc.xml")
    os.makedirs(os.path.dirname(xml_path), exist_ok=True)
    with open(xml_path, "w") as f:
        f.write(xml)
    parent = PARENT_KNOWLEDGE if task_type == "knowledge" else PARENT_MONITOR
    proc = subprocess.run(["lark-cli", "docs", "+create", "--api-version", "v2",
                    "--doc-format", "xml", "--content", "@tmp/task_doc.xml",
                    "--parent-token", parent, "--as", "bot"],
                   capture_output=True, text=True, timeout=15, cwd=SCRIPT_DIR)
    out = proc.stderr or proc.stdout
    if proc.returncode != 0:
        raise RuntimeError(f"doc create failed: {out[:200]}")
    try:
        result = json.loads(out)
        if result.get("ok") and result.get("url"):
            return title, result["url"]
    except:
        pass
    return title, None

def send_group_message(text):
    msg_data = {
        "receive_id": GROUP_CHAT,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    lark_api("POST", "/open-apis/im/v1/messages?receive_id_type=chat_id", msg_data)

def main():
    tasks = get_pending_tasks()
    if not tasks:
        return
    for task in tasks:
        print(f"Processing: {task['task_name']} - {task['keyword']}")
        update_task(task["record_id"], "processing")
        try:
            results = execute_search(task)
            if results:
                task_type = task.get("task_type", "knowledge")
                doc_title, doc_url = create_feishu_doc(task["task_name"], task["keyword"], results, task_type)
                summary = f"采集 {len(results)} 条 → 文档《{doc_title}》"
                update_task(task["record_id"], "done", summary)
                items = "\n".join([f"• {r['title'][:50]}" for r in results[:3]])
                url_line = f"🔗 {doc_url}" if doc_url else "📄 文档已入库"
                msg = f"🤖 自动采集完成\n📋 {task['task_name']}\n🔍 {task['keyword']}\n📊 {len(results)}条\n{items}\n{url_line}"
                send_group_message(msg)
            else:
                update_task(task["record_id"], "done", "0条结果")
        except Exception as e:
            update_task(task["record_id"], "failed", str(e)[:200])
        time.sleep(2)

if __name__ == "__main__":
    main()
