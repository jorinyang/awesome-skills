# OSS 部署：Python oss2 SDK 方式

适用场景：SPA HTML 文件部署到阿里云 OSS，替代 `ossutil` CLI（无需安装额外工具，直接用 Python SDK）。

## 凭据获取

从 `~/.ossutilconfig` 读取（或项目 `.env` 文件）：

```python
import os, configparser

config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.ossutilconfig"))
AK = config["Credentials"]["accessKeyID"]
SK = config["Credentials"]["accessKeySecret"]
ENDPOINT = config["Credentials"]["endpoint"]  # e.g. oss-cn-hongkong.aliyuncs.com
```

## 上传 + 公开访问

```python
import oss2

auth = oss2.Auth(AK, SK)
bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)

# 上传（带 Content-Type）
with open(local_path, 'rb') as f:
    bucket.put_object(oss_key, f, headers={
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'no-cache'
    })

# 设置公开读
bucket.put_object_acl(oss_key, oss2.OBJECT_ACL_PUBLIC_READ)

# 生成访问 URL
url = f"https://{BUCKET_NAME}.{ENDPOINT}/{oss_key}"
```

## 关键路径约定

- **OSS bucket 直接访问**：`https://{bucket}.{endpoint}/{oss_key}`
- **自定义域名**：`https://{domain}/{oss_key}`（注意：自定义域名可能需要 CDN 刷新才能看到更新，开发阶段建议直接用 OSS 直连 URL 验证）
- **SPA 文件前缀**：`web-spa/{project}/`（本约定适用于 `clawshell-vault` bucket）

## 依赖

```bash
pip install oss2
```

## 验证

```bash
curl -sI "https://{bucket}.{endpoint}/{oss_key}" | head -5
# 预期: HTTP/1.1 200 OK, Content-Type: text/html
```
