import re
import json
from collections import defaultdict

def load_categories(filename='categories.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['categories'], data['url_patterns'], data['domain_patterns']

CATEGORIES, URL_PATTERNS, DOMAIN_PATTERNS = load_categories()

MIN_SCORE_THRESHOLD = 4

def classify_text(text, url):
    text = text.lower()
    scores = defaultdict(int)

    # 1. Анализ домена
    for category, domains in DOMAIN_PATTERNS.items():
        for domain in domains:
            if domain in url.lower():
                scores[category] += 10 # Большой вес для домена

    # 2. Анализ URL
    for category, patterns in URL_PATTERNS.items():
        for pattern in patterns:
            if pattern in url.lower():
                scores[category] += 5

    # 3. Анализ текста по ключевым словам с весами
    for category, keywords_with_weights in CATEGORIES.items():
        for keyword, weight in keywords_with_weights.items():
            found = re.findall(rf"\b{keyword}[а-я]*\b", text)
            scores[category] += len(found) * weight

    # 3. Определение категории
    if not any(scores.values()):
        return ["Другое"]

    sorted_categories = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    best_category = sorted_categories[0]
    if best_category[1] >= MIN_SCORE_THRESHOLD:
        return [best_category[0]]
    else:
        return ["Другое"]
