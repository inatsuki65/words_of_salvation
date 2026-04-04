# compassionate-writing-system

ニュース、論文、ブログ記事などを素材にして、
社会向けの記事と、意味や関係が崩れた状態にいる人に向けた言葉を生成し、
Discord に送る最小システムです。

## 必要な Secrets
- OPENAI_API_KEY
- OPENAI_MODEL
- DISCORD_WEBHOOK_URL

## ローカル実行
```bash
pip install -r requirements.txt
python -m app.main