"""生成 tests/fixtures/sample-member/ 模拟一个成员的工作区。

⚠️ 全部使用虚构数据，不映射任何真实病例。
"""
from pathlib import Path

base = Path(__file__).parent / "fixtures" / "sample-member"
(base / "records").mkdir(parents=True, exist_ok=True)

(base / "profile.md").write_text("""# 测试成员档案

- 姓名：测试甲
- 年龄：60
- 性别：男
- 关注点：
  - TG（甘油三酯）  active  目标 <2.3
""", encoding="utf-8")

(base / "summary.md").write_text("""# 趋势

## 关注点

### TG（甘油三酯）
| 日期 | 数值 | 状态 |
|------|------|------|
| 2023-06-15 | 7.5 | 🔴 |
| 2024-01-15 | 4.2 | 🟡 |
| 2024-08-20 | 2.8 | 🟡 |

→ **建议**：继续低脂饮食 + 复查间隔 2 个月

## 血脂趋势
| 日期 | TC | TG | LDL | HDL |
|------|----|----|-----|-----|
| 2023-06-15 | 6.2 | 7.5 | 3.8 | 0.9 |
| 2024-08-20 | 5.1 | 2.8 | 3.2 | 1.1 |
""", encoding="utf-8")

(base / "records" / "2023-06-15-checkup-1.md").write_text("""# 体检 2023-06-15

## 基本信息
- 类型：checkup
- 日期：2023-06-15

## 检查指标
| 指标 | 数值 | 单位 | 参考 |
|------|------|------|------|
| TG | 7.5 | mmol/L | <1.7 |
| HGB | 145 | g/L | 130-175 |

## 异常分析
TG 高于正常上限，建议复查 + 饮食调整。
""", encoding="utf-8")

print(f"Sample member at {base}")
