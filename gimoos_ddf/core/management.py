#!/usr/bin/env python
# -*- coding: utf-8 -*-

def execute_from_command_line():
    import argparse

    from gimoos_ddf import __version__

    parser = argparse.ArgumentParser(prog='gimoos_ddf', description='Gimoos 驱动开发脚手架', add_help=False)
    subparsers = parser.add_subparsers(
        title='可选命令',
        dest='cmd',
    )

    parser.add_argument('-h', '--help', help='显示帮助信息并退出', action='help')
    parser.add_argument('-v', '--version', help='显示版本信息并退出', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--path', help='工作路径', default='.')

    parser_create = subparsers.add_parser('create', help='创建驱动')
    parser_create.add_argument('name', nargs='+', help='驱动名称')

    parser_update = subparsers.add_parser('update', help='更新驱动')

    args = parser.parse_args()

    print(args)

    match args.cmd:
        case 'create':
            import os

            for name in args.name:
                path = os.path.join(args.path, name)

                # 创建文件夹
                if not os.path.exists(path):
                    os.makedirs(path)

                # 创建文件
                with open(os.path.join(path, 'driver.py'), 'w') as f:
                    f.write('')
                with open(os.path.join(path, 'driver.xml'), 'w') as f:
                    f.write('')
                print(f'创建驱动文件 "{name}" 成功')
        case 'update':
            from pathlib import Path

            path = Path(args.path)
            print(f'更新驱动 {path.absolute()}')
