#!/usr/bin/env python3
"""gh_ast_skeleton.py — GitHub 源码 AST 骨架提取器（repo-source-deepread 配套）

用途：深读大仓库源码而不撑爆上下文。对 50KB~200KB 的源码文件，不整读，
而是提取 AST 骨架：模块 docstring / 类+方法签名+docstring 首行 /
顶层函数签名 / 顶层常量（配置文件的金矿——产品打磨过的数值全在常量里）。

用法：
  # 直接指定文件（一次多个，批量！）
  python gh_ast_skeleton.py owner/repo memory/recall.py brain/agent_session.py
  # 按子树前缀+正则选文件（先查 tree 再骨架）
  python gh_ast_skeleton.py owner/repo --prefix main_logic/proactive_chat/ --regex "service|decisions"
  # 小文件整读（<8KB 自动整读，--full 强制整读）
  python gh_ast_skeleton.py owner/repo brain/agent_session.py --full
  # 指定分支（默认 main）
  python gh_ast_skeleton.py owner/repo file.py --branch master

设计要点（N.E.K.O 5014 文件精读沉淀）：
- 一次调用批量拉多个文件，不要一个文件一次工具调用
- 顶层常量是配置文件的黄金（半衰期/冷却/阈值等产品调参全在这）
- docstring 常含架构宣言（如 "Ordinary chat must never wait for topic screening"）
- 测试文件名即设计规格（test_proactive_unanswered_repeat → 有未应答重复策略）
- README 大小写坑：先 API 列目录确认是 README.md 还是 README.MD
- 单文件失败不中断批量
"""
import argparse, ast, json, re, ssl, sys, urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
HEADERS = {"User-Agent": "gh-ast-skeleton/1.0", "Accept": "application/vnd.github+json"}


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=30, context=CTX).read()


def fetch_raw(repo: str, branch: str, path: str) -> str:
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
    return _get(url).decode("utf-8", errors="replace")


def list_tree(repo: str, branch: str) -> list[str]:
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    data = json.loads(_get(url).decode())
    return [t["path"] for t in data.get("tree", []) if t.get("type") == "blob"]


def _sig(node) -> str:
    args = []
    a = node.args
    defaults = [None] * (len(a.args) - len(a.defaults)) + list(a.defaults)
    for arg, d in zip(a.args, defaults):
        s = arg.arg
        if d is not None:
            try:
                s += "=" + ast.unparse(d)[:20]
            except Exception:
                s += "=..."
        args.append(s)
    if a.vararg:
        args.append("*" + a.vararg.arg)
    if a.kwarg:
        args.append("**" + a.kwarg.arg)
    return f"{node.name}({', '.join(args)})"


def skeleton(src: str, path: str, max_doc: int = 350) -> str:
    tree = ast.parse(src)
    out = [f"\n{'=' * 70}\n### {path}  ({len(src) // 1024}KB)"]
    doc = ast.get_docstring(tree)
    if doc:
        out.append('"""' + doc[:max_doc] + ("..." if len(doc) > max_doc else "") + '"""')
    n_consts = 0
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            d = (ast.get_docstring(node) or "").split("\n")[0][:100]
            out.append(f"class {node.name}:  # {d}")
            for m in node.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    md = (ast.get_docstring(m) or "").split("\n")[0][:80]
                    pre = "async " if isinstance(m, ast.AsyncFunctionDef) else ""
                    out.append(f"    {pre}{_sig(m)}  # {md}")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            d = (ast.get_docstring(node) or "").split("\n")[0][:90]
            pre = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
            out.append(f"{pre}def {_sig(node)}  # {d}")
        elif isinstance(node, ast.Assign):
            n_consts += 1
    # 常量密集文件（配置/设置类）：打印顶层常量
    if n_consts >= 3:
        lines = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                try:
                    lines.append(f"{ast.unparse(node.targets[0])} = {ast.unparse(node.value)[:70]}")
                except Exception:
                    pass
        if lines:
            out.append("-- 顶层常量 --\n" + "\n".join(lines[:40]))
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description="GitHub 源码 AST 骨架提取器")
    ap.add_argument("repo", help="owner/repo")
    ap.add_argument("files", nargs="*", help="仓库内文件路径")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--prefix", default="", help="子树前缀过滤（配合 --regex）")
    ap.add_argument("--regex", default="", help="文件名正则过滤（配合 --prefix）")
    ap.add_argument("--full", action="store_true", help="强制整读而非骨架")
    ap.add_argument("--max-doc", type=int, default=350)
    args = ap.parse_args()

    files = list(args.files)
    if args.prefix or args.regex:
        tree = list_tree(args.repo, args.branch)
        pat = re.compile(args.regex) if args.regex else None
        picked = [p for p in tree if p.startswith(args.prefix) and p.endswith(".py")
                  and (pat is None or pat.search(p))]
        print(f"# tree 选中 {len(picked)} 个文件（prefix={args.prefix!r} regex={args.regex!r}）")
        files.extend(picked)
    if not files:
        ap.error("未指定文件：给 files 参数或用 --prefix/--regex 选择")

    for path in files:
        try:
            src = fetch_raw(args.repo, args.branch, path)
            if args.full or len(src) < 8192:
                print(f"\n{'=' * 70}\n### {path}  全文 ({len(src) // 1024}KB)")
                print(src[:12000])
            else:
                print(skeleton(src, path, args.max_doc))
        except Exception as e:  # noqa: BLE001 — 单文件失败不中断批量
            print(f"\n### {path} FAIL: {e}")


if __name__ == "__main__":
    main()
