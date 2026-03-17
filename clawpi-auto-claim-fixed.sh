#!/bin/bash
# 龙虾派自动抢红包脚本（修复版）
# 每5分钟运行一次

JWT="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImRldi1rZXkifQ.eyJhZ2VudF9pZCI6ImY3ZTA0YTgzLWVlMDktNDM0ZS04MWQzLTViZjk4YzQ3Mjg0NyIsImlhdCI6MTc3MzcwNTQ5MiwiZXhwIjoxNzc2Mjk3NDkyfQ.CVTnJcxmNz9HC4ZACvanr7R0mE7SpTX9dEeBIAblTQCRQEmymmjNcGLJCn_Er8nrz8_QGMFvPsfjqVG8e4W0bP2HmA3rh2R99gXKQd7By6xpv1LoH8f5HYEraE_IZQkyyaTeclLUqNBr4nlID5DVEZE3agrA8zaZkookbHXePdOErM5wDgVvG-0djr4LQpZJr4oVDn8S-9EQdnsDhOGnxekHxVyatbdYkW948riilZLhtmJxwFQgHOHfiNHCZyMJRObXWW2DFGcQwcjGQcw0wXYLtu1OtVMS9istT3Q1-LqDLGyF51NzmMIosxCaBZNsoZD9FvrZ8C-_hpafrFB0YQ"
AGENT_ID="f7e04a83-ee09-434e-81d3-5bf98c472847"
LOG_FILE="/root/.bounty-hunter/clawpi-claims.log"

echo "=== $(date) ===" >> $LOG_FILE

# 获取可领取的红包
echo "检查可用红包..." >> $LOG_FILE
RESPONSE=$(curl -s "https://clawpi-v2.vercel.app/api/redpacket/available?n=50" \
  -H "Authorization: Bearer $JWT")

# 提取可领取的红包ID和金额
RED_PACKETS=$(echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        for rp in data.get('redPackets', []):
            if rp.get('can_claim') and not rp.get('already_claimed'):
                print(f\"{rp['id']}:{rp['per_amount']}:{rp.get('creator_nickname', '未知')}\")
except:
    pass
")

if [ -z "$RED_PACKETS" ]; then
    echo "没有可领取的红包" >> $LOG_FILE
    exit 0
fi

# 遍历并领取每个红包
echo "发现 $(echo "$RED_PACKETS" | wc -l) 个可领取红包" >> $LOG_FILE

while IFS= read -r line; do
    RED_PACKET_ID=$(echo "$line" | cut -d: -f1)
    AMOUNT=$(echo "$line" | cut -d: -f2)
    CREATOR=$(echo "$line" | cut -d: -f3)
    
    echo "尝试领取红包 #$RED_PACKET_ID (来自 $CREATOR)..." >> $LOG_FILE
    
    # 创建收款链接 - 修复：使用 jq 正确提取 URL
    PAYMENT_LINK=$(fluxa-wallet paymentlink-create --amount $AMOUNT --desc "领取 $CREATOR 的红包 #$RED_PACKET_ID" 2>&1 | jq -r '.data.paymentLink.url // empty')
    
    if [ -z "$PAYMENT_LINK" ]; then
        echo "创建收款链接失败" >> $LOG_FILE
        continue
    fi
    
    echo "  Payment Link: $PAYMENT_LINK" >> $LOG_FILE
    
    # 领取红包
    CLAIM_RESULT=$(curl -s -X POST "https://clawpi-v2.vercel.app/api/redpacket/claim" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $JWT" \
        -d "{\"redPacketId\":$RED_PACKET_ID,\"paymentLink\":\"$PAYMENT_LINK\"}")
    
    # 检查是否成功
    if echo "$CLAIM_RESULT" | grep -q '"paid":true'; then
        TX_HASH=$(echo "$CLAIM_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('claim',{}).get('tx_hash','N/A'))")
        AMOUNT_USDC=$(python3 -c "print(f'{int($AMOUNT)/1000000:.6f}')")
        echo "✅ 成功领取! $AMOUNT_USDC USDC | TX: $TX_HASH" >> $LOG_FILE
        
        # 记录收入
        python3 /root/.openclaw/workspace/track_money.py log "clawpi_redpacket" $AMOUNT_USDC "Red packet #$RED_PACKET_ID from $CREATOR"
        
        # 发送通知到Telegram
        message send --channel telegram --target 677288391 --message "🧧 抢到红包啦！\n\n来自: $CREATOR\n金额: $AMOUNT_USDC USDC\nTX: $TX_HASH"
    else
        echo "❌ 领取失败: $CLAIM_RESULT" >> $LOG_FILE
    fi
    
    # 等待1秒再处理下一个
    sleep 1
done <<< "$RED_PACKETS"

echo "扫描完成" >> $LOG_FILE
echo "" >> $LOG_FILE
