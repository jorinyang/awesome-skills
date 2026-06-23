#!/usr/bin/env python3
"""
tools-to-mcp-schema.py — 从 defineTool 定义生成 MCP JSON Schema

解析 TypeScript 源文件中的 defineTool 调用，提取工具定义并转换为 MCP 兼容的 JSON Schema。

用法:
  # 从单个文件提取
  python3 tools-to-mcp-schema.py <tools-file.ts>

  # 从多个文件提取并合并
  python3 tools-to-mcp-schema.py tools/*.ts

  # 从 stdin 读取
  cat tools/*.ts | python3 tools-to-mcp-schema.py --stdin

  # 输出格式
  python3 tools-to-mcp-schema.py tools.ts --format mcp    # MCP tools/list 格式
  python3 tools-to-mcp-schema.py tools.ts --format json   # 纯 JSON Schema
  python3 tools-to-mcp-schema.py tools.ts --format markdown  # Markdown 文档

输出: MCP tools/list 响应格式的 JSON
"""

import json
import re
import sys


# ── 参数类型 → JSON Schema 映射 ──
PARAM_TYPE_MAP = {
    'string':   {'type': 'string'},
    'number':   {'type': 'number'},
    'boolean':  {'type': 'boolean'},
    'color':    {'type': 'string', 'description': 'Color value (hex like #ff0000)'},
    'string[]': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1},
}


def parse_defineTool(content: str) -> list[dict]:
    """从 TypeScript 源码中提取 defineTool 调用"""
    tools = []

    # 匹配 name/description/mutates
    name_pattern = re.compile(r"name:\s*['\"]([^'\"]+)['\"]")
    desc_pattern = re.compile(r"description:\s*['\"]([^'\"]+)['\"]")
    mutates_pattern = re.compile(r"mutates:\s*(true|false)")

    # 匹配 params 块（简化版——逐行解析）
    param_pattern = re.compile(
        r"(\w+):\s*\{\s*type:\s*['\"](string|number|boolean|color|string\[\])['\"](?:,\s*description:\s*['\"]([^'\"]*)['\"])?(?:,\s*required:\s*(true|false))?(?:,\s*enum:\s*\[([^\]]+)\])?(?:,\s*min:\s*(\d+))?(?:,\s*max:\s*(\d+))?(?:,\s*default:\s*([^,\}]+))?"
    )

    # 按块分割：寻找连续的 defineTool 区域
    blocks = re.split(r'export const \w+ = defineTool\(', content)

    for block in blocks[1:]:  # 跳过第一个分割前的部分
        # 提取到闭合的 })
        depth = 1
        end = 0
        for i, ch in enumerate(block):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 1:  # 回到初始深度——匹配到 defineTool 参数的闭合大括号
                    end = i
                    break

        tool_block = block[:end]

        name_match = name_pattern.search(tool_block)
        desc_match = desc_pattern.search(tool_block)
        mutates_match = mutates_pattern.search(tool_block)

        if not name_match:
            continue

        name = name_match.group(1)
        desc = desc_match.group(1) if desc_match else ""
        mutates = mutates_match.group(1) == 'true' if mutates_match else False

        # 提取参数
        params_block = re.search(r'params:\s*\{(.+?)\}', tool_block, re.DOTALL)
        params = {}
        required_params = []

        if params_block:
            param_text = params_block.group(1)
            for pm in param_pattern.finditer(param_text):
                pname = pm.group(1)
                ptype = pm.group(2)
                pdesc = pm.group(3) or f'{pname} parameter'
                preq = pm.group(4) == 'true'
                penum = pm.group(5)
                pmin = pm.group(6)
                pmax = pm.group(7)

                param_def = {'type': ptype, 'description': pdesc}
                if penum:
                    param_def['enum'] = [v.strip().strip("'\"") for v in penum.split(',')]
                if pmin:
                    param_def['minimum'] = int(pmin)
                if pmax:
                    param_def['maximum'] = int(pmax)
                if preq:
                    required_params.append(pname)

                params[pname] = param_def

        tools.append({
            'name': name,
            'description': desc,
            'mutates': mutates,
            'params': params,
            'required': required_params,
        })

    return tools


def to_mcp_tool(tool: dict) -> dict:
    """将工具定义转换为 MCP Tool 格式"""
    properties = {}
    required = []

    for pname, pdef in tool['params'].items():
        ptype = pdef.pop('type', 'string')
        schema_def = dict(PARAM_TYPE_MAP.get(ptype, {'type': 'string'}))
        schema_def['description'] = pdef.get('description', pname)

        # 附加约束
        if 'enum' in pdef:
            schema_def['enum'] = pdef['enum']
        if 'minimum' in pdef:
            schema_def['minimum'] = pdef['minimum']
        if 'maximum' in pdef:
            schema_def['maximum'] = pdef['maximum']

        properties[pname] = schema_def
        if pname in tool.get('required', []):
            required.append(pname)

    mcp_tool = {
        'name': tool['name'],
        'description': tool['description'],
        'inputSchema': {
            'type': 'object',
            'properties': properties,
            'required': required,
        }
    }

    return mcp_tool


def to_markdown(tools: list[dict]) -> str:
    """生成 Markdown 工具文档"""
    lines = []
    lines.append(f"# MCP 工具列表 ({len(tools)} 个)")
    lines.append("")

    for tool in tools:
        lines.append(f"## {tool['name']}")
        lines.append(f"")
        lines.append(f"**{tool['description']}**")
        if tool.get('mutates'):
            lines.append(f"")
            lines.append(f"> ⚠️ 会修改状态")
        lines.append(f"")
        lines.append(f"| 参数 | 类型 | 必填 | 说明 |")
        lines.append(f"|------|------|:---:|------|")

        for pname, pdef in tool['params'].items():
            ptype = pdef.get('type', 'string')
            preq = '✅' if pname in tool.get('required', []) else ''
            pdesc = pdef.get('description', '')
            extra = ''
            if 'enum' in pdef:
                extra = f' 可选: {", ".join(pdef["enum"])}'
            if 'minimum' in pdef and 'maximum' in pdef:
                extra += f' 范围: {pdef["minimum"]}-{pdef["maximum"]}'
            lines.append(f"| {pname} | {ptype} | {preq} | {pdesc}{extra} |")

        lines.append("")
        lines.append("---")
        lines.append("")

    return '\n'.join(lines)


def main():
    fmt = 'mcp'
    files = []

    args = sys.argv[1:]
    if '--stdin' in args:
        content = sys.stdin.read()
        tools = parse_defineTool(content)
    elif args:
        # 过滤出格式参数
        for i, a in enumerate(args):
            if a == '--format' and i + 1 < len(args):
                fmt = args[i + 1]
            elif a == '--stdin':
                continue
            elif not a.startswith('--'):
                files.append(a)

        all_tools = []
        for fpath in files:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                all_tools.extend(parse_defineTool(f.read()))
        tools = all_tools
    else:
        print("用法: python3 tools-to-mcp-schema.py <tools.ts> [--format mcp|json|markdown]", file=sys.stderr)
        print("      cat tools.ts | python3 tools-to-mcp-schema.py --stdin", file=sys.stderr)
        sys.exit(1)

    if not tools:
        print("⚠️  未找到 defineTool 定义", file=sys.stderr)
        sys.exit(0)

    if fmt == 'markdown':
        print(to_markdown(tools))
    elif fmt == 'json':
        mcp_tools = [to_mcp_tool(t) for t in tools]
        print(json.dumps(mcp_tools, indent=2, ensure_ascii=False))
    else:  # mcp format
        mcp_tools = [to_mcp_tool(t) for t in tools]
        result = {
            'tools': mcp_tools
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
