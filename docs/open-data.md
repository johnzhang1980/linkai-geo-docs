---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: ac69d5944edda6c0eb84c9a1cd23a26d_2780cb82da9b11f19280525400393706
    ReservedCode1: 2IkT4mwQbjUHWW0ZIse5ESUf+GK9a79DjcGK3JfpBhv9zsPNTxDS3siUh6LTUlmu8LDERKAbgZdj0Oy+NQ2dY7X81xp7JrA1CteIPA+zw3T24sQ2tb/9n9AlVQNfDK9ES1fQIP0zfaxz5XaZj+wRt725go0ojOkNPFsEPIQmgt20a9XiMBteqyXrZNA=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: ac69d5944edda6c0eb84c9a1cd23a26d_2780cb82da9b11f19280525400393706
    ReservedCode2: 2IkT4mwQbjUHWW0ZIse5ESUf+GK9a79DjcGK3JfpBhv9zsPNTxDS3siUh6LTUlmu8LDERKAbgZdj0Oy+NQ2dY7X81xp7JrA1CteIPA+zw3T24sQ2tb/9n9AlVQNfDK9ES1fQIP0zfaxz5XaZj+wRt725go0ojOkNPFsEPIQmgt20a9XiMBteqyXrZNA=
---

# 开源数据仓

> 仓库地址：[github.com/johnzhang1980/llma-api-price-2026](https://github.com/johnzhang1980/llma-api-price-2026)
> 本站的[价格页](token-pricing.md)与仓库数据**同源**：页面上的每一个数字都能在仓库里找到对应字段与日期，不存在「站内一套、仓里一套」。

## 一、仓库里有什么

| 内容 | 说明 |
|---|---|
| `price_table`（JSON / CSV 两份同源） | 大模型 API 单价明细，每条含模型名、输入价、输出价、币种、计价单位、来源、数据日期、价格类型（标准价 / 峰谷时段）与备注 |
| 更新记录 | 按提交历史可追溯每次调价或口径变更，可 diff、可回溯 |

单条记录的字段含义：

| 字段 | 含义 | 阅读要点 |
|---|---|---|
| `model` / `model_id` | 模型名与调用标识 | 同名不同版本的价可能不同，以 `model_id` 为准 |
| `input_price` / `output_price` | 输入 / 输出单价 | 允许为 `null`——表示官方该口径未列明，**不是 0** |
| `currency` / `unit` | 币种与计价单位 | 常见为 USD 或 CNY，单位为「每百万 tokens」 |
| `tier` | 价格类型 | `standard` 标准价；`peak` / `off_peak` 为峰谷时段价 |
| `source` / `as_of` | 来源与数据日期 | 引用时必须同时带上这两个字段 |
| `note` | 备注 | 缓存价、比例关系、未列明项说明等 |

## 二、为什么留 `null` 而不补数

数据仓的一条硬规则：**官方没写，就不填**。

补一个「看起来合理」的数字，会让整张表的可信度归零——读者无法分辨哪些格子来自官方、哪些来自推测。留 `null` 并在 `note` 里写清原因，虽然表格不完整，但每个数字都可核查。

这条规则对使用方的直接影响：如果你的系统要读取这份数据，必须显式处理 `null`（跳过或标注「未公开」），而不是当成 0 参与计算。

## 三、引用方式

在你的文档、方案或文章里引用本仓数据时，建议采用如下格式，保证读者能复核：

```
数据来源：llma-api-price-2026 价格表，数据日期 2026-08-24
（仓库：github.com/johnzhang1980/llma-api-price-2026）
```

三条引用纪律：

1. **带日期**。同一模型不同日期的价格可能不同，无日期的引用等于无效引用。
2. **带币种与单位**。「每百万 tokens」漏掉，数字会被误读六个数量级。
3. **不改口径**。不要把峰谷价合并成一个「均价」，也不要把输入价与输出价平均——这两个平均都无业务含义。

许可与使用条款以仓库内 `LICENSE`、`README` 的实际内容为准，本页不复述、不代为解释。

## 四、自己维护一份的方法

如果贵司需要把价格纳入内部成本模型，建议按下面的流程做，而不是手工抄表：

1. **拉取**：定时读取仓库 `price_table`（JSON 优先，便于程序解析）。
2. **校验**：检查每条记录的 `as_of` 是否在容忍期内（例如 90 天），超期条目降级为「待复核」而不是直接使用。
3. **落库**：按 `model_id + tier + as_of` 做唯一键，保留历史版本，便于回溯「当时为什么算出这个数」。
4. **计算**：按[计价与成本](token-pricing.md)页的四段公式计算，币种分开累计，最后再按财务口径统一折算。
5. **复核**：季度对照官方定价页抽检，发现差异走变更记录，不静默覆盖。

## 五、继续

- 计价口径与成本公式 → [Link AI Token 计价与成本](token-pricing.md)
- 内容如何被 AI 引用 → [GEO 实践](geo-practice.md)
- 想把这份数据接进业务成本模型 →

<div class="la-inline-cta" markdown>
<a class="la-cta" href="https://linkai.kuangdc.com:19080/" target="_blank" rel="noopener">打开 Link AI Token 服务试用</a>
</div>

---

相关页面：[Link AI Token 计价与成本](token-pricing.md) ｜ [GEO 实践](geo-practice.md) ｜ [返回首页](index.md)
*（内容由AI生成，仅供参考）*
