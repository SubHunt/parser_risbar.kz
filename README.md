# 🛒 Risbar.kz Parser

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

Парсер интернет-магазина [risbar.kz](https://risbar.kz) с поддержкой экспорта в несколько форматов данных.

## 📋 Описание

Парсер автоматически собирает информацию о товарах с сайта risbar.kz и сохраняет данные в удобных форматах (CSV, JSON, XML). Поддерживает пагинацию и может обработать весь каталог товаров.

## ✨ Возможности

- ✅ Парсинг названий товаров
- ✅ Сбор артикулов
- ✅ Извлечение категорий
- ✅ Полное описание товаров
- ✅ Детальные характеристики (таблица спецификаций)
- ✅ Информация о наличии
- ✅ Все изображения товара в полном разрешении
- ✅ Поддержка пагинации (автоматический обход всех страниц)
- ✅ Экспорт в CSV, JSON и XML
- ✅ Обработка ошибок и логирование

## 🔧 Установка

### 1. Клонируйте репозиторий

```bash
git clone git@github.com:SubHunt/risbar-parser.git
cd risbar-parser
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

Или установите вручную:

```bash
pip install requests beautifulsoup4 lxml
```

## 🚀 Использование

### Базовый запуск

Запустите парсер с настройками по умолчанию:

```bash
python parser.py
```

### Примеры использования в коде

#### Парсинг первых N товаров (для теста)

```python
from parser import RisbarParser

parser = RisbarParser()

# Парсим только 10 товаров с первой страницы
parser.parse_catalog(
    catalog_url="https://risbar.kz/catalog/",
    max_products=10,
    use_pagination=False
)

# Сохраняем в CSV
parser.save_to_csv('products.csv')
```

#### Парсинг всего каталога

```python
from parser import RisbarParser

parser = RisbarParser()

# Парсим ВСЕ товары со всех страниц каталога
parser.parse_catalog(
    catalog_url="https://risbar.kz/catalog/",
    use_pagination=True
)

# Сохраняем во всех форматах
parser.save_all_formats('full_catalog')
```

#### Парсинг конкретной категории

```python
from parser import RisbarParser

parser = RisbarParser()

# Парсим конкретную категорию
parser.parse_catalog(
    catalog_url="https://risbar.kz/product_cat/naushniki/",
    use_pagination=True
)

parser.save_to_json('category_products.json')
```

## 📊 Форматы экспорта

### CSV
```csv
title,article,category,price,availability,description,details,images,url
Вентилятор сценический,AF-3,Сценические вентиляторы,0,В наличии,...
```

### JSON
```json
[
  {
    "url": "https://risbar.kz/product/af-3/",
    "title": "Вентилятор сценический, 127 Вт",
    "description": "Компактный универсальный сценический вентилятор...",
    "details": "Производитель: Antari | Наименование: AF-3 | ...",
    "category": "Сценические вентиляторы",
    "article": "AF-3",
    "availability": "В наличии",
    "images": [
      "https://risbar.kz/wp-content/uploads/product/af-3-1.png",
      "https://risbar.kz/wp-content/uploads/product/af-3-2.jpg"
    ],
    "price": "0"
  }
]
```

### XML
```xml
<?xml version='1.0' encoding='utf-8'?>
<products total="100">
  <product>
    <url>https://risbar.kz/product/af-3/</url>
    <title>Вентилятор сценический, 127 Вт</title>
    <description>...</description>
    <images>
      <image>https://risbar.kz/wp-content/uploads/product/af-3-1.png</image>
      <image>https://risbar.kz/wp-content/uploads/product/af-3-2.jpg</image>
    </images>
    ...
  </product>
</products>
```

## 🎯 Собираемые данные

| Поле | Описание |
|------|----------|
| `title` | Название товара |
| `article` | Артикул (например, AF-3) |
| `category` | Категория товара |
| `price` | Цена (по умолчанию "0", так как скрыта на сайте) |
| `availability` | Наличие товара ("В наличии" / "Под заказ" и т.д.) |
| `description` | Полное описание из вкладки "ОПИСАНИЕ" |
| `details` | Технические характеристики из таблицы |
| `images` | Массив ссылок на изображения товара |
| `url` | Прямая ссылка на товар |

## ⚙️ API класса RisbarParser

### Инициализация

```python
parser = RisbarParser(base_url="https://risbar.kz")
```

### Основные методы

#### `parse_catalog(catalog_url, max_products=None, use_pagination=True)`
Парсит каталог товаров.

**Параметры:**
- `catalog_url` (str) - URL страницы каталога
- `max_products` (int, optional) - Максимальное количество товаров для парсинга
- `use_pagination` (bool) - Включить обход всех страниц пагинации

**Возвращает:** `List[Dict]` - список товаров

#### `save_to_csv(filename='risbar_products.csv')`
Сохраняет данные в CSV файл.

#### `save_to_json(filename='risbar_products.json')`
Сохраняет данные в JSON файл.

#### `save_to_xml(filename='risbar_products.xml')`
Сохраняет данные в XML файл.

#### `save_all_formats(base_filename='risbar_products')`
Сохраняет данные во всех трех форматах одновременно.

## 🛡️ Обработка ошибок

Парсер автоматически обрабатывает:
- ❌ Ошибки загрузки страниц (таймауты, 404, 500 и т.д.)
- ❌ Отсутствующие элементы на странице
- ❌ Невалидные URL
- ❌ Проблемы с кодировкой

Все ошибки логируются в консоль с подробным описанием.

## ⚡ Производительность

- Пауза между запросами: 1 секунда (по умолчанию закомментирована)
- Таймаут запроса: 15 секунд
- Обработка ~5-10 товаров в минуту
- Полный каталог (5700+ товаров): ~10-20 часов

## 📝 Требования

- Python 3.7+
- requests >= 2.28.0
- beautifulsoup4 >= 4.11.0
- lxml >= 4.9.0

## 🤝 Вклад в проект

Приветствуются любые улучшения! Создавайте Issues и Pull Requests.

### Как внести свой вклад:

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/AmazingFeature`)
3. Закоммитьте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Запушьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## ⚠️ Disclaimer

Этот парсер создан исключительно в образовательных целях. Перед использованием убедитесь, что парсинг не нарушает правила использования сайта risbar.kz. Используйте парсер ответственно и не создавайте чрезмерную нагрузку на сервер.

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 👤 Автор

**SubHunt**

- GitHub: [@SubHunt](https://github.com/SubHunt)

## 🌟 Поддержка проекта

Если проект был вам полезен, поставьте ⭐ на GitHub!

---

**Создано с ❤️ для автоматизации сбора данных**