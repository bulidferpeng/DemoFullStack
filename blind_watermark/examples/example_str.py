#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# embed string
# coding: utf-8
import numpy as np
from blind_watermark import WaterMark
from blind_watermark import att
from blind_watermark.recover import estimate_crop_parameters, recover_crop
import cv2
import os

os.chdir(os.path.dirname(__file__))

bwm = WaterMark(password_img=1, password_wm=1)
bwm.read_img('pic/or1.png')
wm = 'jianchu yuanchuang'
bwm.read_wm(wm, mode='str')
bwm.embed('output/or1.jpeg')

len_wm = len(bwm.wm_bit)  # 解水印需要用到长度
print('Put down the length of wm_bit {len_wm}'.format(len_wm=len_wm))

ori_img_shape = cv2.imread('pic/or1.png').shape[:2]  # 抗攻击有时需要知道原图的shape
h, w = ori_img_shape

# %% 解水印
bwm1 = WaterMark(password_img=1, password_wm=1)
wm_extract = bwm1.extract('output/or1.jpeg', wm_shape=len_wm, mode='str')
print("不攻击的提取结果：", wm_extract)

assert wm == wm_extract, '提取水印和原水印不一致'

# %%screenshotAttack1 = 裁剪攻击 + suofangAttack + 知道攻击参数（之后按照参数还原）

loc_r = ((0.1, 0.1), (0.5, 0.5))
scale = 0.7

x1, y1, x2, y2 = int(w * loc_r[0][0]), int(h * loc_r[0][1]), int(w * loc_r[1][0]), int(h * loc_r[1][1])

# screenshotAttack
att.cut_att3(input_filename='output/or1.jpeg', output_file_name='output/screenshotAttack1.png',
             loc=(x1, y1, x2, y2), scale=scale)

recover_crop(template_file='output/screenshotAttack1.png', output_file_name='output/screenshotAttack1_revert.png',
             loc=(x1, y1, x2, y2), image_o_shape=ori_img_shape)

bwm1 = WaterMark(password_wm=1, password_img=1)
wm_extract = bwm1.extract('output/screenshotAttack1_revert.png', wm_shape=len_wm, mode='str')
print("screenshotAttack，知道攻击参数。提取结果：", wm_extract)
assert wm == wm_extract, '提取水印和原水印不一致'

# %% screenshotAttack2 = 剪切攻击 + suofangAttack + 不知道攻击参数（因此需要 estimate_crop_parameters 来推测攻击参数）
loc_r = ((0.1, 0.1), (0.7, 0.6))
scale = 0.7

x1, y1, x2, y2 = int(w * loc_r[0][0]), int(h * loc_r[0][1]), int(w * loc_r[1][0]), int(h * loc_r[1][1])

print(f'Crop attack\'s real parameters: x1={x1},y1={y1},x2={x2},y2={y2}')
att.cut_att3(input_filename='output/or1.jpeg', output_file_name='output/screenshotAttack2.png',
             loc=(x1, y1, x2, y2), scale=scale)

# estimate crop attack parameters:
(x1, y1, x2, y2), image_o_shape, score, scale_infer = estimate_crop_parameters(original_file='output/or1.jpeg',
                                                                               template_file='output/screenshotAttack2.png',
                                                                               scale=(0.5, 2), search_num=200)

print(f'Crop att estimate parameters: x1={x1},y1={y1},x2={x2},y2={y2}, scale_infer = {scale_infer}. score={score}')

# recover from attack:
recover_crop(template_file='output/screenshotAttack2.png', output_file_name='output/screenshotAttack2_revert.png',
             loc=(x1, y1, x2, y2), image_o_shape=image_o_shape)

bwm1 = WaterMark(password_wm=1, password_img=1)
wm_extract = bwm1.extract('output/screenshotAttack2_revert.png', wm_shape=len_wm, mode='str')
print("screenshotAttack，不知道攻击参数。提取结果：", wm_extract)
assert wm == wm_extract, '提取水印和原水印不一致'

# %%裁剪攻击1 = 裁剪 + 不做缩放 + 知道攻击参数
loc_r = ((0.1, 0.2), (0.5, 0.5))
x1, y1, x2, y2 = int(w * loc_r[0][0]), int(h * loc_r[0][1]), int(w * loc_r[1][0]), int(h * loc_r[1][1])

att.cut_att3(input_filename='output/or1.jpeg', output_file_name='output/RandomPruningAttack.png',
             loc=(x1, y1, x2, y2), scale=None)

# recover from attack:
recover_crop(template_file='output/RandomPruningAttack.png', output_file_name='output/RandomPruningAttack_revert.png',
             loc=(x1, y1, x2, y2), image_o_shape=image_o_shape)

bwm1 = WaterMark(password_wm=1, password_img=1)
wm_extract = bwm1.extract('output/RandomPruningAttack_revert.png', wm_shape=len_wm, mode='str')
print("裁剪攻击，知道攻击参数。提取结果：", wm_extract)
assert wm == wm_extract, '提取水印和原水印不一致'

# %% 裁剪攻击2 = 裁剪 + 不做缩放 + 不知道攻击参数
loc_r = ((0.1, 0.1), (0.5, 0.4))
x1, y1, x2, y2 = int(w * loc_r[0][0]), int(h * loc_r[0][1]), int(w * loc_r[1][0]), int(h * loc_r[1][1])

att.cut_att3(input_filename='output/or1.jpeg', output_file_name='output/RandomPruningAttack2.png',
             loc=(x1, y1, x2, y2), scale=None)

print(f'Cut attack\'s real parameters: x1={x1},y1={y1},x2={x2},y2={y2}')

# estimate crop attack parameters:
(x1, y1, x2, y2), image_o_shape, score, scale_infer = estimate_crop_parameters(original_file='output/or1.jpeg',
                                                                               template_file='output/RandomPruningAttack2.png',
                                                                               scale=(1, 1), search_num=None)

print(f'Cut attack\'s estimate parameters: x1={x1},y1={y1},x2={x2},y2={y2}. score={score}')

# recover from attack:
recover_crop(template_file='output/RandomPruningAttack2.png', output_file_name='output/RandomPruningAttack2_revert.png',
             loc=(x1, y1, x2, y2), image_o_shape=image_o_shape)

bwm1 = WaterMark(password_wm=1, password_img=1)
wm_extract = bwm1.extract('output/RandomPruningAttack2_revert.png', wm_shape=len_wm, mode='str')
print("裁剪攻击，不知道攻击参数。提取结果：", wm_extract)
assert wm == wm_extract, '提取水印和原水印不一致'

# %%椒盐攻击
ratio = 0.05
att.salt_pepper_att(input_filename='output/or1.jpeg', output_file_name='output/椒盐攻击.png', ratio=ratio)
# ratio是椒盐概率

# 提取
wm_extract = bwm1.extract('output/椒盐攻击.png', wm_shape=len_wm, mode='str')
print(f"椒盐攻击ratio={ratio}后的提取结果：", wm_extract)
assert np.all(wm == wm_extract), '提取水印和原水印不一致'

# %%rotatingAttack
angle = 60
att.rot_att(input_filename='output/or1.jpeg', output_file_name='output/rotatingAttack.png', angle=angle)
att.rot_att(input_filename='output/rotatingAttack.png', output_file_name='output/rotatingAttack_revert.png', angle=-angle)

# 提取水印
bwm1 = WaterMark(password_wm=1, password_img=1)
wm_extract = bwm1.extract('output/rotatingAttack_revert.png', wm_shape=len_wm, mode='str')
print(f"rotatingAttackangle={angle}后的提取结果：", wm_extract)
assert wm == wm_extract, '提取水印和原水印不一致'

# %%遮挡攻击
n = 60
att.shelter_att(input_filename='output/or1.jpeg', output_file_name='output/multiOcclusionAttack.png', ratio=0.1, n=n)

# 提取
bwm1 = WaterMark(password_wm=1, password_img=1)
wm_extract = bwm1.extract('output/multiOcclusionAttack.png', wm_shape=len_wm, mode='str')
print(f"遮挡攻击{n}次后的提取结果：", wm_extract)
assert wm == wm_extract, '提取水印和原水印不一致'

# %%suofangAttack
att.resize_att(input_filename='output/or1.jpeg', output_file_name='output/suofangAttack.png', out_shape=(400, 300))
att.resize_att(input_filename='output/suofangAttack.png', output_file_name='output/suofangAttack_revert.png',
               out_shape=ori_img_shape[::-1])
# out_shape 是分辨率，需要颠倒一下

bwm1 = WaterMark(password_wm=1, password_img=1)
wm_extract = bwm1.extract('output/suofangAttack_revert.png', wm_shape=len_wm, mode='str')
print("缩放攻击后的提取结果：", wm_extract)
assert np.all(wm == wm_extract), '提取水印和原水印不一致'
# %%brightnessAttack

att.bright_att(input_filename='output/or1.jpeg', output_file_name='output/brightnessAttack.png', ratio=0.9)
att.bright_att(input_filename='output/brightnessAttack.png', output_file_name='output/brightnessAttack_revert.png', ratio=1.1)
wm_extract = bwm1.extract('output/brightnessAttack_revert.png', wm_shape=len_wm, mode='str')

print("brightnessAttack后的提取结果：", wm_extract)
assert np.all(wm == wm_extract), '提取水印和原水印不一致'
