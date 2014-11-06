import urllib2

images = ['smw2_yoshi_01_input.png', 'smw2_yoshi_02_input.png', 'smw_bowser_input.png', 'smw_boo_input.png', 'smw_dolphin_input.png', 'smw_help_input.png', 'smw_mario_input.png', 'smw_mario_yoshi_input.png', 'smw_mushroom_input.png', 'smw_yoshi_input.png', 'sma_chest_input.png', 'sma_peach_01_input.png', 'sma_peach_02_input.png', 'smb_jump_input.png', 'smw_cape_mario_yoshi_input.png', 'sma_toad_input.png', 'smw2_koopa_input.png', 'invaders_01_input.png', 'invaders_02_input.png', 'invaders_03_input.png', 'invaders_04_input.png', 'invaders_05_input.png', 'invaders_06_input.png', 'mana_granpa_input.png', 'mana_joch_input.png', 'mana_rabite_input.png', 'mana_randi_01_input.png', 'mana_randi_02_input.png', 'mana_salamando_input.png', 'mana_sword_input.png', 'sbm1_01_input.png', 'sbm1_02_input.png', 'sbm1_03_input.png', 'sbm1_04_input.png', 'sbm4_01_input.png', 'sbm4_02_input.png', 'sbm4_03_input.png', 'sbm4_04_input.png', 'gaxe2_axbattler_01_input.png', 'gaxe2_axbattler_02_input.png', 'gaxe_skeleton_input.png', 'icon_atari_bomb_input.png', 'icon_disk_input.png', 'vista_cursor_input.png', 'win31_cursor_input.png', 'win31_386_input.png', 'win31_control_panel_input.png', 'win31_fonts_input.png', 'win31_keyboard_input.png', 'win31_ports_input.png', 'win31_setup_input.png', 'vikings_baelog_input.png', 'vikings_eric_input.png', 'vikings_olaf_input.png']

base_url = 'http://research.microsoft.com/en-us/um/people/kopf/pixelart/supplementary/input_images/'

for image_name in images:
    url = base_url + image_name
    image_data = urllib2.urlopen(url).read()
    path_name = 'img/' + image_name.replace('_input', '')
    with open(path_name, 'wb') as f:
        f.write(image_data)
    print 'Downloaded', image_name, 'to', path_name