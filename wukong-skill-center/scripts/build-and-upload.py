"""
技能打包流水线：GitHub 仓库 → skills-index.json + .zip → OSS

用法: python build-and-upload.py <repo_path> <oss_bucket> <oss_endpoint> <oss_prefix>
需要环境变量: ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET
"""
import os, yaml, json, re, zipfile, sys, oss2


def parse_skill(skill_dir, skill_name):
    """解析单个 SKILL.md 提取元数据"""
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        return None
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None
    fm = yaml.safe_load(match.group(1))
    if not fm or 'name' not in fm:
        return None
    description = fm.get('description', '')
    if isinstance(description, list):
        description = ' '.join(str(d) for d in description)
    description = re.sub(r'\s+', ' ', str(description)).strip()
    if len(description) > 250:
        description = description[:247] + '...'
    tags = fm.get('tags', [])
    if isinstance(tags, str):
        tags = [tags]
    triggers = fm.get('triggers', [])
    if isinstance(triggers, str):
        triggers = [triggers]
    clean_triggers = [t.strip().strip('"').strip("'") for t in triggers[:15] if isinstance(t, str) and not t.startswith('#')]
    return {
        "id": fm['name'],
        "name": fm['name'],
        "display_name": fm['name'].replace('-', ' ').title(),
        "description": description,
        "version": str(fm.get('version', '1.0.0')),
        "tags": tags[:10],
        "triggers": clean_triggers,
        "category": fm.get('category', ''),
        "author": str(fm.get('author', '')),
    }


def build_pipeline(repo_path, out_dir):
    """全量构建：解析 + 索引 + 打包"""
    os.makedirs(out_dir, exist_ok=True)
    zips_dir = os.path.join(out_dir, "zips")
    os.makedirs(zips_dir, exist_ok=True)

    skills = []
    skill_dirs = sorted([d for d in os.listdir(repo_path)
                         if os.path.isdir(os.path.join(repo_path, d)) and not d.startswith('.')])

    for name in skill_dirs:
        skill_dir = os.path.join(repo_path, name)
        try:
            skill = parse_skill(skill_dir, name)
            if skill:
                skills.append(skill)
                # 打包 .zip
                version = skill['version']
                zip_path = os.path.join(zips_dir, f"{name}-v{version}.zip")
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for root, dirs, files in os.walk(skill_dir):
                        dirs[:] = [d for d in dirs if d != '.git']
                        for file in files:
                            file_path = os.path.join(root, file)
                            zf.write(file_path, os.path.relpath(file_path, skill_dir))
        except Exception as e:
            print(f"  ERROR {name}: {e}")

    # 写索引
    index_path = os.path.join(out_dir, "skills-index.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(skills, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(skills)} skills indexed, {len(os.listdir(zips_dir))} zips")
    return index_path, zips_dir


def upload_to_oss(index_path, zips_dir, bucket_name, endpoint, prefix):
    """上传到 OSS 并设公开读"""
    auth = oss2.Auth(os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"],
                     os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"])
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    bucket.get_bucket_info()
    print(f"✅ Connected to OSS: {bucket_name}")

    # 上传索引
    bucket.put_object_from_file(f"{prefix}/skills-index.json", index_path)
    bucket.put_object_acl(f"{prefix}/skills-index.json", oss2.OBJECT_ACL_PUBLIC_READ)
    print(f"✅ Index uploaded")

    # 上传 zips
    for zf in sorted(os.listdir(zips_dir)):
        bucket.put_object_from_file(f"{prefix}/zips/{zf}", os.path.join(zips_dir, zf))
        bucket.put_object_acl(f"{prefix}/zips/{zf}", oss2.OBJECT_ACL_PUBLIC_READ)
    print(f"✅ {len(os.listdir(zips_dir))} zips uploaded")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python build-and-upload.py <repo_path> <oss_bucket> <oss_endpoint> <oss_prefix>")
        sys.exit(1)
    repo, bucket, endpoint, prefix = sys.argv[1:5]
    index, zips = build_pipeline(repo, "/tmp/wukong-build")
    upload_to_oss(index, zips, bucket, endpoint, prefix)
    print(f"Done. Index: https://{bucket}.{endpoint}/{prefix}/skills-index.json")
