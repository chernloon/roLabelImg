import numpy as np
import cv2
import json
import argparse
import pprint
'''
python tool-visualize-rotated-bounding-box-from-json.py --image C:/CL/Dataset/passport/passport-mrz-ocr/midv-500/05_aze_passport/images/CA05_01.jpg --json C:/CL/Dataset/passport/passport-mrz-ocr/midv-500/05_aze_passport/annotation_json/CA05_01.json
'''
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser("This program is to read an image and json, and display the rotated bounding box")
    parser.add_argument("--image",required=True,help="image path")
    parser.add_argument("--json",required=True,help="json path")
    
    args = parser.parse_args()
    
    img = cv2.imread(args.image,1)
    if img is None:
        print("\n[ERROR] Fail to load image {}\n".format(args.image))
        
    displayImg1 = img.copy()
    displayImg2 = img.copy()
    
    
    
    try:
        with open(args.json) as f:
            j = json.load(f)
            
    except Exception as e:
        print('\n[ERROR]: {}'.format(e))
        exit()
    
    for i in range(len(j['rotated_objects'])):
        

        if ('point' in j['rotated_objects'][i]) & ('quad' in j['rotated_objects'][i]):
            cx = j['rotated_objects'][i]['point'][0]
            cy = j['rotated_objects'][i]['point'][1]
            w = j['rotated_objects'][i]['point'][2]
            h = j['rotated_objects'][i]['point'][3]
            angle = j['rotated_objects'][i]['angle']
            rot_mat = cv2.getRotationMatrix2D((cx,cy),-angle*180*7/22,1.0)
            
            coord_mat = np.array([[cx-int(w/2),cy-int(h/2)],
                     [cx+int(w/2),cy-int(h/2)],
                     [cx+int(w/2),cy+int(h/2)],
                     [cx-int(w/2),cy+int(h/2)]])
            
            new_coord_mat = np.zeros(coord_mat.shape,int)

            for k,coord in enumerate(coord_mat):
                c = np.matmul(rot_mat,np.array([[coord[0]],[coord[1]],[1]]))
                new_coord_mat[k][0] = c[0]
                new_coord_mat[k][1] = c[1]
                
            displayImg1 = cv2.line(displayImg1,(new_coord_mat[0][0],new_coord_mat[0][1]),(new_coord_mat[1][0],new_coord_mat[1][1]),(0,0,255),3,cv2.LINE_AA)
            displayImg1 = cv2.line(displayImg1,(new_coord_mat[1][0],new_coord_mat[1][1]),(new_coord_mat[2][0],new_coord_mat[2][1]),(0,0,255),3,cv2.LINE_AA)
            displayImg1 = cv2.line(displayImg1,(new_coord_mat[2][0],new_coord_mat[2][1]),(new_coord_mat[3][0],new_coord_mat[3][1]),(0,0,255),3,cv2.LINE_AA)
            displayImg1 = cv2.line(displayImg1,(new_coord_mat[3][0],new_coord_mat[3][1]),(new_coord_mat[0][0],new_coord_mat[0][1]),(0,0,255),3,cv2.LINE_AA)
            

        if ('quad' in j['rotated_objects'][i]):

            displayImg2 = cv2.line(displayImg2,(int(j['rotated_objects'][i]['quad'][0]),int(j['rotated_objects'][i]['quad'][1])),(int(j['rotated_objects'][i]['quad'][2]),int(j['rotated_objects'][i]['quad'][3])),(255,0,0),3,cv2.LINE_AA)
            displayImg2 = cv2.line(displayImg2,(int(j['rotated_objects'][i]['quad'][2]),int(j['rotated_objects'][i]['quad'][3])),(int(j['rotated_objects'][i]['quad'][4]),int(j['rotated_objects'][i]['quad'][5])),(255,0,0),3,cv2.LINE_AA)
            displayImg2 = cv2.line(displayImg2,(int(j['rotated_objects'][i]['quad'][4]),int(j['rotated_objects'][i]['quad'][5])),(int(j['rotated_objects'][i]['quad'][6]),int(j['rotated_objects'][i]['quad'][7])),(255,0,0),3,cv2.LINE_AA)
            displayImg2 = cv2.line(displayImg2,(int(j['rotated_objects'][i]['quad'][6]),int(j['rotated_objects'][i]['quad'][7])),(int(j['rotated_objects'][i]['quad'][0]),int(j['rotated_objects'][i]['quad'][1])),(255,0,0),3,cv2.LINE_AA)
            
    
    cv2.namedWindow('rotate the points',cv2.WINDOW_KEEPRATIO)
    cv2.imshow('rotate the points', displayImg1)
    cv2.namedWindow('read from quad', cv2.WINDOW_KEEPRATIO)
    cv2.imshow('read from quad',displayImg2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
