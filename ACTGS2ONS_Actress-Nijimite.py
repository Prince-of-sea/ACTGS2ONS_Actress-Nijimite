import configparser
import soundfile
import glob
import sys
import re
import os

debug = 0

same_hierarchy = (os.path.dirname(sys.argv[0]))#同一階層のパスを変数へ代入
DEFAULT_TXT = os.path.join(same_hierarchy,'default.txt')

if debug:
	same_hierarchy = os.path.join(same_hierarchy,'actress_nijimite_EXT')#debug

DIR_WAV = os.path.join(same_hierarchy,'WAV')
DIR_SCR = os.path.join(same_hierarchy,'scr')
DIR_CG = os.path.join(same_hierarchy,'cg')

effect_startnum = 10
effect_list = []
gosub_list = []

define_dict = {}
cfg_dict = {}

str2var_dict = {
	'filename':{},
	'numalias':{
		'S':40,
		'R':41,
		'K':42,
		'T':43,
		'L':44,
	},
}

str2var_cnt = {#0始まりNG! 最低1から
	'numalias':50,
	'filename':1,
	'gotocnt':1,
}


def effect_edit(t,f):
	global effect_list

	list_num=0
	if re.fullmatch(r'[0-9]+',t):#timeが数字のみ＝本処理

		for i, e in enumerate(effect_list,effect_startnum+1):#1からだと番号が競合する可能性あり
			if (e[0] == t) and (e[1] == f):
				list_num = i

		if not list_num:
			effect_list.append([t,f])
			list_num = len(effect_list) + effect_startnum

	return str(list_num)


def str2var_v2(s, m):
	if re.fullmatch(r'[0-9A-z-_]+?', s) and (m == 'filename'):#ファイル名かつ日本語なし
		s2 = s#変更不要
	else:
		global str2var_dict
		global str2var_cnt

		d=str2var_dict[m].get(s)#過去に変換済みかチェック
		
		if d:#変換済みの場合 - 要素をもってくる
			s2 = d
		else:#変換済みではない場合 - 新たに作成
			act_global = bool(re.fullmatch(r'F[0-9]{4}',s))#ACTGSでグローバル変数のばあい
			t = str2var_cnt[m]+(act_global*200)#200足す(≒ONSでもグローバルに)
			
			str2var_dict[m][s] = t
			s2 = t
			str2var_cnt[m] += 1
		
		#str型へ
		if (m == 'filename'):
			s2 = 'RENAMED__' + str(s2)
		else:
			s2 = str(s2)
	
	return s2


def music_cnv():
	d1 = glob.glob(os.path.join(DIR_WAV, '*.*'))
	for i in (d1):
		dd = (os.path.dirname(i) + '_dec')
		dp = (os.path.join(dd, os.path.splitext(os.path.basename(i))[0] + '.wav'))
		os.makedirs(dd, exist_ok=True)
		soundfile.write(dp, soundfile.read(i)[0], soundfile.read(i)[1])


def text_def():
	for p in glob.glob(os.path.join(DIR_SCR, '*.scr')):
		with open(p, encoding='cp932', errors='ignore') as f:
			for line in f:
					define_line = re.match(r'define[\t\s]+(.+?)[\t\s]+"?([A-z0-9-_]+?)"?\n', line)
					if define_line:
						define_dict[ define_line[1] ] = define_line[2]


def text_cnv():
	global gosub_list

	with open(DEFAULT_TXT) as f:
		txt = f.read()

	for p in glob.glob(os.path.join(DIR_SCR, '*.scr')):

		with open(p, encoding='cp932', errors='ignore') as f:

			name = os.path.splitext(os.path.basename(p))[0]
			txt += '\nerrmsg:reset\n;--------------- '+ name +' ---------------\n*SCR_'+ name.replace('.', '_') +'\n\n'

			fr = f.read()
			fr = fr.replace(r'{','{\n').replace(r'}','\n}\n')#処理しやすいようにif文全部複数行跨ぎに
			fr = re.sub(r'\n([^0-9A-z\[\]]+?)\{\n([^0-9A-z\[\]]+?)\n\}\n', r'\n\1｛\2｝', fr)#↑の副作用修正
			
			for line in fr.splitlines():
				line = line.replace(r';', r'') + '\n'
				line = re.sub(r'[\t\s]*(.+?)[\t\s]*\n', r'\1\n', line)

				msg2_line = re.match(r'msg2[\t\s]+(.*)', line)
				gosub_line = re.match(r'\[[\t\s]*(.+?)[\t\s]*\][\t\s]*\{', line)
				goend_line = re.match(r'}', line)
				change_line = re.match(r'change[\t\s]+"(.*?)"', line)
				mov_line = re.match(r'([^=+-]+)[\t\s]*([=+-]+)[\t\s]*([^=+-]+?)(([+-])[\t\s]*([0-9]+?))?\n', line)
				movie_line = re.match(r'movie "(.[A-z0-9-_]+?)(\.[A-z]+?)?"', line)
				flash_line = re.match(r'flash[0-9] ', line)
				goto_line = re.match(r'goto[\t\s]+(.+?)\n', line)
				at_line = re.match(r'@(.+?)\n', line)
				defsel_line = re.match(r'def_sel[\t\s]+(.+?)\n', line)
				select_line = re.match(r'select(2)?[\t\s]+([0-9])', line)#select2割と不完全な実装です
				bg_line = re.match(r'bg([1-3])?(_fi)?[\t\s]+', line)
				sp_line = re.match(r'sp([1-3])(_fi|_cf)?[\t\s]+', line)
				sp0_line = re.match(r'sp[\t\s]+([0-9])[\t\s]+"(.*?)"[\t\s]+([A-z_]+)', line)
				ev1_line = re.match(r'ev1(_fi)?[\t\s]+"(.*?)"', line)
				ef2_line = re.match(r'ef2[\t\s]+"(.*?)"[\t\s]+"(.*?)"', line)
				shake_line = re.match(r'shake[\t\s]+([A-z0-9-_]+)', line)
				ev_line = re.match(r'ev[\t\s]+"(.*?)"[\t\s]+([A-z_]+)', line)
				bgm1_line = re.match(r'bgm1[\t\s]+"(.*?)"', line)
				se2_line = re.match(r'se2[\t\s]+([A-z0-9-_\"]+)', line)

				if re.match(r'se_wait', line):
					pass

				elif re.match(r'random ([0-9]+)', line):
					pass

				elif re.match(r'cls', line):
					pass

				elif re.match(r'ret', line):
					line = '\\\n'

				elif re.match(r'vo "(.*?)"', line):
					if debug:
						line = r';' + line

				elif re.match(r'fo', line):
					pass

				elif re.match(r'sp_fo', line):
					pass

				elif re.match(r'bgm_fo', line):
					pass

				elif re.match(r'bgm_stop', line):
					pass

				elif re.match(r'sleep', line):
					pass

				elif re.match(r'wait ', line):#これ関数で上書きしてx100くらいにしたほうがいいかも
					line = line.replace(r'wait', r'wait_def')

				elif re.match(r'title', line):
					line = 'reset\n'

				elif re.match(r'menu', line):
					line = r';' + line#エラー防止の為コメントアウト

				elif re.match(r'def_cg', line):
					line = r';' + line#エラー防止の為コメントアウト

				elif re.match(r'kaisou_end', line):
					line = r';' + line#エラー防止の為コメントアウト

				elif re.match(r'flag_update', line):
					line = r';' + line#エラー防止の為コメントアウト

				elif re.match(r'bg_effect', line):#コレ結構危うい
					line = r';' + line#エラー防止の為コメントアウト

				elif re.match(r'auto_ret_off', line):
					line = r';' + line#エラー防止の為コメントアウト

				elif re.match(r'select_center_on', line):
					line = r';' + line#エラー防止の為コメントアウト

				elif re.match(r'N', line):
					line = r';' + line#エラー防止の為コメントアウト

				elif re.match(r'set_rgb', line):
					line = r';' + line#エラー防止の為コメントアウト

				elif re.match(r'window(_on|_off)', line):
					line = r';' + line#エラー防止の為コメントアウト

				elif re.match(r'window(_sel)? ', line):
					line = r';' + line#エラー防止の為コメントアウト

				elif re.match(r'define[\t\s]+(.+?)[\t\s]+"?([A-z0-9-_]+?)"?\n', line):
					line = r';' + line#エラー防止の為コメントアウト

				elif re.match(r'blue_sky', line):#
					line = r'mov %1000,1\n'#クリアフラグらしきもの

				elif msg2_line:
					line = 'msg2 "' + msg2_line[1].replace(r'【', r'').replace(r'】', r'') + '"\n'
					if debug:
						line = r';' + line

				elif gosub_line:
					cntstr_g = str(str2var_cnt['gotocnt'])

					line = '\n\nmov %10,0\n'

					for x in gosub_line[1].split(r'|'):
						for y in x.split(r'&'):
							gosub_str = re.search(r'([^=><!]+)[\t\s]*([=><!]+)[\t\s]*([^=><!]+)', y)

							gosub_str_1_b = define_dict.get(gosub_str[1])
							gosub_str_3_b = define_dict.get(gosub_str[3])

							gosub_str_1_t = gosub_str_1_b if (not gosub_str_1_b == None) else gosub_str[1]
							gosub_str_3_t = gosub_str_3_b if (not gosub_str_3_b == None) else gosub_str[3]

							gosub_str_1_r = gosub_str_1_t if (re.fullmatch(r'[0-9]+?', gosub_str_1_t)) else '%' + str2var_v2(gosub_str_1_t, 'numalias')#対象1(F0000 or 定義済み変数)
							gosub_str_3_r = gosub_str_3_t if (re.fullmatch(r'[0-9]+?', gosub_str_3_t)) else '%' + str2var_v2(gosub_str_3_t, 'numalias')#対象2(F0000 or 定義済み変数)
							gosub_str_2_r = r'!=' if (gosub_str[2] == '!') else gosub_str[2]#比較

							line += 'if ' + gosub_str_1_r + gosub_str_2_r + gosub_str_3_r + ' '
							
						line += 'mov %10,1\n'

					line += '\nif %10==1 goto *IF_GOTO' + cntstr_g + '\n'
					line += '*IF_END' + cntstr_g + '\n'
					line += 'goto *IF_SKIP' + cntstr_g + '\n'
					line += '*IF_GOTO' + cntstr_g + '\n\n'

					gosub_list += [cntstr_g]
					str2var_cnt['gotocnt'] += 1

				elif goend_line:
					line = '\ngoto *IF_END' + gosub_list[-1] + '\n'
					line += '*IF_SKIP' + gosub_list[-1] + '\n'

					gosub_list = gosub_list[:-1]

				elif change_line:#別scrへ飛ぶ
					line = 'goto *SCR_' + change_line[1] + '\n'

				elif select_line:
					if (select_line[1] == '2'):
						print('WARNING:"select2" used.')

					if (select_line[2] == '1'):
						line = 'select_start\n'
						line += 'select_reset\n'
					else:
						print('WARNING:select args error!')
						line = r';' + line#エラー防止の為コメントアウト

				elif bg_line:#背景
					if (bg_line[2] == '_fi'):
						fade = '"fi"'
					else:
						fade = '""'

					if bg_line[1] == '1':
						bg1_line = re.match(r'bg1(_fi)?[\t\s]+"(.*?)"', line)
						n = '1'
						a1 = '"' + bg1_line[2] + '"'
						a2 = '""'
						a3 = '""'
					elif bg_line[1] == '2':
						bg2_line = re.match(r'bg2(_fi)?[\t\s]+"(.*?)"[\t\s]+"(.*?)"', line)
						n = '2'
						a1 = '"' + bg2_line[2] + '"'
						a2 = '"' + bg2_line[3] + '"'
						a3 = '""'
					elif bg_line[1] == '3':
						bg3_line = re.match(r'bg3(_fi)?[\t\s]+"(.*?)"[\t\s]+"(.*?)"[\t\s]+"(.*?)"', line)
						n = '3'
						a1 = '"' + bg3_line[2] + '"'
						a2 = '"' + bg3_line[3] + '"'
						a3 = '"' + bg3_line[4] + '"'
					else:
						bg0_line = re.match(r'bg[\t\s]+"(.*?)"[\t\s]+([A-z_]+)', line)
						n = '0'
						a1 = '"' + bg0_line[1] + '"'
						a2 = '"' + bg0_line[2] + '"'
						a3 = '""'

					line = 'bg_def ' + fade + ',' + n + ',' + a1 + ',' + a2 + ',' + a3 + '\n'

				elif sp_line:#立ち絵
					if (sp_line[2] == '_fi'):
						fade = '"fi"'
					if (sp_line[2] == '_cf'):
						fade = '"cf"'
					else:
						fade = '""'

					if sp_line[1] == '1':
						sp1_line = re.match(r'sp1(_fi|_cf)?[\t\s]+"(.*?)"', line)
						n = '1'
						a1 = '"' + sp1_line[2] + '"'
						a2 = '""'
						a3 = '""'
					elif sp_line[1] == '2':
						sp2_line = re.match(r'sp2(_fi|_cf)?[\t\s]+"(.*?)"[\t\s]+"(.*?)"', line)
						n = '2'
						a1 = '"' + sp2_line[2] + '"'
						a2 = '"' + sp2_line[3] + '"'
						a3 = '""'
					elif sp_line[1] == '3':
						sp3_line = re.match(r'sp3(_fi|_cf)?[\t\s]+"(.*?)"[\t\s]+"(.*?)"[\t\s]+"(.*?)"', line)
						n = '3'
						a1 = '"' + sp3_line[2] + '"'
						a2 = '"' + sp3_line[3] + '"'
						a3 = '"' + sp3_line[4] + '"'

					line = 'sp_def ' + fade + ',' + n + ',' + a1 + ',' + a2 + ',' + a3 + '\n'

				elif sp0_line:
					spi = 9 - int(sp0_line[1])
					line = 'lsp ' + str(spi) + ',"cg\\' + sp0_line[2] + '.png"\n'

					if sp0_line[3] == 'FADE_SET':
						line += 'print 10 ;sp0_mode\n'
					else:
						line += 'print 1 ;sp0_mode\n'

				elif mov_line:#window誤認のため対策を
					if (mov_line[2] == '='):
						mov_line_6_ = '' if (mov_line[6] == None) else mov_line[6]

						mov_line_1_b = define_dict.get(mov_line[1])
						mov_line_3_b = define_dict.get(mov_line[3])
						mov_line_6_b = define_dict.get(mov_line_6_)

						mov_line_1_t = mov_line_1_b if (not mov_line_1_b == None) else mov_line[1]
						mov_line_3_t = mov_line_3_b if (not mov_line_3_b == None) else mov_line[3]
						mov_line_6_t = mov_line_6_b if (not mov_line_6_b == None) else mov_line_6_

						mov_line_1_r = mov_line_1_t if (re.fullmatch(r'[0-9]+?', mov_line_1_t)) else '%' + str2var_v2(mov_line_1_t, 'numalias')
						mov_line_3_r = mov_line_3_t if (re.fullmatch(r'[0-9]+?', mov_line_3_t)) else '%' + str2var_v2(mov_line_3_t, 'numalias')

						if (re.fullmatch(r'[0-9]+?', mov_line_6_t)):
							mov_line_6_r = mov_line_6_t
						elif (mov_line_6_t == ''):
							mov_line_6_r = ''
						else:
							mov_line_6_r = str2var_v2(mov_line_6_t, 'numalias')

						mov_line_5_r = mov_line[5] if (not mov_line[5] == None) else ''

						line = 'mov ' + mov_line_1_r + ',' + mov_line_3_r + mov_line_5_r + mov_line_6_r + '\n'
					else:
						print('WARNING:mov set error!')
						line = r';' + line#エラー防止の為コメントアウト

				elif movie_line:
					ext = '.mpg' if (movie_line[2] == None) else movie_line[2]
					line = 'mpegplay "' + movie_line[1] + ext + '",1\n'

				elif flash_line:
					linedef = line
					line = ''
					for s in linedef.replace('\n', '').split(' '):
						if (not s[:5] == 'flash'):
							fl_time = str( int( float(s)*1000 ) )
							line += 'lsp 11,"cg\_White.png",0,0:print 1:csp 11:print ' + effect_edit(fl_time, 'fade') + '\n'

				elif goto_line:
					line = 'goto *SCR_' + name.replace('.', '_') + '_' + goto_line[1] + '\n'

				elif at_line:
					line = '*SCR_' + name.replace('.', '_') + '_' + at_line[1] + '\n'

				elif defsel_line:
					line = 'select_set "' + defsel_line[1] + '"\n'

				elif ev1_line:#もうこれは、おべんとのイベントだ！
					line = 'vsp 15,0:vsp 16,0:vsp 17,0:vsp 10,0'
					if ev1_line[1] == '_fl':
						line += 'bg black,1:'
					
					line += 'bg "cg\\' + ev1_line[2] + '.png",10\n'
				
				elif ef2_line:
					line = 'bg "cg\\' + ef2_line[2] + '.png",' + effect_edit('100', ef2_line[1]) + '\n'

				elif shake_line:#振動(絶対原作と違う)
					if shake_line[1]=='SHAKE_1':
						line ='quake 4,200\n'
					elif shake_line[1]=='SHAKE_2':
						line ='quake 4,400\n'
					else:
						print('WARNING:shake to quake convert error!')
						line = r';' + line#エラー防止の為コメントアウト	

				elif ev_line:		
					line += 'vsp 15,0:vsp 16,0:vsp 17,0:vsp 10,0:bg "cg\\' + ev_line[2] + '.png",'
					if ev_line[2] == 'FADE_SET':
						line += '10\n'
					else:
						line += '1\n'

				elif bgm1_line:
					line = 'bgm "wav_dec\\' + bgm1_line[1] + '.wav"\n'

				elif se2_line:
					line = 'dwave 2,"wav_dec\\' + se2_line[1].replace(r'"', r'') + '.wav"\n'

				elif ( not re.search(r'[0-9A-z-_]', line) ):#英語&記号なし = セリフ
					pass
					if debug:
						line = r';' + line

				else:
					#print( line.replace('\n', '') )
					print('WARNING:not defined - ' + re.match(r'(@?[0-9A-z-_]+)',line)[1])
					line = r';' + line#エラー防止の為コメントアウト
					pass

				if debug:#選択肢動作確認のため演出系削除
					c = False
					for b in [bg_line, sp_line, sp0_line, flash_line, ev1_line, ef2_line, shake_line, bgm1_line, se2_line]:
						if b:#
							c = True
					if c:
						line = r';' + line

				txt += line

	add0txt_effect = ''
	for i,e in enumerate(effect_list,effect_startnum+1):#エフェクト定義用の配列を命令文に&置換
		if e[1] == 'fade':
			add0txt_effect +='effect '+str(i)+',10,'+e[0]+'\n'
		else:
			add0txt_effect +='effect '+str(i)+',18,'+e[0]+',"cg\\'+str(e[1]).replace('"','')+'.png"\n'

	txt = txt.replace('\n\\', '\\')#￥直前の改行を削除(pretextgosub対策)
	txt = txt.replace(r';<<-EFFECT->>', add0txt_effect)
	txt = txt.replace(r'▲氏▲', cfg_dict['Family'])
	txt = txt.replace(r'●名●', cfg_dict['Name'])

	if re.search('NijiOp', txt):#にじみて専用
		txt = txt.replace(r'<<-TITLE->>', r'虹を見つけたら教えて。')
		txt = txt.replace('\n;menu\n', '\ngoto *niji_title_menu\n*niji_title_menu_end\n')

	open(os.path.join(same_hierarchy,'0.txt'), 'w', errors='ignore').write(txt)


def file_check():
	c = True
	for p in [DIR_CG, DIR_SCR, DIR_WAV, DEFAULT_TXT]:
		if not os.path.exists(p):
			print(p+ ' is not found!')
			c = False
	
	return c


def cfg_file():
	global cfg_dict
	ini = glob.glob(os.path.join(same_hierarchy, '*.ini'))[0]
	config = configparser.ConfigParser()
	config.read(ini)
	cfg_dict['Name'] = config['User']['Name']
	cfg_dict['Family'] = config['User']['Family']


def end_check():
	# ここtrueになったらACTGS→NSCの変数名変換限界です
	# (NSC側のグローバル変数ずらせばいいだけなんだけどね...)
	if (str2var_cnt['numalias'] >= 200):
		print('WARNING:global var convert error!')

	# gosubがうまく対になってないときエラー
	if (gosub_list):
		print('WARNING:gosub convert error!')


if file_check():
	cfg_file()
	text_def()
	text_cnv()
	if not debug:
		music_cnv()
	end_check()
