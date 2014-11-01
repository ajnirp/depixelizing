# images = [
# 'img/smw2_koopa.png',
# 'img/sma_chest.png',
# 'img/smw2_yoshi_02.png',
# 'img/smw2_yoshi_01.png',
# 'img/sma_toad.png',
# 'img/invaders_01.png',
# 'img/invaders_02.png',
# 'img/smb_jump.png',
# 'img/smw_boo.png',
# 'img/sma_peach_01.png',
# 'img/smw_dolphin.png',
# 'img/smw_cape_mario_yoshi.png'
# ]

Dir.glob('img/*.png') do |image|
	`python main.py --tests --render voronoi --image #{image}`
end