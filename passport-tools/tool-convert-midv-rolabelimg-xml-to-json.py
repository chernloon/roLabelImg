import cv2
import os
import xml.etree.ElementTree as ET
import json
import argparse
from datetime import date
import numpy as np

def get_rotated_bounding_box(cx,cy,w,h,angle):
    rot_mat = cv2.getRotationMatrix2D((cx,cy),-angle*180*7/22,1.0)
    coord_mat = np.array([[cx-int(w/2),cy-int(h/2)],
             [cx+int(w/2),cy-int(h/2)],
             [cx+int(w/2),cy+int(h/2)],
             [cx-int(w/2),cy+int(h/2)]])

    new_coord_mat = np.zeros(coord_mat.shape,coord_mat.dtype)
    for i,coord in enumerate(coord_mat):
        c = np.matmul(rot_mat,np.array([[coord[0]],[coord[1]],[1]]))
        new_coord_mat[i][0] = c[0]
        new_coord_mat[i][1] = c[1]
    return new_coord_mat

if __name__ == "__main__":

    parser = argparse.ArgumentParser( \
    'Read all xml files generated by roLabelImg from a directory and generate the standardized json files')
    
    parser.add_argument('--root',required=True,help='Root directory containing the XML files generated by roLabelImg')
    parser.add_argument('--source',default='midv-500',choices=['midv-500','midv-2019'],help='midv-500 or midv-2019 dataset')
    parser.add_argument('--img_format',default='jpg',choices=['jpg','tif'])
    
    args = parser.parse_args()
    
    
    root_path = args.root
    if args.source == 'midv-500':
        source_type = 'midv-500'
    elif args.source == 'midv-2019':
        source_type = 'midv-2019'
    else:
        print('\n[ERROR] Wrong source type: {}'.format(args.source))
        exit()
        
    source_type = args.source
    img_format = '.' + args.img_format
    
    if not os.path.isdir(os.path.join(root_path,source_type)):
        print('\n[ERROR] Cannot find the directory: {}'.format(os.path.join(root_path,source_type)))
        exit()
        
    print(os.path.join(root_path,source_type))
    for dir1 in os.listdir(os.path.join(root_path,source_type)):
        xml_dir = os.path.join(root_path,source_type,dir1,'annotation_xml')
        if not os.path.isdir(xml_dir):
            continue
        json_dir = os.path.join(root_path,source_type,dir1,'annotation_json')
        if not os.path.isdir(json_dir):
            os.makedirs(json_dir)
            
        for file in os.listdir(xml_dir):
            if os.path.isfile(os.path.join(xml_dir,file)):
                json_filename = os.path.join(json_dir,file.split('.xml')[0] + '.json')
                xml_path = os.path.join(xml_dir,file)
                tree = ET.parse(xml_path)
                root = tree.getroot()
                
                output_json = {}
                output_json['data_created'] = date.today().strftime("%d-%m-%Y")
                output_json['source'] = source_type
                objects = []
                
                for obj in root.findall('object'):
                    obj_dict = {}

                    
                    flag = 0
                    if(obj.find('name') != None):
                        obj_dict['label'] = obj.find('name').text
                        flag+=1
                    if((obj.find('robndbox').find('cx') != None) & (obj.find('robndbox').find('cy') != None) & (obj.find('robndbox').find('w') != None) & (obj.find('robndbox').find('h') != None)):
                        obj_dict['point'] = [float(obj.find('robndbox').find('cx').text),
                                float(obj.find('robndbox').find('cy').text),
                                float(obj.find('robndbox').find('w').text),
                                float(obj.find('robndbox').find('h').text)]
                        flag +=1
                    if(obj.find('robndbox').find('angle') != None):
                        obj_dict['angle'] = float(obj.find('robndbox').find('angle').text)
                        flag +=1
    
                    if((obj.find('robndbox').find('cx') != None) & (obj.find('robndbox').find('cy') != None) & (obj.find('robndbox').find('w') != None) & (obj.find('robndbox').find('h') != None) & (obj.find('robndbox').find('angle') != None)):
                        coord = get_rotated_bounding_box(float(obj.find('robndbox').find('cx').text),
                                                        float(obj.find('robndbox').find('cy').text),
                                                        float(obj.find('robndbox').find('w').text),
                                                        float(obj.find('robndbox').find('h').text),
                                                        float(obj.find('robndbox').find('angle').text))
                        obj_dict['quad'] = [coord[0][0], coord[0][1], coord[1][0], coord[1][1], coord[2][0], coord[2][1], coord[3][0], coord[3][1]]
                    if flag == 3:
                        obj_dict['text'] = ''
                        obj_dict['flags'] = {}
                        objects.append(obj_dict)
                output_json['rotated_objects'] = objects
                output_json['image_path'] = os.path.join(source_type,dir1,'images',file.split('.xml')[0]+img_format)
                if((root.find('size').find('width') != None) & (root.find('size').find('height') != None)):
                    output_json['image_height'] = root.find('size').find('height').text
                    output_json['image_width'] = root.find('size').find('width').text
                with open(json_filename,'w') as f:
                    json.dump(output_json, f)