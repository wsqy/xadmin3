#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo_app.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # 将上上级目录加入 Python 路径, xadmin本地开发使用
    import pathlib
    manage_path = pathlib.Path(__file__).resolve()
    upper_dir = manage_path.parent.parent # 根据需要调整 .parent 数量

    if str(upper_dir) not in sys.path:
        sys.path.insert(0, str(upper_dir))

    main()
