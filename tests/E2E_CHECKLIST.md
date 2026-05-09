# 端到端测试 Checklist

部署到 OpenClaw 后，必须验证以下 6 个场景才算交付。每条对应 spec 第 12 节验收门槛。

⚠️ **测试用脱敏样本**，不要用真实家人报告做样本。

## 1. 与 pregnancy-care 并存不抢话

**前置：** 同一 OpenClaw 工作区装上 pregnancy-care 和 family-health 两个 skill。

**步骤：**
1. 给 bot 发一条："21周B超报告，发你看下" + 一张孕检 B超图
2. 检查：应由 pregnancy-care 接管
3. 给 bot 发："姈姈最近的体检报告" + 一份普通体检 PDF
4. 检查：应由 family-health 接管

**通过标准：** 两个 skill 各自接到对应消息，pregnancy/ 和 family-health/ 数据目录互相不污染。

## 2. 路由让位规则

**前置：** 工作区已有 pregnancy/profile.md，姓名设为"测试甲"。

**步骤：**
1. 不带任何文字描述，直接给 bot 发一份姓名为"测试甲"的化验单 PDF
2. 检查：family-health 应让位，pregnancy-care 接管
3. 再给 bot 发一份姓名为"测试乙"的化验单 PDF
4. 检查：family-health 应接管

**通过标准：** 第 1 步数据进 pregnancy/，第 3 步数据进 family-health/。

## 3. 别名识别

**前置：** family-health/members.md 里给"姈姈"加 3 个别名（虚构示例："X 某 1"、"X 阿姨"、"小 X"）。

**步骤：**
1. 给 bot 发一份姓名印为"X 某 1"的化验单
2. 给 bot 发一份姓名印为"X 阿姨"的化验单
3. 给 bot 发一份姓名印为"小 X"的化验单

**通过标准：** 3 份报告都正确归到 `members/姈姈/`。

## 4. 关注点自动更新

**前置：** members/爵爵/profile.md 关注点清单包含 TG 条目。

**步骤：**
1. 给 bot 发一份爵爵的化验单 PDF（含 TG 数值，如 4.2）

**通过标准：**
- members/爵爵/summary.md 的 "关注点" 专段下 "TG（甘油三酯）" 小节追加了新行
- bot 汇报中明确提到 "TG 关注点状态变化"
- concerns.md 同步刷新

## 5. 跨成员数据隔离

**前置：** members/姈姈/profile.md 关注点为 [钼靶, EB DNA]，members/爵爵/profile.md 关注点为 [TG, Q 波]。

**步骤：**
1. 给 bot 发一份姈姈的化验单 PDF（OCR 不慎在某行抽到属于其他成员的姓名片段）

**通过标准：**
- 报告归到 `members/姈姈/`
- bot 不会读取 `members/爵爵/profile.md`
- 不会把姈姈的指标错串到爵爵关注点上

**怎么验证不读？** 在 OpenClaw 平台或 bot 日志里查 file_read 调用清单。

## 6. PDF 综合报告生成

**前置：** members/姈姈/ 下有 ≥3 份历史 records/ + 完整 summary.md（含关注点专段）。

**步骤：**
1. 给 bot 发："生成姈姈的综合 PDF"

**通过标准：**
- bot 执行：`python3 {baseDir}/scripts/generate-pdf.py family-health/members/姈姈/ ...`
- 输出 PDF 包含：成员档案 + 所有趋势表 + 关注点专段 + 历史 records 摘要
- bot 把 PDF 文件发回给用户
