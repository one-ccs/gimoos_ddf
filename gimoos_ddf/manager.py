#!/usr/bin/env python
# -*- coding: utf-8 -*-


def main():
    import argparse

    parser = argparse.ArgumentParser(prog='gimoos_ddf', description='Gimoos DDF Manager')
    subparsers = parser.add_subparsers(
        title='可选命令',
        dest='cmd',
    )

    parser.add_argument('-p', '--work-path', help='工作路径', default='.')

    parser_create = subparsers.add_parser('create', help='创建驱动')
    parser_create.add_argument('name', nargs='+', help='驱动名称')

    args = parser.parse_args()

    print(f'args: {args}')
    match args.cmd:
        case 'create':
            import os

            for name in args.name:
                work_path = os.path.join(args.work_path, name)

                # 创建文件夹
                if not os.path.exists(work_path):
                    os.makedirs(work_path)

                # 创建文件
                with open(os.path.join(work_path, 'driver.py'), 'w') as f:
                    f.write('')
                with open(os.path.join(work_path, 'driver.xml'), 'w') as f:
                    f.write('')
                print(f'创建驱动文件 "{name}" 成功')


if __name__ == '__main__':
    main()
