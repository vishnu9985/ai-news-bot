import requests
import feedparser
import os
from transformers import pipeline

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# =========================
# NEWS SOURCES
# =========================
RSS_FEEDS = {
    "📊 Indian Market": "https://news.google.com/rss/search?q=indian+stock+market+nifty+sensex",
    "🌍 Geopolitics": "https://news.google.com/rss/search?q=geopolitical+tensions+war+china+usa+india",
    "💰 Economy": "https://news.google.com/rss/search?q=inflation+RBI+GDP+interest+rates+India",
    "🏭 Industry": "https://news.google.com/rss/search?q=IT+banking+energy+sector+India",
    "🌐 Global Markets": "https://news.google.com/rss/search?q=US+market+Fed+global+stocks"
}

# =========================
# HIGH ALERT KEYWORDS
# =========================
HIGH_ALERT_KEYWORDS = [
    "crash", "war", "conflict", "tensions", "sanctions",
    "inflation surge", "interest rate hike", "rate hike",
    "RBI decision", "Fed decision", "recession",
    "market fall", "sell-off", "fii selling", "volatility"
]

# =========================
# FAST AI MODEL
# =========================
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-small"
)

# =========================
# TELEGRAM FUNCTION
# =========================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

# =========================
# HIGH ALERT FILTER
# =========================
def is_high_alert(text):
    text_lower = text.lower()
    for keyword in HIGH_ALERT_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

# =========================
# AI EXPLANATION
# =========================
def process_news(text):
    prompt = f"""
Explain this financial news simply.

{text}

Include:
- What happened
- Why it matters
- Market impact
"""

    try:
        output = generator(prompt, max_length=120)[0]['generated_text']
        return output.strip()
    except:
        return text

# =========================
# GENERATE REPORT
# =========================
def generate_report():
    final_message = "⚠️ HIGH ALERT MARKET NEWS\n\n"
    found_alert = False

    for category, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        articles = feed.entries[:2]

        for article in articles:
            title = article.title

            if is_high_alert(title):
                explanation = process_news(title)

                final_message += f"{category}\n"
                final_message += f"🚨 {explanation}\n\n"
                final_message += "----------------------\n\n"

                found_alert = True

    if not found_alert:
        return "✅ No high-impact financial news right now."

    return final_message

# =========================
# RUN ONCE
# =========================
if __name__ == "__main__":
    try:
        report = generate_report()
        send_telegram(report)
        print("✅ High alert news sent")
    except Exception as e:
        print("❌ Error:", e)
