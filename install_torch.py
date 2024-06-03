import os
import subprocess
import sys

# Определение типа процессора
processor = subprocess.run(['python', '-c', "import platform; print(platform.machine())"], capture_output=True, text=True).stdout.strip()

# Определение типа операционной системы
os_name = os.name

# Определение версии Python
python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

# Формирование команды для установки torch
if os_name == 'nt':  # Windows
    if processor == 'AMD64':
        torch_command = f"pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
    else:
        raise ValueError(f"Unsupported processor type: {processor}")
elif os_name == 'posix':  # Linux or macOS
    if processor == 'x86_64':
        torch_command = f"pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
    elif processor == 'aarch64':
        torch_command = f"pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
    else:
        raise ValueError(f"Unsupported processor type: {processor}")
else:
    raise ValueError(f"Unsupported operating system: {os_name}")

# Установка torch
subprocess.run(torch_command, shell=True)