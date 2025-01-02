import random
from random import randint
import cv2
import math
import numpy as np
import pyblur
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageDraw
from skimage.measure import label as skimage_label
from .raindrop import Raindrop, make_bezier

"""
This module contain two functions:
Check Collision -- handle the collision of the drops
generateDrops -- generate raindrops on the image

Author: Chia-Tse, Chang
Edited by Vera, Soboleva
"""

def generate_random_positions(drop_num, imgw, imgh, region="top-right"):
    """
    Generate random positions within a specified region of the image.

    :param drop_num: Number of positions to generate.
    :param imgw: Image width.
    :param imgh: Image height.
    :param region: Region of the image to limit the positions. 
                   Options: "top-right", "top-center", "top-left".
    :return: List of (x, y) positions.
    """
    if region == "top-right":
        x_min, x_max = imgw // 2, imgw
        y_min, y_max = 0, imgh // 3
    elif region == "top-center":
        x_min, x_max = imgw // 3, 2 * imgw // 3
        y_min, y_max = 0, imgh // 3
    elif region == "top-left":
        x_min, x_max = 0, imgw // 2
        y_min, y_max = 0, imgh // 3
    elif region == "bottom-right":
        x_min, x_max = imgw // 2, imgw
        y_min, y_max = 2 * imgh // 3, imgh
    elif region == "bottom-center":
        x_min, x_max = imgw // 3, 2 * imgw // 3
        y_min, y_max = 2 * imgh // 3, imgh
    elif region == "bottom-left":
        x_min, x_max = 0, imgw // 2
        y_min, y_max = 2 * imgh // 3, imgh
    elif region == "middle-right":
        x_min, x_max = imgw // 2, imgw
        y_min, y_max = imgh // 3, 2 * imgh // 3
    elif region == "middle-center":
        x_min, x_max = imgw // 3, 2 * imgw // 3
        y_min, y_max = imgh // 3, 2 * imgh // 3
    elif region == "middle-left":
        x_min, x_max = 0, imgw // 3
        y_min, y_max = imgh // 3, 2 * imgh // 3
    elif region == "forth-top-right":
        x_min, x_max = imgw // 2, imgw
        y_min, y_max = 0, imgh // 2
    elif region == "forth-top-left":
        x_min, x_max = 0, imgw // 2
        y_min, y_max = 0, imgh // 2
    elif region == "forth-bottom-right":
        x_min, x_max = imgw // 2, imgw
        y_min, y_max = imgh // 2, imgh
    elif region == "forth-bottom-left":
        x_min, x_max = 0, imgw // 2
        y_min, y_max = imgh // 2, imgh

    else:
        raise ValueError("Invalid region specified. Use 'top-right', 'top-center', or 'top-left'.")
    
    # Generate random positions within the specified region
    ran_pos = [(random.randint(x_min, x_max - 1), random.randint(y_min, y_max - 1)) for _ in range(drop_num)]
    return ran_pos



def CheckCollision(DropList):
	"""
	This function handle the collision of the drops
	:param DropList: list of raindrop class objects 
	"""
	"""
	具体例
	final_x = 20 * 10 = 200
	final_y = 30 * 10 = 300
	tmp_devide = 10
	final_x += 25 * 15 = 200 + 375 = 575
	final_y += 35 * 15 = 300 + 525 = 825
	tmp_devide += 15 = 10 + 15 = 25
	final_x = int(round(575 / 25)) = 23
	final_y = int(round(825 / 25)) = 33
	final_R = int(round(math.sqrt(10^2 + 15^2))) = int(round(math.sqrt(100 + 225))) = 18
	衝突した雨滴を1つにまとめて新しい雨滴を生成する
	"""
	listFinalDrops = []
	Checked_list = []
	list_len = len(DropList)
	# because latter raindrops in raindrop list should has more colision information
	# so reverse list	
	DropList.reverse()
	drop_key = 1
	for drop in DropList:
		# if the drop has not been handle	
		if drop.getKey() not in Checked_list:			
			# if drop has collision with other drops
			if drop.getIfColli():
				# get collision list
				collision_list = drop.getCollisionList()
				# first get radius and center to decide how  will the collision do
				final_x = drop.getCenters()[0] * drop.getRadius()
				final_y = drop.getCenters()[1]  * drop.getRadius()
				tmp_devide = drop.getRadius()
				final_R = drop.getRadius()  * drop.getRadius()
				for col_id in collision_list:
					col_id = int(col_id)
					Checked_list.append(col_id)
					# list start from 0
					final_x += DropList[list_len - col_id].getRadius() * DropList[list_len - col_id].getCenters()[0]
					final_y += DropList[list_len - col_id].getRadius() * DropList[list_len - col_id].getCenters()[1]
					tmp_devide += DropList[list_len - col_id].getRadius()
					final_R += DropList[list_len - col_id].getRadius() * DropList[list_len - col_id].getRadius() 
				final_x = int(round(final_x/tmp_devide))
				final_y = int(round(final_y/tmp_devide))
				final_R = int(round(math.sqrt(final_R)))
				# rebuild drop after handled the collisions
				newDrop = Raindrop(drop_key, (final_x, final_y), final_R)
				drop_key = drop_key+1
				listFinalDrops.append(newDrop)
			# no collision
			else:
				drop.setKey(drop_key)
				drop_key = drop_key+1
				listFinalDrops.append(drop)
	
	return listFinalDrops

def generate_label(h, w, cfg):
	"""
	This function generate list of raindrop class objects and label map of this drops in the image 
	:param h: image height
	:param w: image width
	:param cfg: config with global constants
	:param shape: int from 0 to 2 defining raindrop shape type
	"""
	# configを読み込む
	maxDrop = cfg["maxDrops"]
	minDrop = cfg["minDrops"]   
	maxR = cfg["maxR"]
	minR = cfg["minR"]
	region = cfg["region"]
	# 雨滴の個数をランダムに決定   
	drop_num = randint(minDrop, maxDrop)   
	imgh = h
	imgw = w   
    # random drops position
	# 画像内にランダムに雨滴の位置を決定
	ran_pos = generate_random_positions(drop_num, imgw, imgh, region)
	listRainDrops = []
	listFinalDrops = []   
	for key, pos in enumerate(ran_pos):
		# keyを1から始める
		key = key+1
		# 雨滴の半径をランダムに決定
		radius = random.randint(minR, maxR)
		# 雨滴の形状をランダムに決定 0が円形、1が楕円形、2がベジェ曲線
		shape = random.randint(0,2)
		# 雨滴のオブジェクトを生成
		drop = Raindrop(key, pos, radius, shape)
		# 雨滴のリストに追加
		listRainDrops.append(drop)    
    # to check if collision or not
	# 画像サイズと同じサイズのラベルマップを生成
	label_map = np.zeros([h, w])
	# 雨滴の総数を衝突回数として初期化
	collisionNum = len(listRainDrops)
	# 雨滴のリストをコピー
	listFinalDrops = list(listRainDrops)
	loop = 0
	while collisionNum > 0:
		loop = loop + 1
		listFinalDrops = list(listFinalDrops)
		collisionNum = len(listFinalDrops)
		# label_mapの初期化　雨滴がない部分は0, 雨滴がある部分は雨滴のキーが格納される
		label_map = np.zeros_like(label_map)
        # Check Collision
		for drop in listFinalDrops:
            # check the bounding 
			(ix, iy) = drop.getCenters()
			radius = drop.getRadius()
			# ix = 90, iy = 20, raduis = 10のとき、ROI_WL = 20, ROI_WR = 20, ROI_HU = 30, ROI_HD = 20
			# このとき、iy - 3*radius = 20 - 30 = -10なので、ROI_HU = 20,　それ以外は同様

			ROI_WL = 2*radius
			ROI_WR = 2*radius
			ROI_HU = 3*radius
			ROI_HD = 2*radius
			if (iy-3*radius) <0 :
				ROI_HU = iy
			if (iy+2*radius)>imgh:
				ROI_HD = imgh - iy
			if (ix-2*radius)<0:
				ROI_WL = ix
			if  (ix+2*radius) > imgw:
				ROI_WR = imgw - ix
            # apply raindrop label map to Image's label map
			# drop_labelは雨滴のラベルマップ（画像全体ではない）
			drop_label = drop.getLabelMap()
            # check if center has already has drops
			# 中心座標に既に雨滴があるかどうかを確認
			if (label_map[iy, ix] > 0):
				# 既に雨滴がある場合、衝突したとして、衝突した雨滴のキーを取得
				col_ids = np.unique(label_map[iy - ROI_HU:iy + ROI_HD, ix - ROI_WL: ix+ROI_WR])
				# 0以外の値を取得
				col_ids = col_ids[col_ids!=0]
				drop.setCollision(True, col_ids)
				label_map[iy - ROI_HU:iy + ROI_HD, ix - ROI_WL: ix+ROI_WR] = drop_label[3*radius - ROI_HU:3*radius + ROI_HD, 2*radius - ROI_WL: 2*radius+ROI_WR] * drop.getKey()
			else:
				label_map[iy - ROI_HU:iy + ROI_HD, ix - ROI_WL: ix+ROI_WR] = drop_label[3*radius - ROI_HU:3*radius + ROI_HD, 2*radius - ROI_WL: 2*radius+ROI_WR] * drop.getKey()
                # no collision 
				collisionNum = collisionNum-1
                
		if collisionNum > 0:
			listFinalDrops = CheckCollision(listFinalDrops)        
	return listFinalDrops, label_map
    
    
def generateDrops(imagePath, cfg, listFinalDrops):
	"""
	Generate raindrops on the image
	:param imagePath: path to the image on which you want to generate drops
	:param cfg: config with global constants
	:param listFinalDrops: final list of raindrop class objects after handling collisions
	:param label_map: general label map of all drops in the image
	"""
	ifReturnLabel = cfg["return_label"]
	edge_ratio = cfg["edge_darkratio"]

	PIL_bg_img = Image.open(imagePath)
	bg_img = np.asarray(PIL_bg_img)
	label_map = np.zeros_like(bg_img)[:,:,0]
	imgh, imgw, _ = bg_img.shape
            
	A = cfg["A"]
	B = cfg["B"]
	C = cfg["C"]
	D = cfg["D"]

	alpha_map = np.zeros_like(label_map).astype(float)
	

	for drop in listFinalDrops:
		(ix, iy) = drop.getCenters()
		radius = drop.getRadius()
		ROI_WL = 2*radius
		ROI_WR = 2*radius
		ROI_HU = 3*radius
		ROI_HD = 2*radius
		if (iy-3*radius) <0 :
			ROI_HU = iy	
		if (iy+2*radius)>imgh:
			ROI_HD = imgh - iy
		if (ix-2*radius)<0:
			ROI_WL = ix			
		if  (ix+2*radius) > imgw:
			ROI_WR = imgw - ix

		drop_alpha = drop.getAlphaMap()	

		alpha_map[iy - ROI_HU:iy + ROI_HD, ix - ROI_WL: ix+ROI_WR] += drop_alpha[3*radius - ROI_HU:3*radius + ROI_HD, 2*radius - ROI_WL: 2*radius+ROI_WR]
			
	alpha_map = alpha_map/np.max(alpha_map)*255.0

	PIL_bg_img = Image.open(imagePath)
	for idx, drop in enumerate(listFinalDrops):
		(ix, iy) = drop.getCenters()
		radius = drop.getRadius()		
		ROIU = iy - 3*radius
		ROID = iy + 2*radius
		ROIL = ix - 2*radius
		ROIR = ix + 2*radius
		if (iy-3*radius) <0 :
			ROIU = 0
			ROID = 5*radius		
		if (iy+2*radius)>imgh:
			ROIU = imgh - 5*radius
			ROID = imgh
		if (ix-2*radius)<0:
			ROIL = 0
			ROIR = 4*radius
		if  (ix+2*radius) > imgw:		
			ROIL = imgw - 4*radius
			ROIR = imgw


		tmp_bg = bg_img[ROIU:ROID, ROIL:ROIR,:]
		try:
			drop.updateTexture(tmp_bg)
		except:
			del listFinalDrops[idx]
			continue
		tmp_alpha_map  = alpha_map[ROIU:ROID, ROIL:ROIR]

		output = drop.getTexture()		
		tmp_output = np.asarray(output).astype(float)[:,:,-1]
		tmp_alpha_map = tmp_alpha_map * (tmp_output/255)
		tmp_alpha_map  = Image.fromarray(tmp_alpha_map.astype('uint8'))		

		edge = ImageEnhance.Brightness(output)
		edge = edge.enhance(edge_ratio)

		PIL_bg_img.paste(edge, (ix-2*radius, iy-3*radius), output)
		PIL_bg_img.paste(output, (ix-2*radius, iy-3*radius), output)

	mask = np.zeros_like(bg_img)

	if len(listFinalDrops)>0:
		# make circles and elipses
		for drop in listFinalDrops:
			if (drop.shape == 0):
				cv2.circle(mask, drop.center, drop.radius, (255, 255, 255), -1)
			if (drop.shape == 1):
				cv2.circle(mask, drop.center, drop.radius, (255, 255, 255), -1)
				cv2.ellipse(mask, drop.center,\
						(drop.radius, int(1.3*math.sqrt(3) * drop.radius)), 0, 180, 360, (255, 255, 255), -1)
				
		img = Image.fromarray(np.uint8(mask[:,:,0]) , 'L') 
		# make beziers           
		for drop in listFinalDrops:    
			if (drop.shape == 2):
				img = Image.fromarray(np.uint8(img) , 'L')
				draw = ImageDraw.Draw(img)
				ts = [t/100.0 for t in range(101)]
				xys = [(drop.radius * C[0] - 2*drop.radius + drop.center[0], drop.radius * C[1] - 3*drop.radius + drop.center[1]), (drop.radius * B[0] - 2*drop.radius + drop.center[0], drop.radius * B[1] - 3*drop.radius + drop.center[1]), (drop.radius * D[0] - 2*drop.radius + drop.center[0], drop.radius * D[1] - 3*drop.radius + drop.center[1])]
				bezier = make_bezier(xys)
				points = bezier(ts)

				xys = [(drop.radius * C[0] - 2*drop.radius + drop.center[0], drop.radius * C[1] - 3*drop.radius + drop.center[1]), (drop.radius * A[0] - 2*drop.radius + drop.center[0], drop.radius * A[1] - 3*drop.radius + drop.center[1]), (drop.radius * D[0] - 2*drop.radius + drop.center[0], drop.radius * D[1] - 3*drop.radius + drop.center[1])]
				bezier = make_bezier(xys)
				points.extend(bezier(ts))
				draw.polygon(points, fill = 'white')
				mask = np.array(img)
			
	im_mask = Image.fromarray(mask.astype('uint8'))	

	if ifReturnLabel:
		output_label = np.array(alpha_map)
		output_label.flags.writeable = True
		output_label[output_label>0] = 1
		output_label = Image.fromarray(output_label.astype('uint8'))	
		return PIL_bg_img, output_label, im_mask

	return PIL_bg_img


