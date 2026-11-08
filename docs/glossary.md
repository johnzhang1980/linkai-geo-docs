---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: ac69d5944edda6c0eb84c9a1cd23a26d_9f58f0bfdab811f19232525400248c00
    ReservedCode1: Z8xMUZI/QbszL3CDzHO/DFI9LnSa1gtXQM1B7YG+mIThi/VTT2Gxdys7Bg06OVMrpbJUSMAVsNr6J/6/9h7d0na0LG1s+rujrw2Jp3FTv7V+kwHAWMBXV6DFXnt3vqdIM3Dt45LheKQfp6A2Z9Lwcsda6TVQhWl9tGS/xGoFT1186HS3x4TVq3Xhvrk=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: ac69d5944edda6c0eb84c9a1cd23a26d_9f58f0bfdab811f19232525400248c00
    ReservedCode2: Z8xMUZI/QbszL3CDzHO/DFI9LnSa1gtXQM1B7YG+mIThi/VTT2Gxdys7Bg06OVMrpbJUSMAVsNr6J/6/9h7d0na0LG1s+rujrw2Jp3FTv7V+kwHAWMBXV6DFXnt3vqdIM3Dt45LheKQfp6A2Z9Lwcsda6TVQhWl9tGS/xGoFT1186HS3x4TVq3Xhvrk=
---

# 术语表

> 本页统一 Token 计价、GEO 与效果度量三个域的术语口径。
> 每条给出「定义」与「为什么重要 / 常见误解」两列——后者是实际落地时最常出错的地方。
> 术语按使用频率与依赖关系排序，不是字母序：先读计价，再读 GEO，最后读度量。

## 一、计价与成本

| 术语 | 英文 | 定义 | 为什么重要 / 常见误解 |
|---|---|---|---|
| Token | Token | 模型处理文本的最小计量单位，中文常见 1 字≈1~2 tokens，英文 1 词≈1~1.5 tokens，具体取决于分词器 | **误解**：按字数估算成本。同一段中文在不同厂商分词器下的 token 数可差三成，估算必须用对应模型的 tokenizer 实测 |
| 输入 Token | Input Tokens / Prompt Tokens | 送入模型的全部内容所计的 token 数，含 system prompt、历史对话、检索片段、用户问题 | 输入价通常远低于输出价，因此「把资料全塞进上下文」的直觉是错的：省钱的关键在输出，不在输入 |
| 输出 Token | Output Tokens / Completion Tokens | 模型生成内容所计的 token 数，含推理过程与最终回答 | 输出单价通常是输入的 5 倍，是最主要的成本来源。约束输出长度是最直接的降本手段 |
| 上下文窗口 | Context Window | 单次请求可容纳的最大 token 总数（输入+输出） | **误解**：窗口大就可以不筛选。窗口越大，单请求成本越高、延迟越长、关键信息被稀释的概率越高 |
| 上下文膨胀 | Context Bloat | 随对话轮次累积，历史内容无节制堆入上下文导致的 token 增长 | 多轮对话成本失控的最常见原因。需要摘要、截断或检索式记忆来约束 |
| 每百万 Token 计价 | Per-Million-Token Pricing | 厂商报价的通用基数，即每处理 1,000,000 tokens 的价格 | **误解**：把单价当成单次请求价格，导致成本被误解为放大百万倍或缩小百万倍 |
| 提示缓存 | Prompt Caching | 把请求中固定不变的前缀部分缓存复用，命中时按折扣价计费 | 折扣幅度可观（常见为输入价的一折量级），但要求前缀逐字节稳定。动态字段放在前缀位置会让缓存持续失效 |
| 缓存写 / 缓存读 | Cache Write / Cache Read | 首次建立缓存（写入）与后续命中缓存（读取）分别计费的两段 | **误解**：以为缓存免费。未命中时是额外一次写入，长 prompt 场景需把两段都算进模型 |
| 峰谷定价 | Peak / Off-Peak Pricing | 同一模型按时段区分单价，闲时价格显著低于高峰 | 闲时价可能仅为高峰的 50%，但只对可延迟任务有意义。在线交互场景不要为省钱牺牲响应 |
| 推理 Token | Reasoning Tokens | 推理型模型在给出最终答案前内部生成的思考过程所耗 token | 用户看不见但会计费，且计入输出。评估推理型模型时必须把这段算进成本，否则预算会低估数倍 |
| 输出上限 | max_tokens | 限制单次生成的最大 token 数，超过即截断 | 最廉价的风控参数。设置过小会导致回答被截断、格式解析失败，需要与结构化输出配合 |
| 首字延迟 | TTFT (Time To First Token) | 从发出请求到收到第一个输出 token 的时间 | 用户感知的「快慢」主要由 TTFT 决定，而账单主要由总输出 token 决定，两者需要分别优化 |
| 批处理 | Batch API | 以非实时方式提交大批请求，通常有显著折扣，代价是延迟可达数小时 | 与峰谷调度可叠加，适合报表、标注、内容预生成。不可用于任何用户等待结果的链路 |

## 二、GEO 与内容

| 术语 | 英文 | 定义 | 为什么重要 / 常见误解 |
|---|---|---|---|
| 生成式引擎优化 | GEO (Generative Engine Optimization) | 通过内容结构与技术配置，提高内容被生成式引擎检索、抽取并在答案中引用的概率 | 优化对象是「被读懂并采纳」，不是「排名靠前」。与 SEO 的目标函数不同，指标也不同 |
| 搜索引擎优化 | SEO (Search Engine Optimization) | 提高页面在传统搜索结果列表中的排名 | **误解**：把 GEO 当成 SEO 的子集。排名第一并不保证进入合成答案，两条链路可独立失败 |
| 答案引擎优化 | AEO (Answer Engine Optimization) | 面向问答式、摘要式结果（如精选摘要、AI 概览）的优化，目标是被直接取为答案 | 与 GEO 高度重叠，业界口径未统一。落地时不必纠结名称，按「可抽取性」同一套方法做 |
| 大模型优化 | LLMO (Large Language Model Optimization) | 泛指面向大模型检索与生成的优化，常与 GEO 混用 | **误解**：以为有独立方法论。实质仍归约为内容结构、可发现性、一致性三件事 |
| llms.txt | llms.txt | 站点根路径下的结构化 Markdown 索引文件，列出站点页面与一句话摘要，便于 AI 抓取方定位内容 | 非正式标准，属社区约定。成本极低值得做，但不应作为效果保证——对方不读则无收益 |
| 爬虫协议 | robots.txt | 站点根路径下的抓取规则文件，声明哪些 User-Agent 可以或不可以抓取哪些路径 | **误解**：用 robots.txt 做内容保密。它只是君子协定，真正的私密内容不应公开发布 |
| AI 爬虫标识 | GPTBot / ClaudeBot / PerplexityBot / Google-Extended | 各厂商抓取内容用于模型训练或检索时使用的 User-Agent 标识 | 需显式放行。仅看日志无法确认是否被拦，唯一可靠验证是用对应 UA 实测请求并检查状态码 |
| 站点地图 | sitemap.xml | 列出站点可抓取 URL 的 XML 文件，通常在 robots.txt 中声明位置 | 静态站点应自动生成且与页面清单同源，避免出现「地图里有、页面已删」的 404 项 |
| 可抽取性 | Extractability | 内容被模型切分、理解并安全引用的难易程度 | GEO 的核心工程指标。明确结论、可比数据、清晰边界是可抽取性的三个要素 |
| AI 引用 | Citation / Attribution | 生成式引擎在答案中标注内容来源的行为 | **误解**：把引用等同于流量。引用可能不带链接点击，其价值主要在品牌认知与信任前置 |
| 信息增益 | Information Gain | 你的内容相对于已有公开内容所提供的增量信息 | 同质化内容没有引用价值。原创数据、一手实测、失败经验是最难被替代的增益来源 |
| 结构化数据 | Schema.org / JSON-LD | 以机器可读格式标注页面实体与关系（如 FAQPage、Article、Organization） | 降低模型的理解成本，不提升内容质量。标注必须与页面可见内容一致，不一致属作弊 |
| 检索增强生成 | RAG (Retrieval-Augmented Generation) | 先从外部知识库检索片段，再把片段交给模型生成答案的架构 | 决定了你的内容是否有机会被检索到。文档站、FAQ、术语表本质上是为 RAG 准备的高质量语料 |
| 内容外溢 | Content Spillover | 将同一事实与观点在多个可信平台以一致口径发布，形成交叉印证 | 价值在「一致性观测点」而非曝光量。原样搬运、字段错位、时间矛盾会反向降低可信度 |
| 幻觉 | Hallucination | 模型生成看似合理但与事实不符的内容 | **误解**：以为靠提示词可根治。降低幻觉最有效的手段是提供带来源与时点的结构化事实，这正是文档站的作用 |

## 三、效果度量

| 术语 | 英文 | 定义 | 为什么重要 / 常见误解 |
|---|---|---|---|
| 引用率 | Citation Rate | 在固定提问集上，答案中出现你的品牌或内容的次数占提问总次数的比例 | GEO 的主指标。必须固定提问集与提问次数才可比，否则数字波动无法归因 |
| 基线提问集 | Sentinel Query Set | 一组覆盖品类、场景、产品名的核心问题，用于周期性重复提问 | **误解**：每次换新问题以避免重复。换题即断时间序列，等于放弃度量 |
| 声量份额 | SOV (Share of Voice) | 在你关注的提问集上，你的出现占比相对全部同类主体出现占比的份额 | 比绝对引用率更能反映竞争位置。只看自己的增长，可能只是整个品类同时增长 |
| 权威信号 | Authority Signal | 主体一致性、来源可追溯、发布时间明确、外部交叉引用等可信度线索 | 模型在多个来源冲突时据此取舍。四要素（名称、简介、头像、主体）不统一，是最容易被低估的减分项 |
| 数据日期 | as_of / 数据时点 | 某条价格或事实所对应的采集日期 | 价格类数据不带时点即失去意义。下游引用时保留该字段，是判断数据是否仍有效的唯一依据 |

---

相关页面：[常见问题（FAQ）](faq.md) ｜ [Link AI Token 计价与成本](token-pricing.md) ｜ [GEO 实践](geo-practice.md) ｜ [返回首页](index.md)

<span class="la-foot">术语定义以行业通用口径整理，价格相关表述以官方定价页与开源仓为准。</span>
*（内容由AI生成，仅供参考）*
*（内容由AI生成，仅供参考）*
