#!/usr/bin/env python3
"""
Simple File Manager in Python
Простой файловый менеджер на Python
"""

import os
import shutil
import sys


def list_files(path="."):
    """List all files and directories in the given path."""
    try:
        items = os.listdir(path)
        print(f"\nСодержимое директории: {os.path.abspath(path)}\n")
        print("-" * 50)
        for item in sorted(items):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                print(f"[DIR]  {item}/")
            else:
                size = os.path.getsize(full_path)
                print(f"[FILE] {item} ({size} bytes)")
        print("-" * 50)
        print(f"Всего элементов: {len(items)}")
    except FileNotFoundError:
        print(f"Ошибка: Директория '{path}' не найдена")
    except PermissionError:
        print(f"Ошибка: Нет доступа к директории '{path}'")


def create_file(filename, content=""):
    """Create a new file with optional content."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Файл '{filename}' успешно создан")
    except PermissionError:
        print(f"Ошибка: Нет прав для создания файла '{filename}'")
    except OSError as e:
        print(f"Ошибка при создании файла: {e}")


def read_file(filename):
    """Read and display file content."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"\nСодержимое файла '{filename}':\n")
        print("-" * 50)
        print(content)
        print("-" * 50)
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден")
    except PermissionError:
        print(f"Ошибка: Нет доступа к файлу '{filename}'")
    except UnicodeDecodeError:
        print(f"Ошибка: Невозможно прочитать файл '{filename}' как текст")


def delete_file(filename):
    """Delete a file."""
    try:
        os.remove(filename)
        print(f"Файл '{filename}' успешно удален")
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден")
    except PermissionError:
        print(f"Ошибка: Нет прав для удаления файла '{filename}'")
    except IsADirectoryError:
        print(f"Ошибка: '{filename}' является директорией. Используйте rmdir.")


def create_directory(dirname):
    """Create a new directory."""
    try:
        if os.path.exists(dirname):
            print(f"Директория '{dirname}' уже существует")
        else:
            os.makedirs(dirname)
            print(f"Директория '{dirname}' успешно создана")
    except PermissionError:
        print(f"Ошибка: Нет прав для создания директории '{dirname}'")
    except OSError as e:
        print(f"Ошибка при создании директории: {e}")


def remove_directory(dirname):
    """Remove a directory."""
    try:
        if os.listdir(dirname):
            confirm = input(f"Директория '{dirname}' не пуста. Удалить? (y/n): ")
            if confirm.lower() != 'y':
                print("Операция отменена")
                return
        shutil.rmtree(dirname)
        print(f"Директория '{dirname}' успешно удалена")
    except FileNotFoundError:
        print(f"Ошибка: Директория '{dirname}' не найдена")
    except PermissionError:
        print(f"Ошибка: Нет прав для удаления директории '{dirname}'")
    except OSError as e:
        print(f"Ошибка при удалении директории: {e}")


def copy_file(source, destination):
    """Copy a file to a new location."""
    try:
        shutil.copy2(source, destination)
        print(f"Файл '{source}' скопирован в '{destination}'")
    except FileNotFoundError:
        print(f"Ошибка: Файл '{source}' не найден")
    except PermissionError:
        print(f"Ошибка: Нет прав для копирования")
    except shutil.SameFileError:
        print("Ошибка: Источник и назначение совпадают")


def move_file(source, destination):
    """Move a file to a new location."""
    try:
        shutil.move(source, destination)
        print(f"Файл '{source}' перемещен в '{destination}'")
    except FileNotFoundError:
        print(f"Ошибка: Файл '{source}' не найден")
    except PermissionError:
        print(f"Ошибка: Нет прав для перемещения")
    except shutil.Error as e:
        print(f"Ошибка при перемещении: {e}")


def show_help():
    """Display help message."""
    print("""
Файловый менеджер - Команды:
============================
  ls [путь]           - Показать содержимое директории
  cd <путь>           - Перейти в директорию
  pwd                 - Показать текущую директорию
  cat <файл>          - Показать содержимое файла
  touch <файл>        - Создать пустой файл
  rm <файл>           - Удалить файл
  mkdir <директория>  - Создать директорию
  rmdir <директория>  - Удалить директорию
  cp <src> <dst>      - Копировать файл
  mv <src> <dst>      - Переместить файл
  help                - Показать эту справку
  exit                - Выход
    """)


def main():
    """Main function - interactive file manager."""
    print("=" * 50)
    print("Добро пожаловать в Файловый Менеджер!")
    print("Введите 'help' для списка команд")
    print("=" * 50)

    while True:
        try:
            current_dir = os.getcwd()
            command = input(f"\n{current_dir}> ").strip()

            if not command:
                continue

            parts = command.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "exit" or cmd == "quit":
                print("До свидания!")
                break
            elif cmd == "help":
                show_help()
            elif cmd == "ls":
                path = args[0] if args else "."
                list_files(path)
            elif cmd == "cd":
                if args:
                    try:
                        os.chdir(args[0])
                    except FileNotFoundError:
                        print(f"Ошибка: Директория '{args[0]}' не найдена")
                    except PermissionError:
                        print(f"Ошибка: Нет доступа к директории '{args[0]}'")
                else:
                    print("Использование: cd <путь>")
            elif cmd == "pwd":
                print(os.getcwd())
            elif cmd == "cat":
                if args:
                    read_file(args[0])
                else:
                    print("Использование: cat <файл>")
            elif cmd == "touch":
                if args:
                    create_file(args[0])
                else:
                    print("Использование: touch <файл>")
            elif cmd == "rm":
                if args:
                    delete_file(args[0])
                else:
                    print("Использование: rm <файл>")
            elif cmd == "mkdir":
                if args:
                    create_directory(args[0])
                else:
                    print("Использование: mkdir <директория>")
            elif cmd == "rmdir":
                if args:
                    remove_directory(args[0])
                else:
                    print("Использование: rmdir <директория>")
            elif cmd == "cp":
                if len(args) >= 2:
                    copy_file(args[0], args[1])
                else:
                    print("Использование: cp <источник> <назначение>")
            elif cmd == "mv":
                if len(args) >= 2:
                    move_file(args[0], args[1])
                else:
                    print("Использование: mv <источник> <назначение>")
            else:
                print(f"Неизвестная команда: {cmd}")
                print("Введите 'help' для списка команд")

        except KeyboardInterrupt:
            print("\nДо свидания!")
            break
        except EOFError:
            print("\nДо свидания!")
            break


if __name__ == "__main__":
    main()
