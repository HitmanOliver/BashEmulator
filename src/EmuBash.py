from tkinter import *
import argparse
import getpass
import os
import socket
import sys
from tkinter import ttk

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


T_WINDOW_W = 1000
T_WINDOW_H = 800
T_WINDOW_PAD_X = 50
T_WINDOW_PAD_Y = 50
INPUT_PAD_X = 8
INPUT_PAD_Y = 8

VFS_NAME = "my_vfs"


def build_prompt():
    """Собирает приглашение вида user@host:cwd$ ."""
    user_name = getpass.getuser()
    host_name = socket.gethostname()
    if hasattr(os, "getuid"):
        symbol = '#' if os.getuid() == 0 else "$"
    else:
        symbol = "$"
    return f"{user_name}@{host_name}:~{symbol} "


def t_window_init():
    """Создаёт главное окно и виджеты."""
    global t_window, output_text, input_line

    t_window = Tk()
    t_window.title(f"VFS: {VFS_NAME}")
    t_window.geometry(
        f"{T_WINDOW_W}x{T_WINDOW_H}+"
        f"{T_WINDOW_PAD_X}+{T_WINDOW_PAD_Y}"
    )
    t_window.resizable(False, False)

    output_text = Text(
        t_window, bg="black", fg="white",
        insertbackground="white",
        font=("monospace", 11), wrap=WORD,
    )
    output_text.pack(fill=BOTH, expand=True, padx=8, pady=(8, 0))
    output_text.config(state=DISABLED)

    input_frame = ttk.Frame(t_window)
    input_frame.pack(fill=X, side=BOTTOM, padx=8, pady=8)

    ttk.Label(input_frame, text=build_prompt()).pack(side=LEFT)

    input_line = ttk.Entry(input_frame)
    input_line.pack(
        fill=X, side=LEFT, padx=INPUT_PAD_X,
        pady=INPUT_PAD_Y, expand=True,
    )
    input_line.focus()
    t_window.bind("<Return>", enter_handle_process)


def output_write(text: str = ""):
    """Пишет строку в область вывода."""
    output_text.config(state=NORMAL)
    output_text.insert(END, text + "\n")
    output_text.config(state=DISABLED)
    output_text.see(END)


def parse_command(raw_line):
    """Разбивает строку на команду и аргументы по пробелам."""
    parts = raw_line.split()
    if not parts:
        return None, []
    return parts[0], parts[1:]


def cmd_ls(args):
    """Заглушка ls."""
    output_write(f"ls: args={args}")
    return True


def cmd_cd(args):
    """Заглушка cd."""
    output_write(f"cd: args={args}")
    return True


def cmd_exit(args):
    """Закрывает приложение."""
    t_window.quit()
    return True


COMMAND_TABLE = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


def dispatch_command(raw_line):
    """Определяет команду и вызывает её заглушку."""
    command, arguments = parse_command(raw_line)
    if command is None:
        return True
    handler = COMMAND_TABLE.get(command)
    if handler is None:
        output_write(f"{command}: command not found")
        return False
    return handler(arguments)


def enter_handle_process(event):
    """Обработка Enter в поле ввода."""
    raw = input_line.get()
    input_line.delete(0, END)
    output_write(build_prompt() + raw)
    dispatch_command(raw)



config = {"vfs_root": None, "startup_script": None, "config_path": None}
config_sources = {}


def parse_cli_args(argv):
    """Разбор параметров командной строки."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки")
    parser.add_argument("--vfs-root", dest="vfs_root", default=None)
    parser.add_argument("--startup-script", dest="startup_script", default=None)
    parser.add_argument("--config", dest="config_path", default=None)
    return parser.parse_args(argv)


def load_toml(path):
    """Читает TOML. Пустой dict при ошибке."""
    if path is None or tomllib is None:
        return {}
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        print(f"Ошибка чтения конфига: {e}", file=sys.stderr)
        return {}


def resolve_paths(toml_data, config_path):
    """Относительные пути в TOML -> абсолютные от папки конфига."""
    if not config_path or not toml_data:
        return toml_data
    base = os.path.dirname(os.path.abspath(config_path))
    result = dict(toml_data)
    for key in ("vfs_root", "startup_script"):
        value = result.get(key)
        if value and not os.path.isabs(value):
            result[key] = os.path.normpath(os.path.join(base, value))
    return result


def merge_config(cli_args, toml_data):
    """CLI + TOML. Приоритет — TOML."""
    sources = {}

    def pick(key, cli_value):
        if key in toml_data and toml_data[key] is not None:
            sources[key] = "toml"
            return toml_data[key]
        if cli_value is not None:
            sources[key] = "cli"
            return cli_value
        sources[key] = "default"
        return None

    return (
        {
            "vfs_root": pick("vfs_root", cli_args.vfs_root),
            "startup_script": pick("startup_script", cli_args.startup_script),
            "config_path": cli_args.config_path,
        },
        sources,
    )


def print_debug_config():
    """Отладочный вывод параметров."""
    output_write("=== Конфигурация эмулятора ===")
    for key in ("vfs_root", "startup_script", "config_path"):
        value = config.get(key)
        src = config_sources.get(key, "default")
        shown = value if value is not None else "<не задан>"
        output_write(f"  {key}: {shown}  [{src}]")
    output_write("=============================")


def run_startup_script(path):
    """Выполняет стартовый скрипт. Стоп на первой ошибке."""
    if not path:
        return
    output_write(f"--- Стартовый скрипт: {path} ---")
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        output_write(f"Ошибка: стартовый скрипт не найден: {path}")
        return
    except Exception as e:
        output_write(f"Ошибка чтения стартового скрипта: {e}")
        return

    for lineno, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        output_write(build_prompt() + line)
        if not dispatch_command(line):
            output_write(
                f"Ошибка в стартовом скрипте, строка {lineno}: "
                f"скрипт остановлен"
            )
            return
    output_write("--- Стартовый скрипт завершён ---")


def setup_config(argv):
    """Собирает конфигурацию из CLI и TOML."""
    global config, config_sources
    cli_args = parse_cli_args(argv)

    path = cli_args.config_path
    if path is None:
        default = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config.toml"
        )
        if os.path.isfile(default):
            path = default

    toml_data = resolve_paths(load_toml(path), path)
    config, config_sources = merge_config(cli_args, toml_data)
    config["config_path"] = path


def main():
    """Точка входа."""
    setup_config(sys.argv[1:])
    t_window_init()
    print_debug_config()
    t_window.after(100, lambda: run_startup_script(config["startup_script"]))
    t_window.mainloop()


if __name__ == "__main__":
    main()
