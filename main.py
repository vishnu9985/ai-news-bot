import requests
import feedparser
import os
from transformers import pipeline

# =========================
# CONFIG (FROM GITHUB SECRETS)
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
# FAST MODEL (COMPATIBLE)
# =========================
generator = pipeline(
    "text-generation",
    model="sshleifer/tiny-gpt2"   # FAST + WORKS
)

# =========================
# TELEGRAM FUNCTION
# =========================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

# =========================
# 🚨 SIMPLE HIGH ALERT FILTER (KEYWORDS)
# =========================
def is_high_alert(text):
    keywords = [
        "war", "crash", "inflation", "rbi", "fed",
        "interest rate", "recession", "conflict",
        "fii selling", "market fall", "global tension"
    ]
    
    text_lower = text.lower()
    return any(word in text_lower for word in keywords)

# =========================
# SIMPLE EXPLANATION (FAST)
# =========================
def process_news(text):
    return f"{text}\n👉 This news may impact markets. Watch closely."

# =========================
# GENERATE REPORT
# =========================
def generate_report():
    final_message = "🚨 HIGH ALERT AI NEWS 🚨\n\n"
    found = False

    for category, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        articles = feed.entries[:2]

        category_added = False

        for article in articles:
            title = article.title

            if is_high_alert(title):
                explanation = process_news(title)

                if not category_added:
                    final_message += f"{category}\n"
                    category_added = True

                final_message += f"📰 {explanation}\n\n"
                found = True

    if not found:
        final_message = "✅ No high-impact financial news right now."

    return final_message

# =========================
# RUN ONCE (GITHUB ACTIONS)
# =========================
if __name__ == "__main__":
    try:
        report = generate_report()
        send_telegram(report)
        print("✅ News sent successfully")
    except Exception as e:
        print("❌ Error:", e)
