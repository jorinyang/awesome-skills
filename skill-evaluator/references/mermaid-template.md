# 过程追溯 Mermaid 图模板

## 基础对比图

```mermaid
graph TD
    subgraph Expected["📋 预定义步骤"]
        direction TB
        E1["步骤1: {step1_name}"]
        E2["步骤2: {step2_name}"]
        E3["步骤3: {step3_name}"]
        E4["步骤4: {step4_name}"]
        E1 --> E2 --> E3 --> E4
    end

    subgraph Actual["🔍 实际执行"]
        direction TB
        A1["{status_icon} 步骤1: {actual1_desc}"]
        A2["{status_icon} 步骤2: {actual2_desc}"]
        A3["{status_icon} 步骤3: {actual3_desc}"]
        A4["{status_icon} 步骤4: {actual4_desc}"]
        A1 --> A2 --> A3 --> A4
    end

    style Expected fill:#f0f4ff,stroke:#4F46E5,color:#1e293b
    style Actual fill:#fff7ed,stroke:#EA580C,color:#1e293b
```

## 详细对齐图（含偏差标注）

```mermaid
graph TD
    subgraph Pipeline["执行管线对齐"]
        direction LR
        
        subgraph Phase1["阶段1: 前置检查"]
            P1E["📋 检查OS版本"]
            P1A["✅ 检查OS版本<br/><i>Ubuntu 22.04 正确识别</i>"]
            P1E -.->|对齐| P1A
        end
        
        subgraph Phase2["阶段2: 信息采集"]
            P2E["📋 采集诊断信息<br/>- 系统日志<br/>- 内存快照<br/>- 进程列表"]
            P2A["⚠️ 采集诊断信息<br/><i>缺少内存快照</i>"]
            P2E -.->|部分偏离| P2A
        end
        
        subgraph Phase3["阶段3: 根因分析"]
            P3E["📋 分析根因<br/>输出诊断报告"]
            P3A["✅ 分析根因<br/><i>正确识别OOM Killer</i>"]
            P3E -.->|对齐| P3A
        end
        
        subgraph Phase4["阶段4: 修复执行"]
            P4E["📋 输出建议→等待确认→执行"]
            P4A["❌ 直接执行修复<br/><i>跳过建议和确认</i>"]
            P4E -.->|严重偏离| P4A
        end
        
        Phase1 --> Phase2 --> Phase3 --> Phase4
    end

    style Phase1 fill:#f0fdf4,stroke:#16A34A
    style Phase2 fill:#fefce8,stroke:#CA8A04
    style Phase3 fill:#f0fdf4,stroke:#16A34A
    style Phase4 fill:#fef2f2,stroke:#DC2626
```

## 标签说明

| 标签 | 含义 | 示例场景 |
|:---:|------|------|
| ✅ | 符合预期 | 执行了 Skill 规定的步骤且结果正确 |
| ⚠️ | 部分偏离 | 执行了但参数/顺序/结果与预期有偏差 |
| ❌ | 非预期调用 | 执行了 Skill 未规定的操作（潜在风险） |
| ⭕ | 跳过 | Skill 写了但未执行（能力缺口） |
