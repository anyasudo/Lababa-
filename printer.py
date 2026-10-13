from enum import Enum
from typing import Tuple
import json


# Перечисление цветов (числа — стандартные ANSI-коды)
class Color(Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


# Все ANSI-команды в одном месте
class ANSI:
    RESET = "\033[0m"           # сброс цвета
    CLEAR = "\033[2J"           # очистка экрана
    HIDE_CURSOR = "\033[?25l"   # спрятать курсор
    SHOW_CURSOR = "\033[?25h"   # показать курсор

    @staticmethod
    def color(c: Color) -> str:
        # Команда «включить цвет»
        return f"\033[{c.value}m"

    @staticmethod
    def move(x: int, y: int) -> str:
        # Команда «поставить курсор в (x, y)»
        return f"\033[{y};{x}H"


# Класс для вывода текста псевдошрифтом
class Printer:

    # Конструктор: сохраняем настройки и грузим шрифт
    def __init__(self, color: Color, position: Tuple[int, int],
                 symbol: str = "*", font_file: str = "font5.json"):
        if not symbol:
            raise ValueError("symbol не может быть пустым")
        self.color = color
        self.position = position
        self.symbol = symbol
        self.font_file = font_file
        self.font = self._load_font(font_file)
        self._in_context = False

    # Читает JSON-файл со шрифтом
    @staticmethod
    def _load_font(filename: str) -> dict:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise RuntimeError(f"Файл шрифта не найден: {filename}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Ошибка разбора JSON в {filename}: {e}")

    # Высота шрифта (число строк в шаблоне буквы)
    def _font_height(self) -> int:
        return len(next(iter(self.font.values())))

    # Превращает текст в список строк псевдошрифта
    def _render_lines(self, text: str) -> list:
        height = self._font_height()
        blank = self.font.get(" ", [" " * 5] * height)
        lines = []
        for row in range(height):
            parts = []
            for char in text.upper():
                pattern = self.font.get(char, blank)
                line = pattern[row]
                parts.append("".join(self.symbol if c != " " else " " for c in line))
            lines.append(" ".join(parts))
        return lines

    # Рисует текст в точке (x, y) с нужным цветом
    def _draw_at(self, text: str, x: int, y: int) -> None:
        lines = self._render_lines(text)
        color_code = ANSI.color(self.color)
        for i, line in enumerate(lines):
            print(f"{ANSI.move(x, y + i)}{color_code}{line}{ANSI.RESET}",
                  end="", flush=True)
        print(ANSI.move(x, y + len(lines)), end="", flush=True)

    # Публичный метод: напечатать текст и сдвинуть позицию вниз
    def print(self, text: str) -> None:
        x, y = self.position
        self._draw_at(text, x, y)
        self.position = (x, y + self._font_height() + 1)

    # Статический вывод: создать принтер и сразу напечатать
    @classmethod
    def print_static(cls, text: str, color: Color,
                     position: Tuple[int, int] = (1, 1),
                     symbol: str = "*",
                     font_file: str = "font5.json") -> None:
        cls(color, position, symbol, font_file).print(text)

    # Вход в with: спрятать курсор
    def __enter__(self) -> "Printer":
        print(ANSI.HIDE_CURSOR, end="")
        self._in_context = True
        return self

    # Выход из with: показать курсор и сбросить цвет
    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        print(ANSI.SHOW_CURSOR + ANSI.RESET, end="", flush=True)
        self._in_context = False
        return False


# Демонстрация
if __name__ == "__main__":
    import os
    if os.name == "nt":
        os.system("")  # включает ANSI в старых консолях Windows

    print(ANSI.CLEAR, end="", flush=True)

    # 1) статический вывод, шрифт 5, символ '~', голубой
    Printer.print_static("SONYA", Color.CYAN, position=(1, 1),
                         symbol="~", font_file="font5.json")

    # 2) статический вывод, шрифт 7, символ '%', синий
    Printer.print_static("FLP", Color.BLUE, position=(1, 8),
                         symbol="%", font_file="font7.json")

    # 3) with-блок, шрифт 7, символ 'o', красный — два слова подряд
    with Printer(Color.RED, (1, 16), "o", "font7.json") as p:
        p.print("MINE")
        p.print("CRAFT")

    # 4) with-блок, шрифт 5, символ '^', зелёный — в правой колонке
    with Printer(Color.GREEN, (50, 1), "^", "font5.json") as p:
        p.print("CAT")

    # Опустить курсор ниже картинки
    print(ANSI.move(1, 40), end="", flush=True)
