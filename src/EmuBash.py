from tkinter import *
import getpass
import os
import socket
from tkinter import ttk


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
    global t_window, output_text, input_line, prefix_label

    t_window = Tk()
    t_window.title(f"VFS: {VFS_NAME}")
    t_window.geometry(
        f"{T_WINDOW_W}x{T_WINDOW_H}+"
        f"{T_WINDOW_PAD_X}+{T_WINDOW_PAD_Y}"
    )
    t_window.resizable(False, False)

    output_text = Text(
        t_window,
        bg="black",
        fg="white",
        insertbackground="white",
        font=("monospace", 11),
        wrap=WORD,
    )
    output_text.pack(fill=BOTH, expand=True, padx=8, pady=(8, 0))
    output_text.config(state=DISABLED)

    input_frame = ttk.Frame(t_window)
    input_frame.pack(fill=X, side=BOTTOM, padx=8, pady=8)

    prefix_label = ttk.Label(input_frame, text=build_prompt())
    prefix_label.pack(side=LEFT)

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
    """Заглушка ls: выводит имя и аргументы."""
    output_write(f"ls: args={args}")


def cmd_cd(args):
    """Заглушка cd: выводит имя и аргументы."""
    output_write(f"cd: args={args}")


def cmd_exit(args):
    """Закрывает приложение."""
    t_window.quit()


COMMAND_TABLE = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


def dispatch_command(raw_line):
    """Определяет команду и вызывает её заглушку."""
    command, arguments = parse_command(raw_line)
    if command is None:
        return
    handler = COMMAND_TABLE.get(command)
    if handler is None:
        output_write(f"{command}: command not found")
        return
    handler(arguments)


def enter_handle_process(event):
    """Обработка нажатия Enter в поле ввода."""
    raw = input_line.get()
    input_line.delete(0, END)
    output_write(build_prompt() + raw)
    dispatch_command(raw)


def main():
    """Точка входа."""
    t_window_init()
    t_window.mainloop()


if __name__ == "__main__":
    main()
