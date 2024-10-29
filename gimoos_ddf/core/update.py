#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import psycopg2
import zipfile
import requests
import json
import aiohttp
import asyncio
from requests_toolbelt import MultipartEncoder
from datetime import datetime


# 指定模块所在的目录
module_dir = 'hcc_server_code/driver_xml_code'


def xml_to_dict(xml: str, default: any = ...) -> dict:
    """将xml字符串转换为字典"""
    from xml.etree.ElementTree import Element, fromstring

    def wrapper(element: Element):
        result = {}
        for child in element:
            if len(child) == 0:
                if not child.text:
                    if default is not ...:
                        value = default
                        result[child.tag] = value
                    continue

                try:
                    value = int(child.text)
                except ValueError:
                    try:
                        value = float(child.text)
                    except ValueError:
                        value = child.text

                if isinstance(value, str) and value.lower() in ['true', 'false']:
                        value = value.lower() == 'true'

                result[child.tag] = value
            else:
                result[child.tag] = wrapper(child)
        return result

    return wrapper(fromstring(xml))


def is_need_update(file_path: str) -> bool:
    """检查文件是否需要更新"""
    update_record_path = 'temp/update_record.json'
    update_mtime = os.path.getmtime(os.path.join(module_dir, file_path))
    update_record = {}

    # 读取文件修改记录
    if not os.path.exists(update_record_path):
        with open(update_record_path, 'w', encoding='utf-8') as file:
            file.write('{}')

    with open(update_record_path, 'r', encoding='utf-8') as file:
        update_record = json.load(file)

    if mtime := update_record.get(file_path, None):
        if mtime == update_mtime:
            return False

    update_record[file_path] = update_mtime
    with open(update_record_path, 'w', encoding='utf-8') as file:
        json.dump(update_record, file, indent=4, ensure_ascii=False)

    return True


def get_data() -> list[dict[str, str]]:
    # 用于保存提取的 XML 和 DEVICE_ID 内容
    extracted_data = []

    # 遍历目录中的所有文件
    for filename in os.listdir(module_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            if not is_need_update(filename):
                continue

            file_path = os.path.join(module_dir, filename)

            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

                # 检查文件的第一行
                if lines and lines[0].strip() == 'from .public_include import *':
                    # 提取 XML 变量
                    xml_variables = {}
                    inside_xml = False
                    xml_name = None
                    xml_content = []

                    for line in lines:
                        # 检查是否是 XML 变量的定义
                        xml_match = re.match(r'^\s*(\w+)\s*=\s*(""")', line)
                        if xml_match:
                            xml_name = xml_match.group(1)
                            inside_xml = True
                            xml_content.append(line)
                        elif inside_xml:
                            xml_content.append(line)

                            # 检查是否结束文档字符串
                            if line.strip().endswith('"""'):
                                xml_variables[xml_name] = ''.join(xml_content)
                                inside_xml = False
                                xml_content = []

                    # 提取 DEVICE_ID 及后续代码
                    device_id_code = []
                    for line in lines:
                        if 'DEVICE_ID = C4.GetDeviceID()' in line:
                            device_id_code.append(line)
                            # 将后面的所有代码添加到设备 ID 代码中
                            device_id_code.extend(lines[lines.index(line) + 1:])
                            break

                    xml = xml_variables[xml_name]
                    xml = xml[xml.index('"""') + 3:xml.rindex('"""')]
                    # 解析 XML 内容
                    xml_dict = xml_to_dict(xml)

                    # 保存提取结果
                    extracted_data.append({
                        'filename': filename[:-3],
                        'driver_name': xml_dict.get('name', ''),
                        'driver_xml': xml,
                        'driver_lua': ''.join(device_id_code),
                        'model': xml_dict.get('model', ''),
                        'manufacturer': xml_dict.get('manufacturer', ''),
                        'controlmethod': str(set(xml_dict.get('controlmethod', '').split(','))).replace("'", ""),
                        'alias': str(set(xml_dict.get('alias', '').split(','))).replace("'", ""),
                    })
    return extracted_data


def update_with_sql(ip):
    extracted_data = get_data()

    # PostgreSQL 数据库连接配置
    db_config = {
        'dbname': 'hcc_server',       # 替换为您的数据库名
        'user':   'hcc_server',       # 替换为您的用户名
        'password': 'hcc_server@123', # 替换为您的密码
        'host': ip,                   # 如果在本地，通常是 'localhost'
        'port': '5432'                # 默认是 5432
    }

    conn: psycopg2.extensions.connection = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    cursor.executemany('''
            UPDATE driver_list SET (driver_xml, driver_lua, model, manufacturer, controlmethod, alias) = (%s, %s, %s, %s, %s, %s) WHERE starts_with(driver_file, %s)
        ''',
        [(data['driver_xml'], data['driver_lua'], data['model'], data['manufacturer'], data['controlmethod'], data['alias'], data['filename'] + '.') for data in extracted_data],
    )

    conn.commit()
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}] 更新成功 {cursor.rowcount}/{len(extracted_data)}')
    cursor.close()
    conn.close()


async def login(url):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={
            "project": "items",
            "type": "im-function",
            "id": "login",
            "param": {
                "data": {
                    "username": "root",
                    "password": "123456",
                },
            },
        }) as response:
            if response.status == 200:
                token = (await response.json()).get('data', {}).get('token', None)
                print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}] 登录成功，token：{token}')
                return token
            else:
                print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}] 登录失败，状态码：{response.status_code}')
                return None


async def upload_files(url: str, token: str, data: dict):
    async with aiohttp.ClientSession() as session:
        filename = data['filename']
        driver_xml = data['driver_xml']
        driver_lua = data['driver_lua']

        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}] 开始上传 "{filename}.zip"')

        # 构建 zip 文件
        with zipfile.ZipFile(f'temp/{filename}.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f'driver.xml', driver_xml)
            zip_file.writestr(f'driver.py', driver_lua)

        # 上传 zip 文件
        with open(f'temp/{filename}.zip', 'rb') as file:
            data = aiohttp.FormData()
            data.add_field('param', '{"project":"items","type":"im-function","id":"upload_driver","param":{}}')
            data.add_field('file', file, filename=f'{filename}.zip', content_type='application/zip')

            headers = {
                'Authorization': f'Basic {token}',
            }
            async with session.post(url, data=data, headers=headers) as response:
                if response.status != 200:
                    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}] 上传 "{filename}.zip" 失败，状态码：{response.status}')


async def update_with_fetch(ip, port=8000):
    extracted_data = get_data()
    if not extracted_data:
        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}] 没有需要更新的驱动程序')
        return

    if not os.path.exists('temp'):
        os.mkdir('temp')

    url = f'http://{ip}:{port}/interface/db/selector'

    if not (token := await login(url)):
        return

    tasks = [asyncio.create_task(upload_files(url, token, data)) for data in extracted_data]

    await asyncio.gather(*tasks)
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}] 全部上传完成')


if __name__ == '__main__':
    import sys

    match sys.argv[1]:
        case '-s':
            update_with_sql(sys.argv[2])
        case '-f':
            loop = asyncio.get_event_loop()
            loop.run_until_complete(update_with_fetch(sys.argv[2]))
