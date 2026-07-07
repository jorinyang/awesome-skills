# 脚本安装

wechat-article-archive 的 Python 脚本来自上游仓库 `freestylefly/wechat-article-archive-skill`。

## 安装

```bash
# 1. 克隆上游仓库
cd /tmp && git clone --depth 1 https://github.com/freestylefly/wechat-article-archive-skill.git

# 2. 复制脚本到技能目录
cp /tmp/wechat-article-archive-skill/scripts/*.py \
   ~/.hermes-feishu/skills/content/wechat-article-archive/scripts/
```

## 依赖

```bash
pip install requests lxml
```

`requests` `lxml` 必须在当前 Python 环境中可用。建议在 venv 中安装。

## 验证

```bash
cd ~/.hermes-feishu/skills/content/wechat-article-archive
python3 -c "import requests, lxml; print('OK')"
python3 scripts/discover_account_articles.py --help
```

## Session 缓存

登录态保存到 `~/.cache/wechat-article-archive/session.json`（权限 0600，仅当前用户可读写）。同号下次采集自动复用，无需重新扫码。

会话失效时脚本自动删除缓存，重新运行并扫码即可。
