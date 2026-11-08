#!/bin/bash
# Link AI GEO 文档站一键发布：构建 -> 生成 GEO 资产 -> 上传 Cloudflare Pages -> IndexNow 提频
set -e
export PATH="/Users/gloria/Library/Application Support/com.tencent.mac.marvis/components/MarvisGateway/Current/binaries/node/current/bin:$PATH"
cd "$(dirname "$0")/.."

# mkdocs 运行环境：优先用 VENV 变量指定的虚拟环境，否则用当前会话 venv
VENV="${VENV:-$HOME/.venvs/mkdocs-geo}"
[ -x "$VENV/bin/mkdocs" ] || VENV="/Users/gloria/Library/Application Support/com.tencent.mac.marvis/MarvisData/User/oAN1i2Y7ewUMVATqaVMJLZ0yhubI/workspace/conv_19e52029db3_04fc2f9374b3/temp/mkdocs-venv"

# ---------------------------------------------------------------- IndexNow 提频
# 背景（2026-11-08 实测）：本机走 iPhone 热点时，系统 DNS 会把 api.indexnow.org
# 解析到错误 IP，表现为 "Recv failure: Connection reset by peer"。
# 这不是网络封锁——用公共 DNS 取到真实 IP（微软 Edge 网络 bx-msedge.net）后
# 经 --resolve 固定该 IP 即可 200。故此处一律先查公共 DNS 再推送。
PUBLIC_DNS="${PUBLIC_DNS:-223.5.5.5}"

push_indexnow() {
  local site_url="$1"
  case "$site_url" in */) ;; *) site_url="$site_url/" ;; esac
  local host="${site_url#*://}"; host="${host%%/*}"

  # key 文件：docs/<32位hex>.txt，随 mkdocs 构建复制进 site/
  local key_file key
  key_file=$(ls docs/*.txt 2>/dev/null | grep -E '/[0-9a-f]{32}\.txt$' | head -1 || true)
  if [ -z "$key_file" ]; then
    echo "[indexnow] 未找到 32 位 hex key 文件（docs/<key>.txt），跳过推送"
    return 0
  fi
  key=$(basename "$key_file" .txt)

  # 提交清单直接取 sitemap，避免手写 URL 与站点漂移
  local payload
  payload=$(python3 - "$site_url" "$host" "$key" <<'PY'
import json, pathlib, re, sys
site, host, key = sys.argv[1:4]
xml = pathlib.Path("site/sitemap.xml").read_text(encoding="utf-8")
urls = re.findall(r"<loc>(.*?)</loc>", xml)
print(json.dumps({
    "host": host,
    "key": key,
    "keyLocation": f"{site}{key}.txt",
    "urlList": urls,
}, ensure_ascii=False))
PY
)
  if [ -z "$payload" ]; then
    echo "[indexnow] sitemap 解析失败，跳过推送"
    return 0
  fi

  # 公共 DNS 解析 + --resolve 固定；dig 缺失时退化为直连
  local ip="" resolv=""
  if command -v dig >/dev/null 2>&1; then
    ip=$(dig +short api.indexnow.org @"$PUBLIC_DNS" 2>/dev/null | grep -E '^[0-9.]+$' | tail -1 || true)
  fi
  [ -n "$ip" ] && resolv="--resolve api.indexnow.org:443:$ip"

  local code
  # 端点 1：IndexNow 官方（共享给 Bing/Yandex/Seznam 等）
  code=$(printf '%s' "$payload" | curl -sS --http1.1 -m 25 $resolv -o /dev/null -w '%{http_code}' \
      -X POST "https://api.indexnow.org/indexnow" \
      -H "Content-Type: application/json; charset=utf-8" --data-binary @- 2>/dev/null || echo "000")
  echo "[indexnow] api.indexnow.org -> ${code}${ip:+ (resolved $ip)}"

  # 端点 2：Bing 专用入口，双通道冗余
  code=$(printf '%s' "$payload" | curl -sS --http1.1 -m 25 -o /dev/null -w '%{http_code}' \
      -X POST "https://www.bing.com/indexnow" \
      -H "Content-Type: application/json; charset=utf-8" --data-binary @- 2>/dev/null || echo "000")
  echo "[indexnow] www.bing.com      -> ${code}"

  # 200/202 视为已受理；失败只告警，不影响已完成的部署
  echo "[indexnow] 已提交 $(printf '%s' "$payload" | python3 -c 'import json,sys;print(len(json.load(sys.stdin)["urlList"]))') 条 URL"
}

"$VENV/bin/mkdocs" build --strict
python3 scripts/gen_llms.py
wrangler pages deploy site --project-name=linkai-geo-docs --branch=main --commit-dirty=true
echo "已发布: https://docs.kuangdc.com"

SITE_URL=$(grep -E "^site_url:" mkdocs.yml | head -1 | awk '{print $2}')
push_indexnow "${SITE_URL:-https://docs.kuangdc.com/}"
