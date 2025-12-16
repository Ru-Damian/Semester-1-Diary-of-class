import os
import sys
import inspect
from typing import Any
import importlib
import re

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
FUNCTIONS_DIR = os.path.join(PROJECT_ROOT, "Functions")
files = ["main", "data_processing", "info_extract", "input_check", "student_operations"]
print("Доступные файлы:", files)
target_file = input("Введите названия файла для создания документации: ")
if target_file == "main":
    sys.path.insert(0, PROJECT_ROOT)
else:
    sys.path.insert(0, FUNCTIONS_DIR)

try:
    module = importlib.import_module(target_file)
except Exception:
    if target_file not in files:
        print(f"{target_file} нет в файлах")
    sys.exit(1)

def safe_annotation_str(ann: Any) -> str:
    try:
        if ann is inspect._empty:
            return "any"
        return getattr(ann, "__name__", str(ann))
    except Exception:
        return "any"

def format_params(func) -> str:
    sig = inspect.signature(func)
    lines = []
    for name, param in sig.parameters.items():
        ann_str = safe_annotation_str(param.annotation)
        if param.default is inspect._empty:
            default_str = ""
        else:
            default_str = f" = {param.default!r}"
        lines.append(f"{name}: {ann_str}{default_str}")
    return "<br>".join(lines)

def format_docstring(doc: str) -> str:
    if not doc:
        return ""
    doc = doc.strip()
    lines = doc.split('\n')
    formatted_lines = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        if line.startswith(':param') or line.startswith(':type'):
            if i > 0 and formatted_lines:
                formatted_lines.append(f"<br>{line}")
            else:
                formatted_lines.append(line)
        else:
            if formatted_lines and not formatted_lines[-1].endswith('<br>'):
                if not (formatted_lines[-1].startswith(':param') or 
                    formatted_lines[-1].startswith(':type') or
                    formatted_lines[-1].endswith('.')):
                    formatted_lines.append(" " + line)
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
    return "".join(formatted_lines)

def gen_md_for_module(mod):
    module_name = mod.__name__
    lines = []
    lines.append(f"## Функции модуля {module_name}")
    lines.append("")
    lines.append("| Функция | Описание |")
    lines.append("|---------|----------|")
    for name, obj in inspect.getmembers(mod, inspect.isfunction):
        if obj.__module__ != mod.__name__:
            continue
        doc = inspect.getdoc(obj) or ""
        doc = format_docstring(doc)
        params_str = format_params(obj)
        if doc and params_str:
            if ':param' in doc or ':type' in doc:
                final_doc = doc
            else:
                final_doc = f"{doc}<br>{params_str}"
        elif params_str:
            final_doc = params_str
        else:
            final_doc = doc
        lines.append(f"| {name}() | {final_doc} |")
    return "\n".join(lines), module_name


if __name__ == "__main__":
    md, module_name = gen_md_for_module(module)
    doc_dir = os.path.join(PROJECT_ROOT, "Documentation")
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir, exist_ok=True)
    out_path = os.path.join(doc_dir, f"{module_name}_autodoc.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)