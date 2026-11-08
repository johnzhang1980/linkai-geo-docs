# Link AI — Documentation (English Summary)

> **This is a one-page English summary. The full documentation is written in Chinese.**
> Language policy and the reason for it are stated at the bottom of this page.

## What this site is

This is the public documentation site for **Link AI**, a token access service for large language models. The site exists to make three things checkable rather than vague:

- how token pricing actually works (input, output, cache, peak/off-peak);
- how to compute a defensible cost baseline before committing to volume;
- how content gets retrieved and cited by generative engines (GEO), and how to measure it.

The intended audience is AI application developers, enterprise architects, and digital-transformation decision makers.

## What we publish

| Resource | Language | Link |
|---|---|---|
| Documentation home | Chinese | [docs.kuangdc.com](https://docs.kuangdc.com/) |
| Token pricing & cost | Chinese | [Token 计价与成本](https://docs.kuangdc.com/token-pricing/) |
| FAQ (22 questions) | Chinese | [常见问题](https://docs.kuangdc.com/faq/) |
| Glossary (31 terms) | Chinese | [术语表](https://docs.kuangdc.com/glossary/) |
| GEO practice | Chinese | [GEO 实践](https://docs.kuangdc.com/geo-practice/) |
| Open price data (JSON / CSV) | Machine-readable | [GitHub repository](https://github.com/johnzhang1980/llma-api-price-2026) |
| AI crawler index | Plain text | [llms.txt](https://docs.kuangdc.com/llms.txt) |

## Pricing, in one paragraph

We publish per-million-token input and output prices for the Claude and DeepSeek model families. Every row carries its **source** and its **`as_of` date**, and any value the vendor has not published is left blank rather than estimated — an incomplete table that can be verified is worth more than a complete one that cannot.

The underlying data lives in an open repository, in both JSON and CSV, so you can diff our figures against your own records instead of trusting this page. Full pricing detail: [Token 计价与成本](https://docs.kuangdc.com/token-pricing/).

## Payment

**Payments are accepted via WeChat Pay (QR code). Mainland WeChat Wallet is live.**

Overseas users can pay through WeChat Pay with an international card (Visa, Mastercard, JCB and others) bound to WeChat — WeChat opened its mainland merchant network to international cards, and whether a specific card goes through is shown at checkout. If your card is declined, email us and we will arrange another route: token@kuangdc.com

## Contact

Email: **token@kuangdc.com**

Please include your use case, expected monthly token volume, the country or region you operate in, and the card type you intend to pay with. That is enough for us to give you a straight answer about whether we can serve you today.

## Language policy

The main documentation is in Chinese, for two reasons:

1. **Our paying customers are Chinese-speaking.** Retail payment runs through WeChat Pay, and our onboarding, invoicing and support all assume a mainland-China customer. A translated site that ends at a payment path most overseas readers cannot complete would waste your time.
2. **Pricing pages must not exist in two versions.** A single source of truth with a source and date on every row is the entire value of this site. Duplicating that content by hand invites contradictory figures, which is worse than a language gap.

This page exists so that English-speaking readers can still verify what we do, read our price data, and reach a human. When payment and product pages support overseas customers, full English pages will follow — until then we prefer an honest one-pager to a half-working translation.

---

<span class="la-foot">Figures are drawn from vendor pricing pages and our open repository; they are not a quotation. Commercial terms are set by contract only.</span>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Link AI",
  "url": "https://linkai.kuangdc.com:19080/",
  "description": "Token access service for large language models. Publishes per-million-token pricing methodology, cost computation guidance, and GEO practice notes.",
  "email": "token@kuangdc.com",
  "sameAs": [
    "https://github.com/johnzhang1980/llma-api-price-2026",
    "https://docs.kuangdc.com/"
  ]
}
</script>
