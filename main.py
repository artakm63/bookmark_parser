import sys
import os
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import re
import json
from collections import defaultdict
import concurrent.futures
import argparse
import logging
from tqdm import tqdm

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from category_classifier import classify_text

TIMEOUT = 10
DEFAULT_INPUT_FILE = 'ссылки.txt'
DEFAULT_SUCCESS_FILE = 'output/success.txt'
DEFAULT_FAILED_FILE = 'output/failed.txt'
DEFAULT_METADATA_FILE = 'output/metadata_tokens.txt'
DEFAULT_CATEGORIZED_FILE = 'output/categorized_links.txt'
DEFAULT_JSON_FILE = 'output/categorized_links.json'

def main():
    def extract_metadata_and_text(html):
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string.strip() if soup.title and soup.title.string else ''
        desc = ''
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if isinstance(desc_tag, Tag):
            content = desc_tag.get('content', '')
            if isinstance(content, list):
                content = ' '.join(str(x) for x in content)
            desc = str(content).strip()
        
        for script in soup(["script", "style"]):
            script.extract()
        page_text = soup.get_text()
        lines = (line.strip() for line in page_text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return title, desc, text

    def tokenize(text):
        return re.findall(r'\w+', text.lower())

    def process_url(url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            resp = requests.get(url, timeout=TIMEOUT, headers=headers)
            resp.raise_for_status()  # Проверка на ошибки HTTP (4xx или 5xx)
            resp.encoding = resp.apparent_encoding
            title, desc, page_text = extract_metadata_and_text(resp.text)
            
            meta_text = title + ' ' + desc
            categories = classify_text(meta_text, url)
            
            if categories == ['Другое']:
                categories = classify_text(page_text, url)

            tokens = tokenize(meta_text)
            
            return {
                'url': url,
                'status': 'success',
                'title': title,
                'description': desc,
                'tokens': tokens,
                'categories': categories
            }
        except Exception as e:
            return {
                'url': url,
                'status': 'failed',
                'error': str(e)
            }

    parser = argparse.ArgumentParser(description='Парсер и классификатор ссылок.')

    parser.add_argument('--input', type=str, default=DEFAULT_INPUT_FILE, help='Входной файл со ссылками')
    parser.add_argument('--bookmarks', type=str, help='HTML-файл с закладками из браузера')
    parser.add_argument('--success', type=str, default=DEFAULT_SUCCESS_FILE, help='Файл для успешно проверенных ссылок')
    parser.add_argument('--failed', type=str, default=DEFAULT_FAILED_FILE, help='Файл для нерабочих ссылок')
    parser.add_argument('--metadata', type=str, default=DEFAULT_METADATA_FILE, help='Файл для метаданных')
    parser.add_argument('--categorized', type=str, default=DEFAULT_CATEGORIZED_FILE, help='Файл для отсортированных ссылок')
    parser.add_argument('--json', type=str, default=DEFAULT_JSON_FILE, help='JSON-файл с результатами')
    args = parser.parse_args()

    # Создание директории output, если она не существует
    if not os.path.exists('output'):
        os.makedirs('output')

    if args.bookmarks:
        logging.info(f'Импорт закладок из файла: {args.bookmarks}')
        try:
            urls = extract_urls_from_bookmarks(args.bookmarks)
        except FileNotFoundError:
            logging.error(f'Файл не найден: {args.bookmarks}')
            return
    else:
        logging.info(f'Начало обработки файла: {args.input}')
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logging.error(f'Файл не найден: {args.input}')
            return

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(process_url, url): url for url in urls}
        for future in tqdm(concurrent.futures.as_completed(future_to_url), total=len(urls)):
            results.append(future.result())

    success_urls = [r['url'] for r in results if r['status'] == 'success']
    failed_urls = {r['url']: r['error'] for r in results if r['status'] == 'failed'}

    logging.info(f'Обработано {len(urls)} ссылок. Успешно: {len(success_urls)}, с ошибками: {len(failed_urls)}')

    with open(args.success, 'w', encoding='utf-8') as f:
        for url in success_urls:
            f.write(url + '\n')

    with open(args.failed, 'w', encoding='utf-8') as f:
        for url, error in failed_urls.items():
            f.write(f'{url} - Ошибка: {error}\n')


    categorized = defaultdict(list)
    for r in results:
        if r['status'] == 'success':
            for cat in r['categories']:
                categorized[cat].append(r)
        else:
            categorized['Ошибки обработки'].append(r)

    with open(args.metadata, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(f"URL: {r['url']}\n")
            if r['status'] == 'failed':
                f.write(f"ERROR: {r['error']}\n\n")
            else:
                f.write(f"TITLE: {r['title']}\nDESC: {r['description']}\n")
                f.write(f"TOKENS: {r['tokens']}\nCATEGORIES: {', '.join(r['categories'])}\n\n")

    with open(args.categorized, 'w', encoding='utf-8') as f:
        for category, items in categorized.items():
            f.write(f'=== {category} ===\n')
            for item in items:
                f.write(f"- {item['url']}")
                if item['status'] == 'failed':
                    f.write(f" [Ошибка: {item['error']}]")
                f.write("\n")
            f.write("\n")

    with open(args.json, 'w', encoding='utf-8') as f:
        json.dump(categorized, f, ensure_ascii=False, indent=4)



if __name__ == '__main__':
    main()
