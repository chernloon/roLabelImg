import numpy as np
import json
import argparse
import os

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser( \
    'Insert the midv passport mrz text into the annotated json files')
    
    parser.add_argument('--root',required=True,help='Root directory of the passport dataset folder, eg c:/wiseai/dataset/passport/passport-mrz-ocr')
    parser.add_argument('--source',default='midv-500',choices=['midv-500','midv-2019'],help='midv-500 or midv-2019 dataset')
    parser.add_argument('--img_format',default='jpg',choices=['jpg','tif'])
    
    args = parser.parse_args()
    
    
    root_dir = args.root
    if args.source == 'midv-500':
        source_type = 'midv-500'
    elif args.source == 'midv-2019':
        source_type = 'midv-2019'
    else:
        print('\n[ERROR] Wrong source type: {}'.format(args.source))
        exit()
    
    if not os.path.isdir(root_dir):
        print('Root directory doesnt exist.\n')
        exit()
        
        
    for dir1 in os.listdir(os.path.join(root_dir,source_type)):
    
        if os.path.isdir(os.path.join(root_dir,source_type,dir1)):

            json_path = os.path.join(root_dir, source_type, dir1, 'annotation_json')
            
            # extract mrz text from midv original json
            main_json_filename = dir1 + '.json'
            if not os.path.isfile(os.path.join(root_dir,source_type,dir1,main_json_filename)):
                print('cannot load {}'.format(main_json_filename))
                
            with open(os.path.join(root_dir,source_type,dir1,main_json_filename), encoding="cp866") as f:
                main_j = json.load(f)
            
            text = ''
            for key in main_j.keys():
                if ('value' in main_j[key].keys()):
      
                    if (len(main_j[key]['value']) == 44):
                        text += '\n' + main_j[key]['value']
            text = text[1:]
            
            for file1 in os.listdir(json_path):
                try:
                    with open(os.path.join(json_path,file1)) as f:
                        j = json.load(f)
                except Exception as e:
                    print('\n[ERROR] {}: {}'.format(file1,e))
                    continue
                    
                if 'rotated_objects' in j:
                    if len(j['rotated_objects']) > 1:
                        print('[ERROR] More than 1 mrz zone label in json')
                        continue
                    j['rotated_objects'][0]['text'] = text

                    with open(os.path.join(json_path,file1), 'w') as f:
                        json.dump(j, f)
    
    