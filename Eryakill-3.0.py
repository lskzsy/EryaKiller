#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Erya killer
#	@Version: 3.0
#	@Author: Lsk Skysy
#	@Email: admin@skysy.cn
#   @Finished Time: 2016.11.10
#	
#	说明：1.本脚本只负责课程时长代挂，为了防止被和谐，本脚本不提供加速观看功能
#		 2.原则上脚本自动滤过视频观看中的问题提问
#		 3.原则上脚本	自动帮忙提交每一课时的课后问题，但答案随机，不保证正确性
#		 4.鉴于第三点，请同学们认真完成期末考试（认真找答案！否则不保证期末能通过
#		 5.鉴于第一点和第二点，本脚本严格模拟正常上课行为，所以总共所需时间不曾减少，建议后台挂机使用
#		 6.建议不要连续挂，一天挂几个小时，或者一天挂几章，尽量在工作时间挂，否则容易被查出
#
#	@大天使之剑，屠龙宝刀点击就送！
#

import sys, os, platform, subprocess, time, datetime
import httplib, hashlib, json, cookielib, urllib2, urllib, re, getpass, random
from threading import Timer 

# ！全局变量
cookie = cookielib.CookieJar()         #保存cookie
cookieQuery = cookielib.CookieJar()	   #Baidu Cookie
system = platform.system()
queryBaiduCL = 15					   #检索答案的准答案个数上限
queryBaiduPage = 5					   #检索答案的准答案页面上限

global fid                             #学校ID
global fidname                         #学校名字
global userId
global opener
global queryOpener
global config
webheaders = {
	'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:51.0) Gecko/20100101 Firefox/51.0',
}

# ! 载入配置文件
def inputConfig():
	try:
		f = open('config.json', 'r')
	except IOError, e:
		f = None

	if f is None:
		return None
	config = json.loads(f.read())
	f.close()
	return config

# ！ 写入配置文件
def outputConfig(config):
	f = open('config.json', 'w+')
	f.write(json.dumps(config))
	f.close()

# ! 保存登录用户
def SaveAccount():
	global config
	if config['isSaveAcc']:
		config['isSaveAcc'] = False
		plog('已关闭保存用户功能')
	else:
		acc = raw_input('请输入您的尔雅账号:')
		config['account'] = acc
		config['isSaveAcc'] = True
		plog('已开启保存用户功能')

	outputConfig(config)
		
# ! 设置默认学校
def SaveSchool():
	global fid
	global fidname

	if config['isSaveSch']:
		config['isSaveSch'] = False
		plog('已关闭默认学校功能')
	else:
		SwitchSchool()
		config['isSaveSch'] = True
		config['fid'] = fid
		config['fidname'] = fidname
		plog('已设置默认学校')
		
	outputConfig(config)

# ! 开始执行EryaKiller
def GoErya():
	if not config['isSaveSch']:
		SwitchSchool()

	if config['isSaveAcc']:
		Login(config['account'])
	else:
		Login('')
	EryaKiller()

# ! 用户入口
def UserInterface():
	print '1. 开始观看尔雅课程'
	print '2. 完成期末考试'
	print '3. 设置默认学校'
	print '4. 开启/关闭账号保存'
	print '5. 退出'

	while True:
		sid = raw_input('请选择：')
		if sid.isdigit():
			sid = int(sid)
			
			if sid == 1:
				GoErya()
				return
			if sid == 2:
				print '还没写'
				return
			if sid == 3:
				SaveSchool()
				return
			if sid == 4:
				SaveAccount()
				return
			if sid == 5:
				exit()
	
		print '无效输入!'

def QuerySchool(School):
	url = 'https://passport2.chaoxing.com/org/searchforms'
	postdata = {
		'allowjoin' : '0',
		'filter' : School,
		'pid' : '-1'
	}
	postdata = urllib.urlencode(postdata)
	req = urllib2.Request(url=url, data=postdata, headers=webheaders)
	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + e.reason)
		return QuerySchool(School)
	except:
		return QuerySchool(School)

	return json.loads(resp.read())

# ! 学校选择器
def SwitchSchool():
	global fid
	global fidname
	school = raw_input('请输入您的学校：')
	schools = QuerySchool(school)
	if not schools['result']:
		print '当前学校查无结果,请重新确认!'
		return SwitchSchool()

	i = 1
	line = ''
	for s in schools['froms']:
		print str(i) + '.' + s['name']
		i += 1
					

	while True:
		sid = raw_input('请选择您的学校(输入0为重新输入：')
		if sid.isdigit():
			sid = int(sid)
			#print sid
			if sid == 0:
				return SwitchSchool()		
			if sid < schools['fromNums']:
				plog('已选择学校为' + schools['froms'][sid - 1]['name'].encode('utf-8'))
				fid = str(schools['froms'][sid - 1]['id'])
				fidname = schools['froms'][sid - 1]['name'].encode('utf-8')
				break
	
		print '无效输入!'
 

# ! 完成课后作业（PP考试网大法
def FinishTestWorkByPPK(problem):
	plog('正在检索PPK考试网!')
	on = ''
	url = 'http://s.ppkao.com/cse/search?q=' + urllib.quote(problem) + '&click=1&s=7348154799869824824&nsid='
	req = urllib2.Request(url=url, headers=webheaders)
	#print url
	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		if str(e.reason).find('redirect error') != -1:
			return ''
		return FinishTestWorkByPPK(problem)
	except:
		return FinishTestWorkByPPK(problem)

	inner = resp.read()
	inner = inner.replace('\n', '')
	inner = inner.replace('\r', '')
	inner = inner.replace(' ', '')
	inner = inner.replace('\t', '')
	problem = problem.replace('，', '')
	problem = problem.replace('（', '')
	problem = problem.replace('）', '')
	problem = problem.replace('。', '')
	problem = problem.replace('、', '')
	problem = problem.replace(' ', '')

	inner = inner.replace('，', '')
	inner = inner.replace('（', '')
	inner = inner.replace('）', '')
	inner = inner.replace('。', '')
	inner = inner.replace(',', '')
	inner = inner.replace('(', '')
	inner = inner.replace(')', '')
	inner = inner.replace('、', '')
	inner = inner.replace('<em>', '')
	inner = inner.replace('</em>', '')
	inner = inner.replace(' ', '')


	title = SplitStr(inner, 'c-title', '</h3>')
	for t in title:
		if t.find(problem) != -1:
			on = t
			break

	if on == '':
		content = SplitStr(inner, 'c-abstract', '</div>')
		for i in xrange(0, len(content)):
			if content[i].find(problem) != -1:
				on = SplitStr(title[i], 'href="', '"')

				req = urllib2.Request(url=on[0], headers=webheaders)
				#print on[0]
				on = ''
				try:
					resp = urllib2.urlopen(req)
				except urllib2.URLError, e:
					plog('ERROR' + str(e.reason))
					return FinishTestWorkByPPK(problem)
				except:
					return FinishTestWorkByPPK(problem)
				try:
					inner = resp.read().decode('gb2312').encode('utf-8')
				except UnicodeDecodeError, e:
					plog('字符解码错误！')

				inner = inner.replace('\n', '')
				inner = inner.replace('\r', '')
				inner = inner.replace(' ', '')
				inner = inner.replace('\t', '')

				inner = inner.replace('，', '')
				inner = inner.replace('（', '')
				inner = inner.replace('）', '')
				inner = inner.replace('。', '')
				inner = inner.replace(',', '')
				inner = inner.replace('(', '')
				inner = inner.replace(')', '')
				inner = inner.replace('、', '')
				inner = inner.replace('<em>', '')
				inner = inner.replace('</em>', '')
				inner = inner.replace(' ', '')

				nn = SplitStr(inner, 'single-siticlearfix', '</div>')
				#print nn
				ll = SplitStr(inner, 'practice/?id=', '\'')
				if len(ll) < 1:
					return ''
				#print ll
				for i in xrange(0, len(nn)):
					if nn[i].find(problem) != -1:
						on = 'shiti/' + ll[i] + '.'
						break
				break

		if on == '':
			return ''

	on = SplitStr(on, 'shiti/', '.')
	if len(on) < 1:
		return ''	

	url = 'http://user.ppkao.com/mnkc/tiku/?id=' + on[0]
	#print url
	req = urllib2.Request(url=url, headers=webheaders)
	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return FinishTestWorkByPPK(problem)
	except:
		return FinishTestWorkByPPK(problem)

	#print resp.read()
	try:
		inner = resp.read().decode('gb2312').encode('utf-8')
	except UnicodeDecodeError, e:
		plog('编码存在错误！')

	inner = inner.replace('\n', '')
	inner = inner.replace('\r', '')
	inner = inner.replace(' ', '')
	inner = inner.replace('\t', '')

	on = SplitStr(inner, '参考答案：', '<')
	if len(on) < 1:
		return ''
	on[0] = on[0].replace('对', 'true')
	on[0] = on[0].replace('错', 'false')
	return on[0]

# ! 随机生成答案算法
def RandomAns(type):
	plog('随机生成答案中!')
	if type == 0:
		t = random.randint(0, 3)
		return chr(ord('A') + t)
	elif type == 3:
		t = random.randint(0, 1)
		if t == 0:
			return 'false'
		else:
			return 'true'

# ！排序
def SortAns(tt):
	dirr = 0
	minn = tt[0]
	for i in xrange(0, len(tt)):
		if tt[i] < minn:
			minn = tt[i]
			dirr = i
	return (dirr, minn)

# ! 检索算法
def QueryCore(inner, problem, type):
	if not (type == 0 or type == 3):
		return ''

	a = 0
	b = 0
	c = 0
	d = 0
	tr = 0
	fa = 0

	problemFound = False
	keywordFound = False

	problem = problem.replace('，', '')
	problem = problem.replace('（', '')
	problem = problem.replace('）', '')
	problem = problem.replace('。', '')
	problem = problem.replace('、', '')
	problem = problem.replace(' ', '')

	inner = inner.replace('，', '')
	inner = inner.replace('（', '')
	inner = inner.replace('）', '')
	inner = inner.replace('。', '')
	inner = inner.replace(',', '')
	inner = inner.replace('(', '')
	inner = inner.replace(')', '')
	inner = inner.replace('、', '')
	inner = inner.replace('<em>', '')
	inner = inner.replace('</em>', '')
	inner = inner.replace(' ', '')

	keyword = '正确答案'
	title = 'spantitle="'
	answord = [['A', 'B', 'C', 'D'], [], [], ['√', '×']];
	answord = answord[type]

	off = inner.find(title)
	inner = inner[off+len(title): ]

	while True:
		tt = []
		pdir = inner.find(problem)
		kdir = inner.find(keyword)
		tdir = inner.find(title)
		for t in answord:
			tt.append(inner.find(t))

		if (not problemFound) and pdir != -1:
			if kdir != -1 and kdir < pdir:
				inner = inner[kdir + len(keyword): ]
				continue

			inner = inner[pdir + len(problem): ]
			problemFound = True
			continue

		if (not keywordFound) and kdir != -1:
			if tdir != -1 and kdir > tdir:
				problemFound = False
				inner = inner[tdir + len(title): ]
				continue

			keywordFound = True
			inner = inner[kdir + len(keyword): ]
			continue

		mt, mtdir = SortAns(tt)
		if tdir != -1 and mtdir > tdir:
			problemFound = False
			keywordFound = False
			inner = inner[tdir + len(title): ]
			continue

		if mtdir != -1 and keywordFound and problemFound:
			if type == 0:
				if mt == 0:
					a += 1
				elif mt == 1:
					b += 1
				elif mt == 2:
					c += 1
				elif mt == 3:
					d += 1
			elif type == 3:
				if mt == 0:
					tr += 1
				elif mt == 1:
					fa += 1
			keywordFound = False
			problemFound = False
			inner = inner[mtdir + len(answord[mt]): ]
			continue

		break

	#print fa, tr

	if type == 0:
		if a > b and a > c and a > d:
			return 'A'
		if b > a and b > c and b > d:
			return 'B'
		if c > a and c > b and c > d:
			return 'C'
		if d > a and d > b and d > c:
			return 'D'
		return ''
	elif type == 3:
		if fa > tr:
			return 'false'
		if tr > fa:
			return 'true'
		return ''



# ! 完成课后作业（检索百度方法
def FinishTestWorkByBaidu(problem):
	queryUrl = 'http://wenku.baidu.com/search?org=0&word='	
	headers = dict.copy(webheaders)
	ret = []

	#初始化报头
	headers['Host'] = 'wenku.baidu.com'

	for i in xrange(0, len(problem['text'])):
		ans = ''
		ans = FinishTestWorkByPPK(problem['text'][i])
		if not ans in '':
			#print 'xxxxxx'
			ret.append(ans)
			continue

		plog('正在检索百度文库!')
		inn = ''
		'''
		if len(problem['text'][i]) > 24:
			dirr = problem['text'][i].rfind('，')
			if dirr != -1:
				problem['text'][i] = problem['text'][i][dirr + 1: ]
		problem['text'][i] = problem['text'][i].encode('utf-8')
		'''
		url = queryUrl + urllib.quote(problem['text'][i].decode('utf-8').encode('gbk'))

		j = 0
		while j < 4:
			req = urllib2.Request(url=url + '&pn=' + str(j*10), headers=headers)
			try:
				resp = urllib2.urlopen(req)
				inner = resp.read().decode('gbk').encode('utf-8')
				inner = inner.replace('\n', '')
				inner = inner.replace('\r', '')
				inner = inner.replace(' ', '')
				inner = inner.replace('\t', '')
				inn += inner
				j += 1
			except urllib2.URLError, e:
				plog('ERROR' + str(e.reason))
			except:
				return

		ans = QueryCore(inn, problem['text'][i], problem['type'][i])
		if ans in '':
			ans = RandomAns(problem['type'][i])
		ret.append(ans)
		#print problem['type'][i], ans
	
	problem['answer'] = ret

	return problem
		
# ! 获取某个字符串值的方法
def SplitStr(inner, prev, next):
	ans = []
	while True:
		off = inner.find(prev)
		if off == -1:
			break
		off += len(prev)
		end = inner.find(next, off)
		ans.append(inner[off : end])
		inner = inner[end :]

	return ans

# ！获取课后作业的成绩的相关参数
def GetScoreArg(cid, clazzid, courseid, jobid, workid, utenc ,enc):
	url = 'https://mooc1-2.chaoxing.com/api/work?api=1&workId=' + workid
	url += '&jobid=' + jobid
	url += '&needRedirect=true'
	url += '&knowledgeid=' + cid
	url += '&ut=s'
	url += '&clazzId=' + clazzid
	url += '&type='
	url += '&enc=' + enc
	url += '&utenc=' + utenc
	url += '&courseid=' + courseid

	req = urllib2.Request(
		url=url,
		headers=webheaders
		)
	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return GetScoreArg(cid, clazzid, courseid, jobid, workid, utenc ,enc)
	except:
		return GetScoreArg(cid, clazzid, courseid, jobid, workid, utenc ,enc)
	
	inner = resp.read()
	inner = inner.replace('\n', '')
	inner = inner.replace('\r', '')
	inner = inner.replace(' ', '')
	inner = inner.replace('\t', '')

	score = SplitStr(inner, '成绩：<spanstyle="color:#db2727;">', '<')
	return score[0]

# ! 获取课后作业的相关参数
def GetWorKArg(clazzid, courseid, cid, tabnum):
	url = 'https://mooc1-2.chaoxing.com/knowledge/cards?clazzid=' + clazzid + '&courseid=' + courseid + '&knowledgeid=' + cid + '&num=' + str(tabnum - 1) + '&v=20160407-1'
	#print url
	req = urllib2.Request(
		url=url,
		headers=webheaders
		)
	jobid = ''
	workid = ''
	enc = ''

	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return GetWorKArg(clazzid, courseid, cid, tabnum)
	except:
		return GetWorKArg(clazzid, courseid, cid, tabnum)

	inner = resp.read()
	inner = inner.replace('\n', '')
	inner = inner.replace('\r', '')
	inner = inner.replace(' ', '')
	inner = inner.replace('\t', '')

	argJson = SplitStr(inner, 'mArg=', ';')
	args = json.loads(argJson[1])
	jobid = args['attachments'][0]['jobid']
	workid = args['attachments'][0]['property']['workid']
	enc = args['attachments'][0]['enc']

	if not 'work-' + str(workid) in jobid:
		workid = jobid[5: ] 

	return (jobid, workid, enc)

# ! 获取课后作业关键参数utenc
def GetUtenc(cid, courseid, clazzid, enc):
	url = 'https://mooc1-2.chaoxing.com/mycourse/studentstudy?chapterId=' + cid + '&courseId=' + courseid + '&clazzid=' + clazzid + '&enc=' + enc
	req = urllib2.Request(
		url=url,
		headers=webheaders
		)
	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return GetUtenc(cid, courseid, clazzid, enc)
	except:
		return GetUtenc(cid, courseid, clazzid, enc)

	inner = resp.read()
	inner = inner.replace('\n', '')
	inner = inner.replace('\r', '')
	inner = inner.replace(' ', '')
	inner = inner.replace('\t', '')

	utenc = SplitStr(inner, 'utEnc="', '"')
	return utenc[0]


# ! 获取课后作业的题号以及题型
def GetTestProblem(cid, clazzid, courseid, jobid, workid, utenc ,enc):
	url = 'https://mooc1-2.chaoxing.com/api/work?api=1&workId=' + str(workid)
	url += '&jobid=' + jobid
	url += '&needRedirect=true'
	url += '&knowledgeid=' + cid
	url += '&ut=s'
	url += '&clazzId=' + clazzid
	url += '&type='
	url += '&enc=' + enc
	url += '&utenc=' + utenc
	url += '&courseid=' + courseid

	total = ''
	workrid = ''
	token = ''
	problemId = ''
	problemType = []
	problemText = []

	req = urllib2.Request(
		url=url,
		headers=webheaders
		)
	#print url
	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return GetTestProblem(cid, clazzid, courseid, jobid, workid, utenc ,enc)
	except:
		return GetTestProblem(cid, clazzid, courseid, jobid, workid, utenc ,enc)
	
	inner = resp.read()
	inner = inner.replace('\n', '')
	inner = inner.replace('\r', '')
	inner = inner.replace(' ', '')
	inner = inner.replace('\t', '')

	total = SplitStr(inner, 'totalQuestionNum"value="', '"')
	workrid = SplitStr(inner, 'workRelationId"value="', '"')
	token = SplitStr(inner, 'enc_work"value="', '"')

	problemId = SplitStr(inner, 'a="', '"')
	problemId = problemId[0].split(',')

	for p in problemId:
		if p != '':
			t = SplitStr(inner, 'name="answertype' + p + '"value="', '"')
			problemType.append(int(t[0]))

	problemText = SplitStr(inner, '】', '<')

	problem = {'id' : problemId, 'type' : problemType, 'text' : problemText}
	return (total[0], workrid[0], token[0], problem)
'''
# ! 完成课后作业
def FinishTestWork(problem):
	ret = []

	#偷懒写法之一，考试宝典告诉我们C的可能性最大
	#根据尔雅的代码，还会存在连线题，简单题，完型填空诸如此类，因为作者没见过，所以一律返空
	for t in problem['type']:
		if t == 0:
			ret.append('C')
		elif t == 3:
			ret.append('true')
		else:
			ret.append('_')
	problem['answer'] = ret
	
	return problem
'''

# ! 提交课后作业的答案
def PostTestAnswer(clazzid, courseid, token, total, cid, workid, jobid, workrid, problem):
	url = 'https://mooc1-2.chaoxing.com/work/addStudentWorkNewWeb?_classId=' + clazzid + '&courseid=' + courseid + '&token=' + token
	postdata = {
		'pyFlag' : '',
		'courseId' : courseid,
		'classId' : clazzid,
		'api' : '1',
		'workAnswerId' : '',
		'totalQuestionNum' : total,
		'fullScore' : '100.0',
		'knowledgeid' : cid,
		'oldSchoolId' : '',
		'oldWorkId' : workid,
		'jobid' : jobid,
		'workRelationId' : workrid,
		'enc' : '',
		'enc_work' : token
	}

	for i in xrange(0, len(problem['type'])):
		postdata['answer' + problem['id'][i]] = problem['answer'][i]
		postdata['answertype' + problem['id'][i]] = str(problem['type'][i])
	postdata['answerwqbid'] = ','.join(problem['id'])
	postdata = urllib.urlencode(postdata)
	req = urllib2.Request(url, postdata, webheaders)
	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return PostTestAnswer(clazzid, courseid, token, total, cid, workid, jobid, workrid, problem)
	except:
		return PostTestAnswer(clazzid, courseid, token, total, cid, workid, jobid, workrid, problem)

	return resp.code == 200


# ! 关键参数ENC生成函数
def NewEnc(clazzId, jobId, objectId, playTime, duration, clipTime):
	global userId
	salt = '[d_yHJ!$pdA~5]'
	mm = hashlib.md5()
	mm.update('[' + clazzId + ']' +'[' + userId + ']' +'[' + jobId + ']' +'[' + objectId + ']' +'[' + str(playTime * 1000) + ']' 
		+ salt + '[' + str(duration * 1000) + ']' + '[' + clipTime + ']')
	#print clazzId, userId, jobId, objectId, playTime, duration, clipTime
	#print mm.hexdigest()
	return str(mm.hexdigest())

# ! 获取看视频时问题
def GetProblemForWatching(mid):
	url = 'https://mooc1-2.chaoxing.com/richvideo/initdatawithviewer?&start=undefined&mid=' + mid
	problemId = ''
	answer = ''
	proTime = 0
	req = urllib2.Request(
		url=url,
		headers=webheaders
		)
	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return GetProblemForWatching(mid)
	except:
		return GetProblemForWatching(mid)

	ans = json.loads(resp.read())
	problemId = str(ans[0]['datas'][0]['resourceId'])
	if ans[0]['datas'][0]['options'][0]['isRight']:
		answer = 'A'
	else:
		answer = 'B'
	proTime = ans[0]['datas'][0]['startTime']
	return (problemId, answer, proTime)

# ! 发送看视频时问题答案
def PostAnswerForWProblem(problemId, answer):
	url = 'https://mooc1-2.chaoxing.com/richvideo/qv?resourceid=' + problemId + '&answer=' + '\'' + answer + '\''
	req = urllib2.Request(
		url=url,
		headers=webheaders
		)
	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		PostAnswerForWProblem(problemId, answer)
	except:
		PostAnswerForWProblem(problemId, answer)


# ! 校验时长用的请求（不允许大幅度跳时，服务端有做检测
def PostJudgeRequest(dtoken, duration, objectid, clazzid, otherinfo, jobid, playtime):
	global userId
	url = 'https://mooc1-2.chaoxing.com/multimedia/log/' + dtoken
	url += '?duration=' + str(duration)
	url += '&objectId=' + objectid
	url += '&clazzId=' + clazzid
	url += '&clipTime=' + '0_' + str(duration)
	url += '&otherInfo=' + otherinfo
	url += '&dtype=Video'
	url += '&userid=' + userId
	url += '&rt=0.9'
	url += '&jobid=' + jobid
	url += '&view=pc'
	url += '&playingTime=' + str(playtime)
	url += '&isdrag=3'
	url += '&enc=' + NewEnc(clazzid, jobid, objectid, playtime, duration, '0_' + str(duration))
	#print url

	headers = dict.copy(webheaders)
	headers['Host'] = 'mooc1-2.chaoxing.com'
	headers['Referer'] = 'https://mooc1-2.chaoxing.com/ananas/modules/video/index.html?v=20150402'
	req = urllib2.Request(
		url=url,
		headers=headers
		)
	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return PostJudgeRequest(dtoken, duration, objectid, clazzid, otherinfo, jobid, playtime)
	except:
		return PostJudgeRequest(dtoken, duration, objectid, clazzid, otherinfo, jobid, playtime)

	ans = json.loads(resp.read())
	return ans['isPassed']

# ! 每一课时的结束包
def PostEndRequest(dtoken, duration, objectid, clazzid, otherinfo, jobid, playtime):
	global userId
	url = 'https://mooc1-2.chaoxing.com/multimedia/log/' + dtoken
	url += '?duration=' + str(duration)
	url += '&objectId=' + objectid
	url += '&clazzId=' + clazzid
	url += '&clipTime=' + '0_' + str(duration)
	url += '&otherInfo=' + otherinfo
	url += '&dtype=Video'
	url += '&userid=' + userId
	url += '&rt=0.9'
	url += '&jobid=' + jobid
	url += '&view=pc'
	url += '&playingTime=' + str(playtime)
	url += '&isdrag=4'
	url += '&enc=' + NewEnc(clazzid, jobid, objectid, playtime, duration, '0_' + str(duration))
	#print url

	headers = webheaders
	headers['Host'] = 'mooc1-2.chaoxing.com'
	headers['Referer'] = 'https://mooc1-2.chaoxing.com/ananas/modules/video/index.html?v=20150402'
	req = urllib2.Request(
		url=url,
		headers=headers
		)
	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return PostEndRequest(dtoken, duration, objectid, clazzid, otherinfo, jobid, playtime)
	except:
		return PostEndRequest(dtoken, duration, objectid, clazzid, otherinfo, jobid, playtime)

	ans = json.loads(resp.read())
	return ans['isPassed']

def GetDuration(oid):
	dur = ''
	dtoken = ''
	url = 'https://mooc1-2.chaoxing.com/ananas/status/' + oid + '?k=' + fid + '&_dc=' + LocalTimeStamp()
	req = urllib2.Request(
		url=url,
		headers=webheaders
		)

	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return GetDuration(oid)
	except:
		return GetDuration(oid)

	inner = resp.read()
	#print inner
	data = json.loads(inner)
	if not data['duration'] is None:
		dur = data['duration']
		dtoken = data['dtoken']
	return (dur, dtoken)

# ! 获取视频的ObjectId
def GetObjectId(courseid, clazzid, cid, tabnum):
	url = 'https://mooc1-2.chaoxing.com/knowledge/cards?clazzid=' + clazzid + '&courseid=' + courseid + '&knowledgeid=' + cid + '&num=' + str(tabnum - 2) + '&v=20160407-1'
	matchOid = re.compile(r'''.*data="{&quot;objectid&quot;:&quot;(?P<oid>.*)&quot;,&quot;name''')
	matchCInf = re.compile(r'''.*mArg=(?P<inf>.*);}catch''')
	#matchMid = re.compile(r'''.*"mid":"(?P<mid>.*)","type":".mp4"''')
	oid = ''
	begin = 0
	jobId = ''
	isPassed = False
	otherInfo = ''
	mid = ''
	req = urllib2.Request(
		url=url,
		headers=webheaders
		)

	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return GetObjectId(courseid, clazzid, cid, tabnum)
	except:
		return GetObjectId(courseid, clazzid, cid, tabnum)

	inner = resp.read()
	inner = inner.replace('\n', '')
	inner = inner.replace('\r', '')
	inner = inner.replace(' ', '')
	inner = inner.replace('\t', '')
	m = matchOid.match(inner)
	if not m is None:
		oid = m.group('oid')
		#print 'xxxxx'
	m = matchCInf.match(inner)
	if not m is None:
		data = json.loads(m.group('inf'))
	if data['attachments'][0].has_key('headOffset'):
		begin = data['attachments'][0]['headOffset']
	if data['attachments'][0].has_key('jobid'):
		jobId = data['attachments'][0]['jobid']
	if data['attachments'][0].has_key('otherInfo'):
		otherInfo = data['attachments'][0]['otherInfo']
	if data['attachments'][0].has_key('isPassed'):
		isPassed = data['attachments'][0]['isPassed']
	if data['attachments'][0].has_key('mid'):
		mid = data['attachments'][0]['mid']
	if data['attachments'][0].has_key('objectid'):
		oid = data['attachments'][0]['objectid']

	return (oid, begin, jobId, isPassed, otherInfo, mid)

# ! 获取TabNum
def GetTabNum(courseid, clazzid, cid):
	url = 'https://mooc1-2.chaoxing.com/mycourse/studentstudyAjax'
	postdata = {
		'courseId' : courseid,
		'clazzid' : clazzid,
		'chapterId' : cid
	}
	tabnum = 0
	postdata = urllib.urlencode(postdata)
	req = urllib2.Request(url, postdata, webheaders)
	try:
		resp = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return GetTabNum(courseid, clazzid, cid)
	except:
		return GetTabNum(courseid, clazzid, cid)

	inner = resp.read()
	inner = inner.replace('\n', '')
	inner = inner.replace('\r', '')
	inner = inner.replace(' ', '')
	inner = inner.replace('\t', '')
	tabnum = SplitStr(inner, 'PCount.previous(\'', '\'')

	return int(tabnum[0])


# ! 获取课程章节列表，判断当前需要观看的章节
def GetOrangeChapter(courseid, clazzid, enc):
	url = 'https://mooc1-2.chaoxing.com/mycourse/studentcourse?courseId=' + courseid + '&clazzid=' + clazzid + '&enc=' + enc
	matchChapter = re.compile(r'''.*<emclass="orange">\d</em></span><spanclass="articlename"><ahref='/mycourse/studentstudy\?chapterId=(?P<cid>.*)&courseId=\d+&clazzid=\d+&enc=.*'title="(?P<cname>.*)">(?P=cname)</a></span></h3>''')
	cid = ''
	cname = ''
	req = urllib2.Request(
		url=url,
		headers=webheaders
		)
	try:
		resq = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return GetOrangeChapter(courseid, clazzid, enc)
	except:
		return GetOrangeChapter(courseid, clazzid, enc)


	inner = resq.read()
	inner = inner.replace('\n', '')
	inner = inner.replace('\r', '')
	inner = inner.replace(' ', '')
	inner = inner.replace('\t', '')
	m = matchChapter.match(inner)
	if not m is None:
		cid = m.group('cid')
		cname = m.group('cname')
	#print cid, cname
	return (cid, cname)

# ! 发送登录请求
def PostLoginRequest(account, password, numcode):
	global fid
	global fidname
	posturl = 'https://passport2.chaoxing.com/login?refer=http://i.mooc.chaoxing.com'
	postdata = {
		'refer_0x001' : 'http://i.mooc.chaoxing.com',
		'pid' : '-1',
		'pidName' : '',
		'fid' : fid,
		'fidName' : fidname,
		'allowJoin' : '0',
		'isCheckNumCode' : '1',
		'f' : '0',
		'productid' : '',
		'uname' : account,
		'password' : password,
		'numcode' : numcode,
		'verCode' : ''
	}

	postdata = urllib.urlencode(postdata)
	req = urllib2.Request(posturl, postdata, webheaders)
	try:
		ans = urllib2.urlopen(req)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return PostLoginRequest(account, password, numcode)
	except:
		return PostLoginRequest(account, password, numcode)
	return ans

# ！获取当前UNIX时间
def LocalTimeStamp():
	t = time.mktime(datetime.datetime.now().timetuple()) * 1000
	return str(long(t))

# ！回显Log
def plog(inner):
	if inner[: 5] in 'ERROR':
		time.sleep(10)
	print '[' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ']' + '：' + inner

# ！验证码
def GetNumCode():
	url = "https://passport2.chaoxing.com/num/code?" + LocalTimeStamp()
	try:
		resq = urllib2.urlopen(url)
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return GetNumCode()
	except:
		return GetNumCode()

	f = file('verImg.png', 'wb')
	f.write(resq.read())
	f.close()

	#偷懒写法之一，因为本脚本尽量使用python27自带的原生库，所以验证码显示交给系统处理
	#如果放在linux服务器上挂的，自己想办法过验证码吧
	if system in 'Darwin':
		subprocess.call(['open', 'verImg.png'])
	elif system in 'Windows':
		os.startfile('verImg.png')
	else:
		subprocess.call(['xdg-open', 'verImg.png'])

	return raw_input('请输入验证码(输入0，刷新验证码:')

# ！获取课程
def GetCourse():
	enc = ''
	courseId = ''
	clazzid = ''
	name = ''
	courses = []
	url = 'http://mooc1-2.chaoxing.com/visit/courses'
	matchCourse = re.compile(r'''studentcourse\?courseId=(?P<courseid>\d+)&clazzid=(?P<clazzid>\d+)&enc=(?P<enc>\w+)'target="_blank"title="(?P<name>\W+)">(?P=name)''')
	try:
		req = urllib2.Request(
			url=url,
			headers=webheaders
			)
		resq = urllib2.urlopen(req)
		inner = resq.read()
		inner = inner.replace('\n', '')
		inner = inner.replace('\r', '')
		inner = inner.replace(' ', '')
		inner = inner.replace('\t', '')
		m = matchCourse.findall(inner)
		courses = m
		'''
				courseId = mm.group('courseid')
				clazzid = mm.group('clazzid')
				enc = mm.group('enc')
				name = mm.group('name')
				courses.append((courseId, clazzid, enc, name))
				'''
				#print 'xxxxx'
	except urllib2.URLError, e:
		plog('ERROR' + str(e.reason))
		return GetCourse()
	except:
		return GetCourse()

	#print courses
	#print courseId,clazzid,enc
	return courses

# ! 登录
def Login(account):
	global userId
	numcode = 0
	m = ''
	matchError = re.compile(r'.*show_error">(?P<error>.*)&nbsp;</td><td>&nbsp;</td>', re.I | re.M)

	if account == '':
		account = raw_input('请输入您的尔雅账号:')
	password = getpass.getpass('请输入您的尔雅密码:')
	while int(numcode) == 0:
		numcode = GetNumCode()
	
	resp = PostLoginRequest(account, password, numcode)
	if resp.code == 200:
		inner = resp.read()
		inner = inner.replace('\n', '')
		inner = inner.replace('\r', '')
		inner = inner.replace(' ', '')
		inner = inner.replace('\t', '')
		m = matchError.match(inner)
		#print inner
		if not m is None:
			plog(m.group('error')) 
			return Login(account)
		else:
			plog('登录成功!')
			for item in cookie:
				#print item.name, item.value
				if item.name in 'UID':
					userId = item.value
					#print 'xxx'
					break
	elif resp.code == 302:
			plog('登录成功!')
	return 0

# ! 初始化
def Init():
	global opener
	global queryOpener
	global fid
	global fidname
	global config

	iconfig = inputConfig()
	if iconfig:
		config = iconfig
	else:
		oconfig = {
			'account' : '',
			'password' : '',
			'fid' : '',
			'fidname' : '',
			'isSaveAcc' : False,
			'isSaveSch' : False
		}
		outputConfig(oconfig)
		config = oconfig

	fid = config['fid']
	fidname = config['fidname'].encode('utf-8')
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
	queryOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieQuery))
	urllib2.install_opener(opener)
	plog('初始化参数成功!')

# ！尔雅观看主函数
def EryaKiller():
	nowc = 0

	while True:
		#获取当前需要看的章节
		courses = GetCourse()
		courseid, clazzid, enc, name = courses[nowc]
		if enc in '':
			plog('获取课程失败!')
		else:
			plog('获取课程成功!->' + name)

		cid, cname = GetOrangeChapter(courseid, clazzid, enc)
		if cid in '':
			plog('当前课程没有需要完成的章节!')
			if nowc < len(courses):
				nowc += 1
				continue
			else:
				break
		else:
			plog('获取当前需要观看的章节成功!->' + cname)

		utenc = GetUtenc(cid, courseid, clazzid, enc)
		tabnum = GetTabNum(courseid, clazzid, cid)
		#print utenc

		#初始化验证包需要的参数
		oid, begin, jobId, isPassed, otherInfo, mid = GetObjectId(courseid, clazzid, cid, tabnum)
	
		if oid in '':
			plog('获取当前章节的Objectid失败!')
		else:
			plog('获取当前章节的Objectid成功!')
		#print begin

		dur, dtoken = GetDuration(oid)

		plog('开始观看【' + name + '-' + cname + '】')

		problemId, pans, proTime = GetProblemForWatching(mid)
		#print problemId, pans
		proFlag = True
		nowtime = int(begin) / 1000
		if nowtime > proTime:
			proFlag = False
		PostJudgeRequest(dtoken, dur, oid, clazzid, otherInfo, jobId, 0)
		while True:
			if nowtime >= dur:
				PostJudgeRequest(dtoken, dur, oid, clazzid, otherInfo, jobId, dur)
				if PostEndRequest(dtoken, dur, oid, clazzid, otherInfo, jobId, dur):
					break

			if nowtime >= proTime and proFlag:
				time.sleep(5)
				PostAnswerForWProblem(problemId, pans)
				nowtime = proTime
				proFlag = False
				PostJudgeRequest(dtoken, dur, oid, clazzid, otherInfo, jobId, nowtime)
				plog('【' + name + '-' + cname + '-' + str(nowtime) + 'S】' + '已回答视频弹出问题')
				nowtime += 180
				time.sleep(180)
				continue

			if PostJudgeRequest(dtoken, dur, oid, clazzid, otherInfo, jobId, nowtime):
				break
			plog('正在观看【' + name + '-' + cname + '-' + str(nowtime) + 'S】')
			time.sleep(180)
			nowtime += 180

		plog('完成观看【' + name + '-' + cname + '】')

		#开始完成课后作业
		#获取作业相关参数
		jobId, workId, enc = GetWorKArg(clazzid, courseid, cid, tabnum)
		plog('获取【' + name + '-' + cname + '】课后作业相关参数！')

		#获取作业题目
		total, workrid, token, problem = GetTestProblem(cid, clazzid, courseid, jobId, workId, utenc ,enc)
		plog('获取【' + name + '-' + cname + '】课后作业成功！')

		#完成作业（百度文库大法，太长的问题走随机数
		problem = FinishTestWorkByBaidu(problem)
		#print problem
		#break
		'''
		#完成作业（暂时采用固定答案，正确率大概只有25%
		problem = FinishTestWork(problem)
		'''
		#提交作业答案
		if PostTestAnswer(clazzid, courseid, token, total, cid, workId, jobId, workrid, problem):
			plog('提交【' + name + '-' + cname + '】课后作业成功！')

		time.sleep(5)
		score = GetScoreArg(cid, clazzid, courseid, jobId, workId, utenc ,enc)
		plog('【' + name + '-' + cname + '】课后作业的成绩是:' + score)
		


# ！脚本入口函数
if __name__ == "__main__":
	Init()
	while True:
		UserInterface()

