# GitHub API 技能仓库探索技术

> 当 git clone 超时、浏览器不可用时，用 GitHub REST API 探索仓库结构。

## 核心 API 端点

### 列出目录内容
```bash
# 根目录
curl -s https://api.github.com/repos/{owner}/{repo}/contents/

# 子目录
curl -s https://api.github.com/repos/{owner}/{repo}/contents/{path}
```

返回 JSON 数组，每个条目包含 `name`, `type` (file/dir/submodule), `download_url`。

### 搜索代码
```bash
curl -s "https://api.github.com/search/code?q={keyword}+repo:{owner}/{repo}"
```

### 搜索仓库
```bash
curl -s "https://api.github.com/search/repositories?q={name}+user:{owner}"
```

### 读取原始文件
```bash
curl -s https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}
```

## 解析脚本模板

```python
import json, sys
data = json.load(sys.stdin)
for item in data:
    t = item['type']
    name = item['name']
    if t == 'dir':
        print(f'📁 {name}')
    elif name.endswith('.md'):
        print(f'📄 {name}')
    else:
        print(f'   {name}')
```

## 子模块 (Submodule) 处理

当条目 `type` 为 `"submodule"` 且 `download_url` 为 `null` 时，该目录是 git submodule，指向独立仓库。处理步骤：

1. **搜索独立仓库：**
   ```bash
   curl -s "https://api.github.com/search/repositories?q={submodule-name}+user:{owner}"
   ```

2. **从独立仓库读取文件：**
   ```bash
   # 列出独立仓库内容
   curl -s https://api.github.com/repos/{owner}/{submodule-repo}/contents/

   # 读取 SKILL.md
   curl -s https://raw.githubusercontent.com/{owner}/{submodule-repo}/main/SKILL.md
   ```

3. **常见模式：** 主仓库如 `canghe-skills` 使用 submodule 引用独立技能仓库，如 `canghe-wechat-article-extractor` 是 `freestylefly/wechat-article-archive-skill` 的 submodule。GitHub API 不穿透 submodule，必须单独查询。

## 微信公众号文章内容提取

```bash
curl -sL -H "User-Agent: Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36" \
  "https://mp.weixin.qq.com/s/{article_id}" \
  | python3 -c "
import sys, re
html = sys.stdin.read()
m = re.search(r'id=\"js_content\"[^>]*>(.*?)</div>\s*<script', html, re.DOTALL)
if m:
    text = re.sub(r'<[^>]+>', '', m.group(1))
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&amp;', '&', text)
    text = text.strip()
    print(text[:8000])
"
```

## 中国 Git 托管平台（AtomGit / GitCode / Gitee）

这些平台的 REST API 经常不可用（返回空、JSON 解析失败、认证墙），**优先级方案是直接 `git clone --depth 1`：**

```bash
# AtomGit
git clone --depth 1 https://atomgit.com/{owner}/{repo}.git /tmp/{repo}

# Gitee
git clone --depth 1 https://gitee.com/{owner}/{repo}.git /tmp/{repo}

# GitCode
git clone --depth 1 https://gitcode.com/{owner}/{repo}.git /tmp/{repo}
```

克隆后直接探索本地文件系统（`find` / `read_file` / `cat`），不依赖 API。

**AtomGit 特定：** API 端点格式与 GitHub 相似（`atomgit.com/api/v4/projects/{encoded_path}`），但认证和响应格式不兼容。实践中直接用 `git clone` 绕过。

**浏览器备选：** 如果 git clone 也失败（某些企业内网限制），可尝试 `browser_navigate` 访问仓库 Web 页面，但需要 Chrome CDP 连接可用。

## 注意事项

- GitHub API 对未认证请求有速率限制（60次/小时）。大量请求时使用 `-H "Authorization: Bearer $GITHUB_TOKEN"`。
- `raw.githubusercontent.com` 不计算在 API 速率限制内。
- 子模块的 `submodule_git_url` 字段可能为 `null`，不要依赖它。
- CNS 平台的 API 不可靠是常态，git clone 是稳定兜底方案。
