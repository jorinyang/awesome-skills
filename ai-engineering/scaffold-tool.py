#!/usr/bin/env python3
"""
scaffold-tool.py — 从 JSON 描述生成 defineTool TypeScript 骨架

用法:
  echo '[{"name":"set_font","desc":"Set font properties","mutates":true,"params":{"id":"Node ID","font":"Font family","weight":"100-900"}}]' | python3 scaffold-tool.py
  python3 scaffold-tool.py --interactive

输出: 符合 defineTool 三层架构的 TypeScript 代码
"""

import json
import sys
import os

# ── 参数类型推断 ──
def infer_param_type(name: str, desc: str) -> tuple[str, dict]:
    """从参数名和描述推断 ParamType 和约束"""
    name_lower = name.lower()
    desc_lower = desc.lower()

    # 数字
    if any(kw in name_lower for kw in ['size', 'width', 'height', 'radius', 'opacity',
                                          'weight', 'scale', 'count', 'index', 'gap',
                                          'padding', 'margin', 'spacing', 'rotation',
                                          'depth', 'level', 'step']):
        p = {'type': 'number', 'description': desc}
        if 'weight' in name_lower or '100' in desc:
            p['min'] = 100
            p['max'] = 900
        if 'opacity' in name_lower:
            p['min'] = 0
            p['max'] = 1
        return 'number', p

    # 布尔
    if any(kw in name_lower for kw in ['is_', 'has_', 'enable', 'disable', 'visible',
                                          'locked', 'required', 'italic', 'bold']):
        return 'boolean', {'type': 'boolean', 'description': desc}

    # 颜色
    if any(kw in name_lower for kw in ['color', 'fill', 'stroke', 'background', 'hex']):
        return 'color', {'type': 'color', 'description': desc + ' (hex like #ff0000)'}

    # 字符串数组
    if any(kw in name_lower for kw in ['ids', 'names', 'types', 'tags', 'list']):
        return 'string[]', {'type': 'string[]', 'description': desc}

    # 默认字符串
    return 'string', {'type': 'string', 'description': desc}


def scaffold_tool(tool_def: dict) -> str:
    """从 JSON 定义生成 defineTool TypeScript 代码"""
    name = tool_def['name']
    desc = tool_def.get('desc', '')
    mutates = tool_def.get('mutates', False)
    params_raw = tool_def.get('params', {})

    # 自动添加 id 参数（如果还没）
    if 'id' not in params_raw:
        params_raw = {'id': 'Target node ID', **params_raw}

    # 推断参数类型
    params_ts = []
    arg_hints = []
    for pname, pdesc in params_raw.items():
        ptype, pdef = infer_param_type(pname, pdesc)
        required = pname == 'id'
        optional_mark = '' if required else '?'

        params_ts.append(f"    {pname}: {{")
        for k, v in pdef.items():
            if isinstance(v, str):
                params_ts.append(f"      {k}: '{v}',")
            elif isinstance(v, bool):
                params_ts.append(f"      {k}: {str(v).lower()},")
            elif isinstance(v, (int, float)):
                params_ts.append(f"      {k}: {v},")
        params_ts.append(f"    }},")

        # 执行函数参数提示
        arg_hints.append(f"    // args.{pname}{optional_mark}: {ptype}")

    params_block = '\n'.join(params_ts)
    hints_block = '\n'.join(arg_hints)

    code = f'''import {{ defineTool, requireNode, nodeSummary }} from '#core/tools'

/**
 * {desc}
 *
 * @mutates {str(mutates).lower()}
 */
export const {name} = defineTool({{
  name: '{name}',
  description: '{desc}',
  mutates: {str(mutates).lower()},
  params: {{
{params_block}
  }},
  execute: (figma, args) => {{
    // TODO: 实现工具逻辑
{hints_block}
    const node = requireNode(figma, args.id)
    // ... your logic here ...
    return nodeSummary(node)
  }}
}})
'''
    return code


def scaffold_batch(tools: list) -> str:
    """批量生成工具，返回完整模块代码"""
    parts = []
    parts.append("""/**
 * Auto-generated tools — scaffolded by agent-tool-system
 *
 * TODO: 填充 execute 函数体
 * TODO: 决定每个工具属于 CORE 还是 EXTENDED
 */
""")

    for tool in tools:
        parts.append(scaffold_tool(tool))
        parts.append('')

    # 生成注册表骨架
    tool_names = [t['name'] for t in tools]
    registry = (
        "// ── 注册表 ──\n"
        "import type { ToolDef } from './schema'\n"
        "\n"
        "export const CORE_TOOLS: ToolDef[] = [\n"
        "  // TODO: 把高频工具移到这里（≤30个）\n"
        f"  {', '.join(tool_names)},\n"
        "]\n"
        "\n"
        "export const EXTENDED_TOOLS: ToolDef[] = [\n"
        "  // TODO: 把低频工具移到这里\n"
        "]\n"
    )
    parts.append(registry)

    return '\n'.join(parts)


def interactive_mode():
    """交互式模式"""
    print("🛠️  agent-tool-system · 工具脚手架")
    print("输入工具定义（Ctrl+D 结束，每行一个 JSON 对象）")
    print()
    print('示例: {"name":"set_font","desc":"Set font on a text node","mutates":true,"params":{"font":"Font family","weight":"100-900"}}')
    print()

    tools = []
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                tool = json.loads(line)
                tools.append(tool)
                print(f'  ✅ {tool["name"]}')
            except json.JSONDecodeError as e:
                print(f'  ❌ 解析失败: {e}')
    except KeyboardInterrupt:
        pass

    if not tools:
        print("未输入任何工具定义。")
        return

    print(f'\n生成 {len(tools)} 个工具...\n')
    print(scaffold_batch(tools))


def main():
    if '--interactive' in sys.argv or '-i' in sys.argv:
        interactive_mode()
        return

    # 从 stdin 读取 JSON
    try:
        data = sys.stdin.read()
        if not data.strip():
            print("用法: echo '[{...}]' | python3 scaffold-tool.py", file=sys.stderr)
            print("      python3 scaffold-tool.py --interactive", file=sys.stderr)
            sys.exit(1)
        tools = json.loads(data)
        if isinstance(tools, dict):
            tools = [tools]
        print(scaffold_batch(tools))
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
