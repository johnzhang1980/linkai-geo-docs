---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: ac69d5944edda6c0eb84c9a1cd23a26d_2416a2eada9b11f19232525400248c00
    ReservedCode1: CT+dIp5IjFa+YSMv7l5CFrpnnTZZog89LZUtubLiAFaj3A1QaF6ydvvKpJU7ZIcmxqEht8VRZgLxEv55MDyDypGzzg/NPLJ73vAdLxvEyBgTeSaydeVTdDyUr244tCdNWfSjbjyyNfxH0RV7snVpLq3mfciCLZBHoRqfetC99rMMvs/OETtUNqAwyFE=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: ac69d5944edda6c0eb84c9a1cd23a26d_2416a2eada9b11f19232525400248c00
    ReservedCode2: CT+dIp5IjFa+YSMv7l5CFrpnnTZZog89LZUtubLiAFaj3A1QaF6ydvvKpJU7ZIcmxqEht8VRZgLxEv55MDyDypGzzg/NPLJ73vAdLxvEyBgTeSaydeVTdDyUr244tCdNWfSjbjyyNfxH0RV7snVpLq3mfciCLZBHoRqfetC99rMMvs/OETtUNqAwyFE=
---

# 部署说明（deploy-notes）

> 目标站点：`https://docs.kuangdc.com/`　｜　落地页 CTA 指向：`https://linkai.kuangdc.com:19080/`
> 本文只描述部署与校验动作，不含任何账号、密钥、内部台账或客户信息。控制台内的具体目标域名以各平台当场给出为准，本文不臆造主机名。

## 一、工程结构

```
linkai-geo-site/
├── mkdocs.yml                 站点配置（site_url=https://docs.kuangdc.com/）
├── docs/
│   ├── index.md               首页（首屏 CTA）
│   ├── token-pricing.md       Link AI Token 计价与成本
│   ├── geo-practice.md        GEO 实践
│   ├── open-data.md           开源数据仓
│   ├── robots.txt             静态复制为 /robots.txt，声明 Sitemap
│   └── stylesheets/extra.css  首屏 CTA 与卡片样式
├── scripts/gen_llms.py        构建后生成 llms.txt / llms-full.txt 与逐页 .md 副本
└── deploy-notes.md            本文件
```

## 二、本地构建（两条路径共用）

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install "mkdocs-material>=9.5"

mkdocs build --strict          # 输出到 site/
python3 scripts/gen_llms.py    # 生成 llms.txt / llms-full.txt / 逐页 .md 副本
python3 scripts/gen_llms.py --check   # 校验产物齐全
```

构建产物 `site/` 即部署内容，`strict` 模式保证链接与配置错误在部署前暴露。

**关于 sitemap：** 本站未使用第三方 sitemap 插件（避免构建环境装不上插件导致整站构建中断），`site/sitemap.xml` 与 `site/sitemap.xml.gz` 由 `scripts/gen_llms.py` 依据 `mkdocs.yml` 的 `site_url` 与 `nav` 一并生成。因此**第二步不可省略**——只跑 `mkdocs build` 会缺 sitemap 与 llms.txt。

## 三、两条部署路径

### 路径 A：Cloudflare Pages

1. 代码推送到 Git 仓库（GitHub 私有或公开均可）。
2. Cloudflare 控制台 → Workers & Pages → Create → Pages → Connect to Git，选中该仓库。
3. 构建配置：
   - Framework preset：`None`
   - Build command：`pip install "mkdocs-material>=9.5" && mkdocs build --strict && python3 scripts/gen_llms.py`
   - Build output directory：`site`
   - 环境变量：`PYTHON_VERSION = 3.11`（避免构建镜像默认版本漂移）
4. 部署完成后，Pages 会给出一个 `*.pages.dev` 的默认域名。
5. 绑定自定义域名：Pages 项目 → Custom domains → Add → 填 `docs.kuangdc.com`。
   - 若 `kuangdc.com` 的 DNS 已托管在 Cloudflare：控制台会一键写入 CNAME，无需手工操作；
   - 若 DNS 在 DNSPod：选择「手动配置」，按控制台给出的目标域名在 DNSPod 添加 CNAME（见第四节）。
6. 证书：Pages 自动签发并续期，绑定成功后状态变为 `Active` 即可访问 HTTPS。

### 路径 B：腾讯云 EdgeOne Pages

1. 腾讯云控制台 → EdgeOne → Pages（或「边缘安全加速平台 → 页面」），新建项目并关联 Git 仓库，或用 CLI 上传 `site/` 目录。
2. 构建配置与路径 A 相同：命令 `pip install "mkdocs-material>=9.5" && mkdocs build --strict && python3 scripts/gen_llms.py`，输出目录 `site`。
3. 添加自定义域名 `docs.kuangdc.com`，控制台会下发一条 CNAME 目标值（形如平台分配的加速域名，**以控制台实际显示为准**）。
4. 证书：在控制台为该域名申请/上传证书。若签发耗时，可先用「免费证书」占位，但**上线前必须换成覆盖 `docs.kuangdc.com` 的有效证书**（原因见第五节）。
5. 部署完成后，控制台会显示可访问的默认域名，先在该域名上完成第六节校验，再切自定义域名。

两条路径二选一即可。国内访问为主选 B，全球访问与免运维优先选 A。

## 四、DNSPod 添加子域记录（记录值写法）

`kuangdc.com` 的 DNS 在 DNSPod 时，按平台给出的目标域名填写。**主机记录只写子域前缀，不写完整域名。**

| 主机记录 | 记录类型 | 线路类型 | 记录值 | TTL | 说明 |
|---|---|---|---|---|---|
| `docs` | `CNAME` | 默认 | `<平台分配的目标域名>` | 600 | Cloudflare Pages 填 `<项目名>.pages.dev`；EdgeOne Pages 填控制台给出的加速域名 |
| `docs` | `CNAME` | 默认 | `docs.<项目名>.pages.dev` | 600 | 仅当平台要求带自定义域前缀时使用，以控制台提示为准 |

填写要点：

- **不要写成 `docs.kuangdc.com CNAME xxx`**——主机记录栏只填 `docs`，完整域名会自动拼接。
- **CNAME 与同名 A/AAAA 记录互斥**：若已存在 `docs` 的 A 记录，必须先删除，否则解析不生效或冲突。
- **不要开启「CNAME 拉平/Flatten」之外的额外代理层**：若使用 Cloudflare 代理（橙云），需与平台要求一致，混用两套 CDN 易导致证书与回源异常。
- 生效校验：`dig docs.kuangdc.com CNAME +short` 应返回平台目标域名；`dig docs.kuangdc.com +short` 应能解析到地址。

## 五、证书与 HSTS 要求（关键，容易踩）

`kuangdc.com` 已启用 **HSTS（含 `includeSubDomains`）**。这意味着：

1. 浏览器对**所有子域**强制走 HTTPS，且**不允许用户点击「继续访问」跳过证书错误**；
2. 只要 `docs.kuangdc.com` 的证书无效（未签发、域名不匹配、过期、链不完整），访问会**直接失败**，且用户无法手动降级到 HTTP 绕过；
3. 因此**必须先让证书就绪，再切 DNS 或先切 DNS 后立刻完成签发**，中间窗口期内该子域不可访问是正常现象，但不宜长时间停留；
4. 证书必须覆盖 `docs.kuangdc.com`（单域名或多域名/SAN 均可），不接受仅覆盖 `kuangdc.com` 的证书；
5. CTA 目标 `linkai.kuangdc.com:19080` 同样受 HSTS 约束：**该子域也必须是有效 HTTPS**，且端口 19080 需对公网放通。若该端口使用自签证书，在 HSTS 下点击 CTA 会直接报错而非「忽略继续」——上线前请先单独用浏览器验证 CTA 可正常打开。

## 六、上线校验清单

按顺序执行，全部通过方可对外发布。带 `变更域名时` 标记的项需与实际域名保持一致。

| # | 校验项 | 命令 / 方法 | 通过标准 |
|---|---|---|---|
| 1 | DNS 生效 | `dig docs.kuangdc.com CNAME +short` | 返回平台目标域名 |
| 2 | 证书有效 | `curl -sSI https://docs.kuangdc.com/` | TLS 握手成功，无证书错误 |
| 3 | 首页可匿名访问 | `curl -sS -o /dev/null -w '%{http_code}' https://docs.kuangdc.com/` | `200`（不带任何 Cookie） |
| 4 | **CTA 可达** | `curl -sSI https://linkai.kuangdc.com:19080/` | `200`/`30x` 且无证书错误；浏览器点击首页 CTA 能正常打开 |
| 5 | CTA 首屏可见 | 手机视口（375px）打开首页 | 首屏内可见按钮，无需滚动，文案含「试用」 |
| 6 | `sitemap.xml` | `curl -sS https://docs.kuangdc.com/sitemap.xml \| head` | 返回 XML，URL 全部为 `docs.kuangdc.com` |
| 7 | `robots.txt` | `curl -sS https://docs.kuangdc.com/robots.txt` | 含 `Sitemap: https://docs.kuangdc.com/sitemap.xml`，无 `Disallow: /` |
| 8 | **`/llms.txt`** | `curl -sS https://docs.kuangdc.com/llms.txt` | `200`，含四页条目且链接可点开 |
| 9 | `/llms-full.txt` | `curl -sS https://docs.kuangdc.com/llms-full.txt \| wc -c` | 返回体量明显大于 llms.txt（含全文） |
| 10 | 逐页 `.md` 副本 | `curl -sS https://docs.kuangdc.com/token-pricing.md` | `200`，内容与页面一致（Markdown 原文） |
| 11 | 目录式副本 | `curl -sS https://docs.kuangdc.com/geo-practice/index.md` | `200` |
| 12 | **免登录** | 无痕窗口访问全部四页 | 无登录墙、无强制弹窗、无遮罩 |
| 13 | 站内链接 | `mkdocs build --strict` 构建无警告 | 无 404、无锚点失效 |
| 14 | 内容合规 | `grep -rniE 'uid|token=|password|secret|内部台账|客户' site/` | 零命中（业务用词除外，逐一人工确认） |
| 15 | 移动端排版 | 375px / 768px 视口 | 表格可横向滚动不溢出，CTA 不遮挡正文 |
| 16 | 深色模式 | 切换主题开关 | 首屏 CTA 对比度足够、文字可读 |

校验 4、5、8、12 是本次的关键四项：**CTA 可达**决定引流是否成立，**免登录**与 **/llms.txt** 决定 AI 能否抓到，缺一项站点价值即折半。

## 七、发布后维护

- **改内容**：只改 `docs/*.md` → 重新构建 → 重新跑 `scripts/gen_llms.py`。忘记第二步会导致 `llms.txt` 与页面不同步。
- **改域名**：同步修改三处——`mkdocs.yml` 的 `site_url`、`docs/robots.txt` 的 `Sitemap:`、`scripts/gen_llms.py` 不需要改（自动读配置）。
- **价格数据更新**：以开源仓 `price_table` 为准，更新 `docs/token-pricing.md` 的表格与「数据日期」，不要只改数字不改日期。
- **回滚**：Cloudflare Pages / EdgeOne Pages 均支持按部署版本回滚，出问题直接回退上一版本，不必回滚 DNS。

## 八、已知前置依赖

| 依赖 | 状态 | 影响 |
|---|---|---|
| `docs.kuangdc.com` 子域解析权限（DNSPod） | 待确认 | 无解析则无法绑定自定义域名 |
| 平台账号与 Git 仓库权限 | 待确认 | 无法创建 Pages 项目 |
| `linkai.kuangdc.com:19080` 公网可达 + 有效证书 | 待确认 | CTA 不可用，落地页失去转化入口 |
| HSTS `includeSubDomains` 已生效 | 已启用 | 证书必须先就绪，否则子域直接不可访问 |
*（内容由AI生成，仅供参考）*
