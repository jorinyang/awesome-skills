# author-methodology-analysis 脚本安装指南

## 上游仓库

本技能 Python 脚本源自：
- https://github.com/freestylefly/author-methodology-analysis-skill (苍何, MIT)

## 安装步骤

```bash
# 克隆上游仓库
cd /tmp
git clone https://github.com/freestylefly/author-methodology-analysis-skill.git

# 将脚本和参考模板复制到技能目录
cp /tmp/author-methodology-analysis-skill/scripts/*.py \
   ~/.hermes-feishu/skills/methodology/author-methodology-analysis/scripts/
cp /tmp/author-methodology-analysis-skill/references/* \
   ~/.hermes-feishu/skills/methodology/author-methodology-analysis/references/

# 安装 Python 依赖（建议在 venv 中）
pip install python-docx pypdf
```

## 脚本清单

| 脚本 | 功能 |
|------|------|
| `analyze_corpus.py` | 解析语料（Markdown/TXT/DOCX/PDF）并生成确定性特征数据（JSON + CSV） |
| `generate_dashboard.py` | 从共享数据源生成离线 HTML 看板（十章节学习者视角） |
| `validate_outputs.py` | 校验数据、报告、HTML 和同步元数据的一致性 |

## 参考模板

| 模板 | 用途 |
|------|------|
| `report-template.md` | 生成主方法论报告时读取 |
| `data-analysis-framework.md` | 执行 21 维详细数据分析时读取 |
| `copywriting-framework-template.md` | 生成独立文案框架时读取 |
| `interactive-dashboard-template.md` | 生成 HTML 看板时读取 |
| `analysis-data.schema.json` | 共享分析数据结构定义 |

## 环境要求

- Python 3.8+
- `python-docx` (DOCX 解析)
- `pypdf` (PDF 文本提取)
- 飞书文档读取通过 `lark-doc` 技能（已内置）

## 样本量约束

| 样本数 | 约束 |
|:--:|------|
| < 3 | 禁止趋势/演化/稳定风格结论 |
| 3-4 | 仅描述性分析，明确标注低稳定性 |
| 5-10 | 核心维度 + 部分扩展维度 |
| 10-19 | 核心 + 扩展 + 交叉关联 |
| ≥ 20 | 全 21 维度 + 时间演化分析 |
| ≥ 50 | 抽样（如 token 成本过高），披露抽样方法 |
