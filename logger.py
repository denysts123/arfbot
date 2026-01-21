import sys
import inspect

import colorama

colorama.init(autoreset=True)


def get_stack() -> str:
    caller = inspect.stack()[2]
    module = inspect.getmodule(caller.frame)
    module_name = module.__name__ if module else "__main__"
    func_name = caller.function

    return f"{module_name}.{func_name}"


def critical(message: str):
    source = get_stack()
    print(colorama.Fore.RED + colorama.Style.BRIGHT + f"[CRITICAL] [{source}] {message}")
    input(colorama.Fore.CYAN + "Press enter to exit...")
    sys.exit(1)

def error(message: str):
    source = get_stack()
    print(colorama.Fore.RED + f"[ERROR] [{source}] {message}")

def warning(message: str):
    source = get_stack()
    print(colorama.Fore.YELLOW + f"[WARNING] [{source}] {message}")

def info(message: str):
    source = get_stack()
    print(colorama.Fore.GREEN + f"[INFO] [{source}] {message}")

def debug(message: str):
    source = get_stack()
    print(colorama.Fore.BLUE + f"[DEBUG] [{source}] {message}")
