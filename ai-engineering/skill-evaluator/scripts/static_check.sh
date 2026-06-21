#!/bin/bash
# L1 静态合规检查脚本
# 用法: bash static_check.sh <skill目录路径>
# 输出: JSON 格式的检查结果

set -e

SKILL_DIR="${1:-.}"
SCORE=0
TOTAL=6
ISSUES="[]"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "{"
echo '  "skill_dir": "'"$SKILL_DIR"'",'
echo '  "checks": ['

# --- 检查1: SKILL.md 存在 ---
check_skill_md() {
    if [ -f "$SKILL_DIR/SKILL.md" ]; then
        echo '    {"name": "SKILL.md 存在", "status": "pass", "detail": "文件存在"},'
        return 0
    else
        echo '    {"name": "SKILL.md 存在", "status": "fail", "detail": "SKILL.md 未找到"},'
        return 1
    fi
}

# --- 检查2: YAML frontmatter ---
check_frontmatter() {
    if head -1 "$SKILL_DIR/SKILL.md" 2>/dev/null | grep -q '^---$'; then
        HAS_NAME=$(sed -n '/^---$/,/^---$/p' "$SKILL_DIR/SKILL.md" | grep -c '^name:' || true)
        HAS_DESC=$(sed -n '/^---$/,/^---$/p' "$SKILL_DIR/SKILL.md" | grep -c '^description:' || true)
        if [ "$HAS_NAME" -ge 1 ] && [ "$HAS_DESC" -ge 1 ]; then
            echo '    {"name": "YAML frontmatter", "status": "pass", "detail": "name 和 description 均存在"},'
            return 0
        else
            echo '    {"name": "YAML frontmatter", "status": "fail", "detail": "缺少 name 或 description"},'
            return 1
        fi
    else
        echo '    {"name": "YAML frontmatter", "status": "fail", "detail": "缺少 YAML frontmatter"},'
        return 1
    fi
}

# --- 检查3: 脚本语法 ---
check_script_syntax() {
    local FAILS=0
    local DETAILS=""
    if [ -d "$SKILL_DIR/scripts" ]; then
        for f in "$SKILL_DIR/scripts"/*.sh; do
            [ -f "$f" ] || continue
            if bash -n "$f" 2>/dev/null; then
                DETAILS="$DETAILS$(basename "$f")=OK,"
            else
                DETAILS="$DETAILS$(basename "$f")=FAIL,"
                FAILS=$((FAILS + 1))
            fi
        done
        for f in "$SKILL_DIR/scripts"/*.py; do
            [ -f "$f" ] || continue
            if python3 -m py_compile "$f" 2>/dev/null; then
                DETAILS="$DETAILS$(basename "$f")=OK,"
            else
                DETAILS="$DETAILS$(basename "$f")=FAIL,"
                FAILS=$((FAILS + 1))
            fi
        done
    fi
    if [ "$FAILS" -eq 0 ]; then
        echo '    {"name": "脚本语法", "status": "pass", "detail": "'"${DETAILS:-无脚本文件}"'"},'
        return 0
    else
        echo '    {"name": "脚本语法", "status": "fail", "detail": "'"$FAILS 个脚本语法错误: $DETAILS"'"},'
        return 1
    fi
}

# --- 检查4: 引用完整性 ---
check_references() {
    local MISSING=0
    local DETAILS=""
    if [ -f "$SKILL_DIR/SKILL.md" ]; then
        # 提取 references/ 和 scripts/ 引用（排除 backtick 内和代码块内的引用）
        REFS=$(grep -oP '(?<![`\"])(?:references|scripts)/[a-zA-Z0-9_./-]+' "$SKILL_DIR/SKILL.md" 2>/dev/null | grep -v '^references/.*\.md$' || true)
        [ -z "$REFS" ] && REFS=$(grep -oP 'references/[^)\s"`]+|scripts/[^)\s"`]+' "$SKILL_DIR/SKILL.md" 2>/dev/null || true)
        for ref in $REFS; do
            if [ -f "$SKILL_DIR/$ref" ]; then
                DETAILS="$DETAILS$ref=OK,"
            else
                DETAILS="$DETAILS$ref=MISSING,"
                MISSING=$((MISSING + 1))
            fi
        done
    fi
    if [ "$MISSING" -eq 0 ]; then
        echo '    {"name": "引用完整性", "status": "pass", "detail": "'"${DETAILS:-无引用检查}"'"},'
        return 0
    else
        echo '    {"name": "引用完整性", "status": "fail", "detail": "'"$MISSING 个引用缺失: $DETAILS"'"},'
        return 1
    fi
}

# --- 检查5: 高危指令 ---
check_dangerous() {
    local FOUND=0
    local DETAILS=""
    PATTERNS=("rm -rf /" "rm -rf ~" "DROP TABLE" "DROP DATABASE" "> /dev/sda" "dd if=/dev/zero" "chmod 777 /" ":(){ :|:& };:")
    for pattern in "${PATTERNS[@]}"; do
        if grep -rq --include="*.sh" --include="*.py" \
            --exclude="static_check.sh" \
            "$pattern" "$SKILL_DIR" 2>/dev/null; then
            DETAILS="$DETAILS'$pattern' "
            FOUND=$((FOUND + 1))
        fi
    done
    if [ "$FOUND" -eq 0 ]; then
        echo '    {"name": "高危指令扫描", "status": "pass", "detail": "未发现高危指令"},'
        return 0
    else
        echo '    {"name": "高危指令扫描", "status": "fail", "detail": "发现高危指令: '"$DETAILS"'"},'
        return 1
    fi
}

# --- 检查6: 渐进式加载 ---
check_progressive() {
    local LINES=$(wc -l < "$SKILL_DIR/SKILL.md" 2>/dev/null || echo 9999)
    if [ "$LINES" -le 500 ]; then
        echo '    {"name": "渐进式加载", "status": "pass", "detail": "SKILL.md '"${LINES}行"' ≤ 500 行"}'
    else
        echo '    {"name": "渐进式加载", "status": "fail", "detail": "SKILL.md '"${LINES}行"' > 500 行，建议外置到 references/"}'
        return 1
    fi
}

# 执行所有检查
check_skill_md && SCORE=$((SCORE + 1))
check_frontmatter && SCORE=$((SCORE + 1))
check_script_syntax && SCORE=$((SCORE + 1))
check_references && SCORE=$((SCORE + 1))
check_dangerous && SCORE=$((SCORE + 1))
check_progressive && SCORE=$((SCORE + 1))

echo '  ],'
echo '  "summary": {'
echo '    "passed": '"$SCORE"','
echo '    "total": '"$TOTAL"','
echo '    "pass_rate": '"$(python3 -c "print(round($SCORE/$TOTAL*100,1))")"
echo '  }'
echo "}"
