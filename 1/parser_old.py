import requests
from bs4 import BeautifulSoup
import csv
import json
import xml.etree.ElementTree as ET
from typing import List, Dict
import time
from urllib.parse import urljoin, urlparse


class RisbarParser:
    def __init__(self, base_url: str = "https://risbar.kz"):
        """
        Парсер для сайта risbar.kz
        :param base_url: Базовый URL сайта
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        })
        self.products = []

    def fetch_page(self, url: str) -> BeautifulSoup:
        """
        Загрузка и парсинг страницы
        :param url: URL страницы
        :return: BeautifulSoup объект
        """
        try:
            print(f"Загрузка: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            # time.sleep(1)  # Пауза между запросами
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"❌ Ошибка загрузки {url}: {e}")
            return None

    def parse_product(self, product_url: str) -> Dict:
        """
        Парсинг детальной страницы товара
        :param product_url: URL товара
        :return: Словарь с данными товара
        """
        soup = self.fetch_page(product_url)
        if not soup:
            return None

        product = {
            'url': product_url,
            'title': '',
            'description': '',
            'details': '',
            'category': '',
            'article': '',
            'availability': '',
            'images': [],
            'price': ''
        }

        try:
            # Название товара (основной заголовок на странице)
            title_selectors = ['h1.product_title', 'h1', '.product_title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    product['title'] = title_elem.get_text(strip=True)
                    break

            # Артикул - ищем текст после "Артикул"
            article_block = soup.find(text=lambda t: t and 'Артикул' in t)
            if article_block:
                parent = article_block.find_parent()
                if parent:
                    article_text = parent.get_text(strip=True)
                    # Извлекаем артикул после двоеточия
                    if ':' in article_text:
                        product['article'] = article_text.split(':', 1)[
                            1].strip()

            # Категория - ищем текст после "Категория"
            category_block = soup.find(text=lambda t: t and 'Категория' in t)
            if category_block:
                parent = category_block.find_parent()
                if parent:
                    # Ищем следующий элемент с категорией
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        product['category'] = next_elem.get_text(strip=True)

            # Наличие товара
            availability_elem = soup.select_one(
                '.stock, .availability, button:contains("В наличии")')
            if availability_elem:
                product['availability'] = availability_elem.get_text(
                    strip=True)

            # Альтернативный поиск наличия
            if not product['availability']:
                avail_text = soup.find(
                    text=lambda t: t and 'наличи' in t.lower())
                if avail_text:
                    product['availability'] = avail_text.strip()

            # Описание товара (вкладка "ОПИСАНИЕ")
            desc_elem = soup.select_one('#tab-description')
            if desc_elem:
                # Убираем лишние пробелы и переносы
                desc_text = desc_elem.get_text(separator=' ', strip=True)
                product['description'] = ' '.join(desc_text.split())

            # Детальные характеристики (вкладка "ХАРАКТЕРИСТИКИ")
            # Парсим таблицу с характеристиками
            details_table = soup.select_one(
                '#tab-additional_information table.woocommerce-product-attributes')
            if details_table:
                characteristics = []
                rows = details_table.select('tr')
                for row in rows:
                    label = row.select_one(
                        '.woocommerce-product-attributes-item__label')
                    value = row.select_one(
                        '.woocommerce-product-attributes-item__value')
                    if label and value:
                        char_name = label.get_text(strip=True).replace(':', '')
                        char_value = value.get_text(strip=True)
                        characteristics.append(f"{char_name}: {char_value}")

                product['details'] = ' | '.join(characteristics)

            # Цена (устанавливаем 0, так как на сайте скрыта)
            product['price'] = '0'

            # Картинки - несколько вариантов селекторов
            # 1. Основное изображение
            main_img = soup.select_one(
                '.woocommerce-product-gallery__image img, .product-image img')
            if main_img:
                img_url = main_img.get('src') or main_img.get('data-src')
                if img_url:
                    product['images'].append(urljoin(self.base_url, img_url))

            # 2. Миниатюры галереи из data-thumb
            gallery_thumbs = soup.select('div[data-thumb]')
            for thumb in gallery_thumbs:
                thumb_url = thumb.get('data-thumb')
                if thumb_url:
                    # Заменяем размер миниатюры на полный размер
                    full_url = thumb_url.replace(
                        '-100x100', '').replace('-150x150', '')
                    full_url = urljoin(self.base_url, full_url)
                    if full_url not in product['images']:
                        product['images'].append(full_url)

            # 3. Все изображения в галерее
            gallery_images = soup.select(
                '.woocommerce-product-gallery__image img, .product-gallery img')
            for img in gallery_images:
                img_url = img.get('src') or img.get(
                    'data-src') or img.get('data-large_image')
                if img_url:
                    full_url = urljoin(self.base_url, img_url)
                    if full_url not in product['images']:
                        product['images'].append(full_url)

            print(f"✅ Спарсен: {product['title'][:50]}...")

        except Exception as e:
            print(f"❌ Ошибка парсинга товара {product_url}: {e}")

        return product

    def get_pagination_urls(self, catalog_url: str) -> List[str]:
        """
        Получение всех URL страниц пагинации
        :param catalog_url: URL каталога
        :return: Список URL всех страниц
        """
        soup = self.fetch_page(catalog_url)
        if not soup:
            return [catalog_url]

        urls = [catalog_url]

        # Ищем все ссылки пагинации
        page_links = soup.select('.page-numbers')
        for link in page_links:
            href = link.get('href')
            if href and href not in urls:
                full_url = urljoin(self.base_url, href)
                urls.append(full_url)

        print(f"📄 Найдено страниц каталога: {len(urls)}")
        return urls

    def parse_catalog(self, catalog_url: str = "https://risbar.kz/catalog/",
                      max_products: int = None,
                      use_pagination: bool = True) -> List[Dict]:
        """
        Парсинг каталога товаров
        :param catalog_url: URL страницы каталога
        :param max_products: Максимальное количество товаров (для теста)
        :param use_pagination: Парсить все страницы каталога
        :return: Список товаров
        """
        # Получаем все страницы каталога
        if use_pagination:
            catalog_pages = self.get_pagination_urls(catalog_url)
        else:
            catalog_pages = [catalog_url]

        count = 0

        for page_url in catalog_pages:
            if max_products and count >= max_products:
                break

            soup = self.fetch_page(page_url)
            if not soup:
                continue

            # Находим все карточки товаров
            # Селектор: .product_wrap содержит ссылку a.db
            product_cards = soup.select('.product a.db')
            print(f"🔍 На странице найдено товаров: {len(product_cards)}")

            for card in product_cards:
                if max_products and count >= max_products:
                    break

                product_url = card.get('href')
                if product_url:
                    full_url = urljoin(self.base_url, product_url)

                    product = self.parse_product(full_url)
                    if product and product.get('title'):
                        self.products.append(product)
                        count += 1
                        print(f"📦 Товаров собрано: {count}")

        return self.products

    def save_to_csv(self, filename: str = 'risbar_products.csv'):
        """Сохранение в CSV"""
        if not self.products:
            print("❌ Нет данных для сохранения")
            return

        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['title', 'article', 'category', 'price', 'availability',
                          'description', 'details', 'images', 'url']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for product in self.products:
                row = product.copy()
                row['images'] = '; '.join(product['images'])
                writer.writerow(row)

        print(f"✅ CSV сохранен: {filename}")

    def save_to_json(self, filename: str = 'risbar_products.json'):
        """Сохранение в JSON"""
        if not self.products:
            print("❌ Нет данных для сохранения")
            return

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)

        print(f"✅ JSON сохранен: {filename}")

    def save_to_xml(self, filename: str = 'risbar_products.xml'):
        """Сохранение в XML"""
        if not self.products:
            print("❌ Нет данных для сохранения")
            return

        root = ET.Element('products')
        root.set('total', str(len(self.products)))

        for product in self.products:
            product_elem = ET.SubElement(root, 'product')

            for key, value in product.items():
                if key == 'images':
                    images_elem = ET.SubElement(product_elem, 'images')
                    for img_url in value:
                        img_elem = ET.SubElement(images_elem, 'image')
                        img_elem.text = img_url
                else:
                    elem = ET.SubElement(product_elem, key)
                    elem.text = str(value)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(filename, encoding='utf-8', xml_declaration=True)

        print(f"✅ XML сохранен: {filename}")

    def save_all_formats(self, base_filename: str = 'risbar_products'):
        """Сохранить во всех форматах одновременно"""
        self.save_to_csv(f'{base_filename}.csv')
        self.save_to_json(f'{base_filename}.json')
        self.save_to_xml(f'{base_filename}.xml')


# Пример использования
if __name__ == "__main__":
    # Создаем парсер
    parser = RisbarParser()

    # Вариант 1: Парсинг только первой страницы (для теста)
    print("=" * 60)
    print("🚀 ЗАПУСК ПАРСЕРА RISBAR.KZ")
    print("=" * 60)

    # Парсим каталог (первые 5 товаров для теста)
    # parser.parse_catalog(
    #     catalog_url="https://risbar.kz/catalog/",
    #     max_products=5,  # Для теста берем только 5 товаров
    #     use_pagination=False  # Не парсим все страницы, только первую
    # )

    # # Сохраняем результаты
    # parser.save_all_formats('risbar_products')

    # Вариант 2: Парсинг всего каталога (раскомментируй для полного парсинга)

    parser.parse_catalog(
        catalog_url="https://risbar.kz/catalog/",
        use_pagination=True  # Парсим ВСЕ страницы каталога
    )

    print("=" * 60)
    print(f"✅ ГОТОВО! Всего спарсено товаров: {len(parser.products)}")
    print("=" * 60)

    parser.save_all_formats('risbar_full_catalog')

    # Вариант 3: Парсинг конкретной категории
    """
    parser.parse_catalog(
        catalog_url="https://risbar.kz/product_cat/naushniki/",  # Замени на нужную категорию
        use_pagination=True
    )
    parser.save_all_formats('risbar_category')
    """
