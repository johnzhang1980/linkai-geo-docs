#!/bin/bash
# Link AI GEO 文档站一键发布：构建 -> 生成 GEO 资产 -> 上传 Cloudflare Pages
set -e
export PATH="/Users/gloria/Library/Application Support/com.tencent.mac.marvis/components/MarvisGateway/Current/binaries/node/current/bin:$PATH"
cd "$(dirname "$0")/.."

# mkdocs 运行环境：优先用 VENV 变量指定的虚拟环境，否则用当前会话 venv
VENV="${VENV:-$HOME/.venvs/mkdocs-geo}"
[ -x "$VENV/bin/mkdocs" ] || VENV="/Users/gloria/Library/Application Support/com.tencent.mac.marvis/MarvisData/User/oAN1i2Y7ewUMVATqaVMJLZ0yhubI/workspace/conv_19e52029db3_04fc2f9374b3/temp/mkdocs-venv"

"$VENV/bin/mkdocs" build --strict
python3 scripts/gen_llms.py
wrangler pages deploy site --project-name=linkai-geo-docs --branch=main --commit-dirty=true
echo "已发布: https://docs.kuangdc.com"
