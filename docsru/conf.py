import os
import sys

# Добавляем путь к вашему проекту, чтобы Sphinx мог найти модули
sys.path.insert(0, os.path.abspath('..'))

# Расширения Sphinx
extensions = [
    'sphinx.ext.autodoc',      # Автоматическое документирование из докстрингов
    'sphinx.ext.viewcode',     # Показывать исходный код
    'sphinx.ext.napoleon',     # Поддержка Google-style докстрингов
    'sphinx.ext.todo',         # Поддержка TODO-заметок
]

# Тема оформления
html_theme = 'sphinx_rtd_theme'

# Настройки для autodoc
autodoc_member_order = 'groupwise'  # Группировать методы и атрибуты
autodoc_default_flags = ['members', 'undoc-members', 'show-inheritance']
autoclass_content = 'both'  # Показывать и класс и __init__ докстринги

# Язык
language = 'ru'

# Название проекта
project = 'Financial Tracker'
copyright = '2025, Литвиненко Артем'
author = 'Литвиненко Артем'

# Версия
version = '1.0'
release = '1.0.0'