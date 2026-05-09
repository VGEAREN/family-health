# family-health

> 家人健康检查管理 OpenClaw skill。与 [pregnancy-care](https://github.com/VGEAREN/pregnancy-care) 并存。

## 功能

- 体检 / 化验单 / 影像 / 专科报告 自动归档（按成员）
- 多年指标趋势追踪
- 慢病关注点专项追踪（active / watching / resolved 状态机）
- 综合 PDF 报告生成（每个成员）
- 与 pregnancy-care 通过单向只读 `pregnancy/profile.md` 实现礼让协议

## 数据目录

```
family-health/
├── members.md              ← 成员索引 + 别名映射
├── concerns.md             ← 全家关注点总览
└── members/<显示名>/
    ├── profile.md
    ├── summary.md
    ├── records/            ← 结构化报告
    ├── reports/            ← 原始 PDF / 图片
    └── ocr_results/        ← OCR 原文
```

## 报告 4 大类

`checkup` 年度体检 / `lab` 化验单 / `imaging` 影像 / `specialist` 专科诊断

## 安装

OpenClaw skill 通过 OpenClaw 平台安装。Python 依赖：

```bash
pip3 install pymupdf reportlab
```

## 与 pregnancy-care 共存

- 与 pregnancy-care v1.1.0+ 互为礼让协议（**双向对称**）：
  - family-health 读 `pregnancy/profile.md`：孕妇本人的报告 + 孕期相关让位给 pregnancy-care
  - pregnancy-care 读 `family-health/members.md`：体检/影像/化验等让位给 family-health
- 用户可显式覆盖（"这是体检不是产检" / "归到孕期档案"）
- 安装时机不限（先后顺序无所谓）：未安装的一方对应索引文件不存在，礼让逻辑自动跳过

## 测试

```bash
python3 -m pytest tests/ -v
```

## 免责声明

所有分析仅供参考，不构成医学建议。请咨询专业医生。
