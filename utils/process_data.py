# coding=utf8
"""================================
@Author: Mr.Chang
@Date  : 2022/9/9 3:29 下午
==================================="""
import argparse

import pandas as pd
import json


def csv_to_json(csv_path, json_path):
    datas = pd.read_csv(csv_path)
    data_dict = {}
    for zh, en in zip(datas['中文意图'], datas['意图']):
        if zh not in data_dict:
            data_dict[zh] = en

    with open(json_path, 'w', encoding='utf8') as f:
        json.dump(data_dict, f, ensure_ascii=False)
    print(f'Done! file in {json_path}')


def csv_2_sanji_json(csv_path, json_path, field1=None, field2=None):
    datas = pd.read_csv(csv_path)
    data_dict = {}
    for en_intent, sanji in zip(datas[field1], datas[field2]):
        data_dict[en_intent] = sanji

    with open(json_path, 'w', encoding='utf8') as f:
        json.dump(data_dict, f, ensure_ascii=False)
    print(f'Done! file in {json_path}')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--tasks', type=str, default='csv2json', help='csv 转为 json ')
    parser.add_argument('--csv_path', type=str, default=None, help='The path to the CSV file')
    parser.add_argument('--json_path', type=str, default=None, help='The path to saved json file')
    parser.add_argument('--field1', type=str, default='意图intent', help='csv field name ')
    parser.add_argument('--field2', type=str, default='意图三级标签（tag3）', help='csv field name ')
    args = parser.parse_args()
    if args.tasks == 'csv2json':
        csv_to_json(args.csv_path, args.json_path)
    elif args.tasks == 'sanji':
        csv_2_sanji_json(args.csv_path, args.json_path, args.field1, args.field2)
    else:
        print('please input correct task name')
