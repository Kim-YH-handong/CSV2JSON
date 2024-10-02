'''
author: Younghun Kim
Functions:
    - Read Preserving csv files and convert them to Deepfake Benchmark JSON format
Note: 
    - This code is only for FaceForensics++ dataset
'''

import csv
import json
import os
import re
# CSV 파일 경로 리스트
csv_file_paths = [
    '/mnt/server19_hard0/younghun/FairnessDataset/ff++/realtrain.csv',
    '/mnt/server19_hard0/younghun/FairnessDataset/ff++/faketrain.csv',
    '/mnt/server19_hard0/younghun/FairnessDataset/ff++/realval.csv',
    '/mnt/server19_hard0/younghun/FairnessDataset/ff++/fakeval.csv',
    '/mnt/server19_hard0/younghun/FairnessDataset/ff++/test.csv',
]

# JSON 파일 경로
dataset_name = 'FF-FH'
json_file_path = f'{dataset_name}.json'

json_data = {dataset_name: {}}

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
            if 'youtube' in data['img_path']:
                df_type = 'FF-real'
            elif 'Deepfakes' in data['img_path']:
                continue
            elif 'Face2Face' in data['img_path']:
                continue
            elif 'FaceSwap' in data['img_path']:
                continue
            elif 'NeuralTextures' in data['img_path']:
                continue
            elif 'FaceShifter' in data['img_path']:
                df_type = 'FF-FH'
            else:
                raise ValueError(f"Unknown spe_label: {data['spe_label']}")
            
            # 프레임 경로 crop_img 추가
            frame_path = data['img_path'].replace("D:", "datasets")
            if 'crop_img' not in data['img_path']:
                path_parts = frame_path.split('/')
                path_parts.insert(2, 'crop_img')
                frame_path = '/'.join(path_parts)
       
            if df_type == 'FF-real':
                video_key = frame_path.split('_')[3]
            else:
                video_key = '_'.join(frame_path.split('_')[3:5])

            # video_key 패턴 확인
            pattern = re.compile(r'^[0-9_]+$')
            if not pattern.match(video_key):
                import pdb; pdb.set_trace()
                raise ValueError(f"Invalid video_key: {video_key}")

            # json 파일에 데이터 추가
            if df_type not in json_data[dataset_name]:
                json_data[dataset_name][df_type] = {}
            if type_data not in json_data[dataset_name][df_type]:
                json_data[dataset_name][df_type][type_data] = {}
            if 'c23' not in json_data[dataset_name][df_type][type_data]:
                json_data[dataset_name][df_type][type_data]['c23'] = {}
            if video_key not in json_data[dataset_name][df_type][type_data]['c23']:
                json_data[dataset_name][df_type][type_data]['c23'][video_key] = {
                    "label": df_type,
                    "frames": []
                }
                        
            # 새로운 비디오인 경우, attributes 추가
            if new_video_key != video_key:
                new_video = True

            # Frame path 추가
            # faketrain, fakeval: img_path, label, ismale, isasian, iswhite, isblack, intersec_label, spe_label
            # realtrain, realval: img_path, label, ismale, isasian, iswhite, isblack, intersec_label
            # test: img_path, label, ismale, isasian, iswhite, isblack, intersec_label
            json_data[dataset_name][df_type][type_data]['c23'][video_key]['frames'].append(frame_path)
            if new_video:
                if 'fake' in csv_file_path:
                    json_data[dataset_name][df_type][type_data]['c23'][video_key]['attributes'] = {
                        'ismale': data['ismale'],
                        'isasian': data['isasian'],
                        'iswhite': data['iswhite'],
                        'isblack': data['isblack'],
                        'intersec_label': data['intersec_label'],
                        'spe_label': data['spe_label']
                    }
                elif 'real' in csv_file_path:
                    json_data[dataset_name][df_type][type_data]['c23'][video_key]['attributes'] = {
                        'ismale': data['ismale'],
                        'isasian': data['isasian'],
                        'iswhite': data['iswhite'],
                        'isblack': data['isblack'],
                        'intersec_label': data['intersec_label']
                    }
                elif 'test' in csv_file_path:
                    json_data[dataset_name][df_type][type_data]['c23'][video_key]['attributes'] = {
                        'ismale': data['ismale'],
                        'isasian': data['isasian'],
                        'iswhite': data['iswhite'],
                        'isblack': data['isblack'],
                        'intersec_label': data['intersec_label']
                    }
                else:
                    raise ValueError(f"Unknown csv_file_path: {csv_file_path}")
                new_video = False
                new_video_key = video_key
# 수정된 JSON 파일 저장
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)

print("새로운 데이터셋이 추가되었습니다.")