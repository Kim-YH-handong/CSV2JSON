'''
author: Younghun Kim
Functions:
    - Read Preserving csv files and convert them to Deepfake Benchmark JSON format
Note: 
    - This code is only for DeepFakeDetection dataset
'''

import csv
import json
import os
import re
# CSV 파일 경로 리스트
csv_file_paths = [
    '/mnt/server19_hard0/younghun/FairnessDataset/celebdf/train.csv',
    '/mnt/server19_hard0/younghun/FairnessDataset/celebdf/val.csv',
    '/mnt/server19_hard0/younghun/FairnessDataset/celebdf/test.csv',
]

# JSON 파일 경로
dataset_name = 'Celeb-DF-v2'
json_file_path = f'{dataset_name}.json'

json_data = {dataset_name: {}}

# File path pattern to extract video key
real_pattern = re.compile(r'_YouTube-real_(\d+)_')
real_pattern2 = re.compile(r'_(id\d+_\d+)_')
fake_pattern = re.compile(r'_(id\d+_id\d+_\d+)_')

# 모든 CSV 파일을 읽어와서 dictionary 형태로 변환
for csv_file_path in csv_file_paths:
    new_video = True
    new_video_key = None
    with open(csv_file_path, mode='r', encoding='utf-8') as file:  # Open csv file
        csv_reader = csv.DictReader(file)
        for data in csv_reader:
            # 파일 경로로부터 데이터 타입 추출
            if 'train' in csv_file_path:
                type_data = 'train'
            elif 'val' in csv_file_path:
                type_data = 'val'
            elif 'test' in csv_file_path:
                type_data = 'test'
            else:
                raise ValueError(f"Unknown csv_file_path: {csv_file_path}")
            
            # 파일 경로로부터 데이터 레이블 추출
            if data['label'] == '1':
                df_type = 'CelebDFv2_fake'
            elif data['label'] == '0':
                df_type = 'CelebDFv2_real'
            else:
                raise ValueError(f"Unknown spe_label: {data['label']}")
            
            # 프레임 경로 crop_img 추가
            frame_path = "datasets" + data['img_path']
            if 'crop_img' not in data['img_path']:
                raise ValueError(f"Invalid img_path: {data['img_path']}")
       
            if df_type == 'CelebDFv2_real':
                match = real_pattern.search(frame_path)
                if match:
                    video_key = match.group(1)
                else:
                    match = real_pattern2.search(frame_path)
                    if match:
                        video_key = match.group(1)
                    else:
                        import pdb; pdb.set_trace()
                        raise ValueError(f"Invalid video_key: {frame_path}")
            elif df_type == 'CelebDFv2_fake':
                match = fake_pattern.search(frame_path)
                if match:
                    video_key = match.group(1)
                else:
                    raise ValueError(f"Invalid video_key: {frame_path}")
              
            # json 파일에 데이터 추가
            if df_type not in json_data[dataset_name]:
                json_data[dataset_name][df_type] = {}
            if type_data not in json_data[dataset_name][df_type]:
                json_data[dataset_name][df_type][type_data] = {}
            # if 'c23' not in json_data[dataset_name][df_type][type_data]:
            #     json_data[dataset_name][df_type][type_data]['c23'] = {}
            if video_key not in json_data[dataset_name][df_type][type_data]:
                json_data[dataset_name][df_type][type_data][video_key] = {
                    "label": df_type,
                    "frames": []
                }
            
            # 새로운 비디오인 경우, attributes 추가
            if new_video_key != video_key:
                new_video = True
            # train, val, test: img_path, label, ismale, iswhite, isblack, intersec_label
            json_data[dataset_name][df_type][type_data][video_key]['frames'].append(frame_path)
            if new_video:
                json_data[dataset_name][df_type][type_data][video_key]['attributes'] = {
                    'ismale': data['ismale'],
                    'iswhite': data['iswhite'],
                    'isblack': data['isblack'],
                    'intersec_label': data['intersec_label'],
                }
# 수정된 JSON 파일 저장
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)

print("새로운 데이터셋이 추가되었습니다.")