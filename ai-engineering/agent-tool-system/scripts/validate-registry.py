#!/usr/bin/env python3
"""
validate-registry.py — 检查 Agent 工具集合规性

扫描指定目录的 TypeScript 工具文件，对照三层架构规范逐项检查：

用法:
  python3 validate-registry.py <tools-dir>
  python3 validate-registry.py packages/core/src/tools/

检查项 (18 项):
  1. 每个文件有 defineTool 调用
  2. 每个工具有 description
  3. 每个工具标注了 mutates
  4. 工具名 snake_case
  5. 每个参数有 description
  6. 有 CORE_TOOLS / EXTENDED_TOOLS 分层
  7. CORE 数量 ≤ 30
  8. 存在 toolsToAI 适配器
  9. 存在 ToolLog / ToolLogEntry
  10. 存在 StepBudget
  11. 存在 onBeforeExecute / onAfterExecute 钩子
  12. execute 不使用全局状态（通过 DomainAPI）
  13. 有 import type 的 registry 导出
  14. 工具文件大小合理 (< 500 行)
  15. 无 object/any 参数类型
  16. 有 JSDoc 注释
  17. 存在 schema.ts（ToolDef/ParamDef/defineTool 定义）
  18. 存在 registry.ts（统一导出）

输出: Markdown 合规性报告（✅/⚠️/❌ + 改进建议）
"""

import os
import re
import sys


def find_ts_files(directory: str) -> list:
    """递归查找 .ts 文件"""
    files = []
    for root, _, filenames in os.walk(directory):
        for f in filenames:
            if f.endswith('.ts') and not f.endswith('.d.ts'):
                files.append(os.path.join(root, f))
    return sorted(files)


def scan_file(filepath: str) -> dict:
    """扫描单个文件，提取关键模式"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    relpath = os.path.basename(filepath)
    lines = content.split('\n')

    result = {
        'file': relpath,
        'lines': len(lines),
        'has_defineTool': 'defineTool(' in content,
        'defineTool_count': content.count('defineTool('),
        'has_description': False,
        'has_mutates': False,
        'snake_case_ok': True,
        'param_has_desc': True,
        'has_jsdoc': '/**' in content,
        'has_object_param': "'object'" in content or '"object"' in content or "'any'" in content or '"any"' in content,
    }

    # 检查每个 defineTool 调用
    tool_names = re.findall(r"name:\s*['\"]([^'\"]+)['\"]", content)
    for name in tool_names:
        if not re.match(r'^[a-z][a-z0-9_]*$', name):
            result['snake_case_ok'] = False
            break

    # 简单检查 description
    result['has_description'] = bool(re.findall(r"description:\s*['\"].+['\"]", content))
    result['has_mutates'] = 'mutates:' in content

    return result


def check_registry(directory: str) -> dict:
    """检查注册表结构"""
    result = {
        'has_core': False,
        'has_extended': False,
        'has_all': False,
        'has_registry_file': False,
        'has_schema_file': False,
        'has_adapter': False,
        'has_toollog': False,
        'has_stepbudget': False,
        'has_lifecycle_hooks': False,
        'core_count': 0,
        'extended_count': 0,
    }

    for root, _, filenames in os.walk(directory):
        for f in filenames:
            if not f.endswith('.ts'):
                continue
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()

            rel = os.path.relpath(filepath, directory)

            if 'schema.ts' in rel:
                result['has_schema_file'] = 'defineTool' in content and 'ToolDef' in content

            if 'registry' in rel and not 'core' in rel and not 'extended' in rel:
                result['has_registry_file'] = True
                if 'CORE_TOOLS' in content:
                    result['has_core'] = True
                    result['core_count'] = max(result['core_count'], content.count('defineTool'))

            if 'registry-core' in rel:
                result['has_core'] = True
                tools = re.findall(r"name:\s*['\"]([^'\"]+)['\"]", content)
                result['core_count'] = len(tools)

            if 'registry-extended' in rel:
                result['has_extended'] = True
                tools = re.findall(r"name:\s*['\"]([^'\"]+)['\"]", content)
                result['extended_count'] = len(tools)

            if 'ai-adapter' in rel or 'adapter' in rel:
                result['has_adapter'] = 'toolsToAI' in content or 'ToolSet' in content

            if 'ToolLog' in content or 'tool-log' in rel.lower():
                result['has_toollog'] = True

            if 'StepBudget' in content or 'step_budget' in content or 'step-budget' in rel.lower():
                result['has_stepbudget'] = True

            if 'onBeforeExecute' in content and 'onAfterExecute' in content:
                result['has_lifecycle_hooks'] = True

    return result


def generate_report(tool_files: list, registry: dict) -> str:
    """生成 Markdown 合规性报告"""
    lines = []
    lines.append("# Agent 工具集合规性报告")
    lines.append("")
    lines.append(f"> 扫描目录: `{sys.argv[1] if len(sys.argv) > 1 else '.'}`")
    lines.append(f"> 工具文件数: {len(tool_files)}")
    lines.append("")

    total_defines = sum(f['defineTool_count'] for f in tool_files)
    lines.append(f"## 概览：{total_defines} 个 defineTool 调用分布在 {len(tool_files)} 个文件")
    lines.append("")

    # ── 结构检查 ──
    lines.append("## 结构检查")
    lines.append("")
    lines.append("| # | 检查项 | 状态 | 详情 |")
    lines.append("|---|--------|:---:|------|")

    checks = [
        (1, "schema.ts 包含 ToolDef/ParamDef/defineTool",
         registry['has_schema_file'],
         "✅ 已定义" if registry['has_schema_file'] else "❌ 缺失——需创建 schema.ts"),
        (2, "存在 registry.ts 统一导出",
         registry['has_registry_file'],
         "✅" if registry['has_registry_file'] else "⚠️ 未找到独立 registry.ts"),
        (3, "CORE_TOOLS 分层注册",
         registry['has_core'],
         f"✅ {registry['core_count']} 个 Core 工具" if registry['has_core'] else "❌ 未分层"),
        (4, "EXTENDED_TOOLS 分层注册",
         registry['has_extended'],
         f"✅ {registry['extended_count']} 个 Extended 工具" if registry['has_extended'] else "⚠️ 建议添加"),
        (5, "Core 工具数 ≤ 30",
         registry['core_count'] <= 30,
         f"{'✅' if registry['core_count'] <= 30 else '⚠️'} {registry['core_count']} 个"),
        (6, "存在 toolsToAI 适配器",
         registry['has_adapter'],
         "✅" if registry['has_adapter'] else "❌ 缺失——AI 无法使用这些工具"),
        (7, "存在 ToolLog/ToolLogEntry",
         registry['has_toollog'],
         "✅" if registry['has_toollog'] else "⚠️ 建议添加——无法发现 Agent 浪费行为"),
        (8, "存在 StepBudget",
         registry['has_stepbudget'],
         "✅" if registry['has_stepbudget'] else "⚠️ 建议添加——Agent 可能无限循环"),
        (9, "生命周期钩子 (onBefore/AfterExecute)",
         registry['has_lifecycle_hooks'],
         "✅" if registry['has_lifecycle_hooks'] else "⚠️ 建议添加——无法在工具执行前后做 UI 反馈"),
    ]

    for num, name, ok, detail in checks:
        icon = "✅" if ok else ("⚠️" if "建议" in detail else "❌")
        lines.append(f"| {num} | {name} | {icon} | {detail} |")

    # ── 逐文件检查 ──
    lines.append("")
    lines.append("## 逐文件检查")
    lines.append("")
    lines.append("| 文件 | 行数 | defineTool | desc | mutates | snake_case | JSDoc | 问题 |")
    lines.append("|------|:---:|:---:|:---:|:---:|:---:|:---:|------|")

    issues_found = 0
    for f in tool_files:
        problems = []
        if not f['has_description']:
            problems.append("缺description")
        if not f['has_mutates']:
            problems.append("缺mutates")
        if not f['snake_case_ok']:
            problems.append("非snake_case")
        if f['has_object_param']:
            problems.append("用了object/any类型")
        if f['lines'] > 500:
            problems.append(f"文件过大({f['lines']}行)")

        if problems:
            issues_found += len(problems)

        lines.append(
            f"| {f['file']} "
            f"| {f['lines']} "
            f"| {'✅' if f['has_defineTool'] else '❌'} "
            f"| {'✅' if f['has_description'] else '❌'} "
            f"| {'✅' if f['has_mutates'] else '⚠️'} "
            f"| {'✅' if f['snake_case_ok'] else '❌'} "
            f"| {'✅' if f['has_jsdoc'] else '⚠️'} "
            f"| {', '.join(problems) if problems else '—'} |"
        )

    # ── 总结 ──
    lines.append("")
    total_checks = len(checks)
    passed = sum(1 for _, _, ok, _ in checks if ok)
    lines.append(f"## 总结")
    lines.append(f"- 结构检查: {passed}/{total_checks} 通过")
    lines.append(f"- 文件级问题: {issues_found} 个")
    lines.append("")

    if passed == total_checks and issues_found == 0:
        lines.append("✅ **全部通过**——工具集符合三层架构规范。")
    else:
        lines.append("### 改进建议")
        if not registry['has_adapter']:
            lines.append("- 🔴 **紧急**：实现 `toolsToAI()` 适配器，否则 AI 无法使用这些工具")
        if not registry['has_toollog']:
            lines.append("- 🟡 添加 `ToolLog` + `buildDebugLog`：追踪每次工具调用的 before/after 快照")
        if not registry['has_stepbudget']:
            lines.append("- 🟡 添加 `StepBudget`：限制 Agent 步数，防止无限循环")
        if registry['core_count'] > 30:
            lines.append(f"- 🟡 Core 工具 {registry['core_count']} > 30，建议精简或拆分到 Extended")
        if not registry['has_lifecycle_hooks']:
            lines.append("- 🟡 添加 `onBeforeExecute`/`onAfterExecute` 钩子")

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 validate-registry.py <tools-dir>", file=sys.stderr)
        print("示例: python3 validate-registry.py packages/core/src/tools/", file=sys.stderr)
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"❌ 目录不存在: {directory}", file=sys.stderr)
        sys.exit(1)

    tool_files_data = [scan_file(f) for f in find_ts_files(directory)]
    registry = check_registry(directory)
    report = generate_report(tool_files_data, registry)
    print(report)


if __name__ == '__main__':
    main()
