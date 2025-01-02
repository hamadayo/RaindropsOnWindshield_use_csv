import cv2
import math
import numpy as np
from PIL import Image
from PIL import ImageDraw
import pyblur
import random
from random import randint
from raindrop.config import cfg

"""
This module contains a description of Raindrop class
"""

def make_bezier(xys):
    # xys should be a sequence of 2-tuples (Bezier control points)
	# 今回は常に3つの制御点を持つベジェ曲線を扱う
    n = len(xys)
    combinations = pascal_row(n-1)
    def bezier(ts):
        # This uses the generalized formula for bezier curves
        # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        result = []
        for t in ts:
            tpowers = (t**i for i in range(n))
            upowers = reversed([(1-t)**i for i in range(n)])
            coefs = [c*a*b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                tuple(sum([coef*p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
        return result
    return bezier

# パスカルの三角形を計算
def pascal_row(n, memo={}):
    # This returns the nth row of Pascal Triangle
	# 仮にn = 5の場合、memoには{5: [1, 5, 10, 10, 5, 1]}が格納される
    if n in memo:
        return memo[n]
	# パスカルの行の最初は1
    result = [1]
    x, numerator = 1, n
	# n = 5の場合、denominatorは(1, 3)なので1~2までの範囲でループ
    for denominator in range(1, n//2+1):
		#numerator = 5, denominator = 1なのでx = 5
        x *= numerator
        x /= denominator
        result.append(x) # [1, 5]
        numerator -= 1 # 4

	# n = 5の場合、00101のようになるので
    if n&1 == 0:
		# 偶数の場合最後の要素を削除して反転して追加　[1, 4, 6]なら、[1, 4, 6, 4, 1]
        result.extend(reversed(result[:-1]))
    else:
		# 奇数の場合そのまま反転して追加　[1, 5, 10]なら、[1, 5, 10, 10, 5, 1]
        result.extend(reversed(result))
	
	# n = 5の場合、memo[5]に[1, 5, 10, 10, 5, 1]を格納
    memo[n] = result
    return result


class Raindrop():
	def __init__(self, key, centerxy = None, radius = None, shape = None):
		"""
		:param key: a unique key identifying a drop
		:param centerxy: tuple defining coordinates of raindrop center in the image
		:param radius: radius of a drop
		:param shape: int from 0 to 2 defining raindrop shape type
		"""
		# 一位に識別するためのキー
		self.key = key	
		# 衝突したかどうか	
		self.ifcol = False	
		# 衝突した雨滴のキー
		self.col_with = []
		# 雨滴の中心座標
		self.center = centerxy
		# 雨滴の半径
		self.radius = radius
		# ぼかし係数（最小値は１）半径に基づいて計算
		self.blur_coeff = max(int(self.radius/3), 1)
		# 雨滴の形状 0: 円形 1: 楕円形 2: ベジェ曲線
		self.shape = shape         
		# 雨滴の種類を表す   
		self.type = "default"
        # label map's WxH = 4*R , 5*R
		# 雨滴のラベルマップ　雨滴が存在する部分は1、それ以外は0
		self.labelmap = np.zeros((self.radius * 5, self.radius*4))
		# 雨滴のアルファマップ labelmapにぼかしを適用した配列で、0~255の値を持つ(0が透明、255が不透明)
		self.alphamap = np.zeros((self.radius * 5, self.radius*4))
		# 雨滴の背景
		self.background = None
		# 雨滴のテクスチャ
		self.texture = None
		# 雨滴の形状に応じてアルファマップを作成
		self._create_label()
		self.use_label = False


	def setCollision(self, col, col_with):
		self.ifcol = col
		self.col_with = col_with

	def updateTexture(self, bg): 	
		fg = pyblur.GaussianBlur(Image.fromarray(np.uint8(bg)), 5)
		fg = np.asarray(fg)
		# add fish eye effect to simulate the background
		K = np.array([[30*self.radius, 0, 2*self.radius],
				[0., 20*self.radius, 3*self.radius],
				[0., 0., 1]])
		D = np.array([0.0, 0.0, 0.0, 0.0])
		Knew = K.copy()
        
		Knew[(0,1), (0,1)] = math.pow(self.radius, 1/500)*2 * Knew[(0,1), (0,1)]
		fisheye = cv2.fisheye.undistortImage(fg, K, D=D, Knew=Knew)     

		tmp = np.expand_dims(self.alphamap, axis = -1)
		tmp = np.concatenate((fisheye, tmp), axis = 2)
		
		self.texture = Image.fromarray(tmp.astype('uint8'), 'RGBA')
        
		# uncomment if you want a background in drop to be flipped
		#self.texture = self.texture.transpose(Image.FLIP_TOP_BOTTOM)
        
	def _create_label(self):  
		self._createDefaultDrop()

	def _createDefaultDrop(self):
		"""
		create the raindrop Alpha Map according to its shape type
		update raindrop label
		"""         
		if (self.shape == 0):    
			# cv2.circleでlabelmapに中心が半径*2, 半径*3の位置に半径の大きさの円を描画,128で内側まで塗りつぶし(-1)
			cv2.circle(self.labelmap, (self.radius * 2, self.radius * 3), int(self.radius), 128, -1)
			# labelmapにぼかし効果を加え、alphamapを生成（0~255の値）
			self.alphamap = pyblur.GaussianBlur(Image.fromarray(np.uint8(self.labelmap)), self.blur_coeff)  
			# numpy配列に変換しfloat型に変換
			self.alphamap = np.asarray(self.alphamap).astype(float)
			# 正規化後に0~255の値に再スケーリング
			self.alphamap = self.alphamap/np.max(self.alphamap)*255.0
			# set label map
			self.labelmap[self.labelmap>0] = 1
               
		if (self.shape == 1):   
			# cv2.circleでlabelmapに中心が半径*2, 半径*3の位置に半径の大きさの円を描画,128で内側まで塗りつぶし(-1) 
			cv2.circle(self.labelmap, (self.radius * 2, self.radius * 3), int(self.radius), 128, -1)
			# cv2.ellipseでlabelmapに中心が半径*2, 半径*3の位置に横軸が半径、縦軸が1.3倍の半径の楕円を描画,描画範囲は180~360度,128で内側まで塗りつぶし(-1)
			cv2.ellipse(self.labelmap, (self.radius * 2, self.radius * 3), (self.radius, int(1.3*math.sqrt(3) * self.radius)), 0, 180, 360, 128, -1)
			# 後は同じ
			self.alphamap = pyblur.GaussianBlur(Image.fromarray(np.uint8(self.labelmap)), self.blur_coeff)        
			self.alphamap = np.asarray(self.alphamap).astype(float)
			self.alphamap = self.alphamap/np.max(self.alphamap)*255.0
			# set label map
			self.labelmap[self.labelmap>0] = 1
            
		if (self.shape == 2): 
			#ベジェ曲線の制御点を設定（x, y)のタプル
			A = cfg["A"]
			B = cfg["B"]
			C = cfg["C"]
			D = cfg["D"]
			# labelmapをnumpy配列からPIL画像のグレースケール画像に変換
			img = Image.fromarray(np.uint8(self.labelmap) , 'L')
			# ImageDraw.Drawで描画操作を行う
			draw = ImageDraw.Draw(img)
			# ベジェ曲線の計算
			ts = [t/100.0 for t in range(101)]
			xys = [(self.radius * C[0], self.radius * C[1]), (self.radius * B[0], self.radius * B[1]), (self.radius * D[0], self.radius * D[1])]
			bezier = make_bezier(xys)
			points = bezier(ts)

			# ２つ目のベジェ曲線の計算
			xys = [(self.radius * C[0], self.radius * C[1]), (self.radius * A[0], self.radius * A[1]), (self.radius * D[0], self.radius * D[1])]
			bezier = make_bezier(xys)
			# pointsに追加
			points.extend(bezier(ts))
			# ベジェ曲線で囲まれた領域を塗りつぶし
			draw.polygon(points, fill = 'gray')   

			#　後は同じ        
			self.alphamap = pyblur.GaussianBlur(img, self.blur_coeff)       
			self.alphamap = np.asarray(self.alphamap).astype(float)
			self.alphamap = self.alphamap/np.max(self.alphamap)*255.0
			# set label map
			self.labelmap[self.labelmap>0] = 1            


	def setKey(self, key):
		self.key = key

	def getLabelMap(self):
		return self.labelmap

	def getAlphaMap(self):
		return self.alphamap

	def getTexture(self):
		return self.texture

	def getCenters(self):
		return self.center
		
	def getRadius(self):
		return self.radius

	def getKey(self):
		return self.key

	def getIfColli(self):
		return self.ifcol

	def getCollisionList(self):
		return self.col_with
	
	def getUseLabel(self):
		return self.use_label
