#!/usr/bin/python3
import urllib.parse
import urllib.request
import sys
import execjs
"""
Name:PySyuf
Description: Simpler Youtube URL Fetcher
Version:0.1
Code: danielchc
Last edit: 10/03/2018
"""

"""Start decipher"""
def getPlayerInfoById(videoID):
	try:
		pinfo = urllib.request.urlopen('https://www.youtube.com/watch?v={}'.format(videoID))
		data = str(pinfo.read())
		playerid = data.split('/yts/jsbin/player-')
		return playerid[1].split('"')[0]
	except:
		print('Error getting player URL')
		sys.exit(1)


def decipherFunction(decipherScript):
		signatureCall = decipherScript.split('||"signature",')
		signatureLen = len(signatureCall)
		signatureFunction = ''
		for i in range(signatureLen-1,0,-1):
			signatureCall[i]=signatureCall[i].split(');')[0]
			if signatureCall[i].find('(') != -1:
				signatureFunction = signatureCall[i].split('(')[0];
				break
			else:
				print('Error getting signature function')
				sys.exit(1)
				
		decipherPatterns = decipherScript.split(signatureFunction + '=function(')[1]
		decipherPatterns = decipherPatterns.split('}')[0]
		deciphers = decipherPatterns.split('(a')
		for i in range(len(deciphers)):
			deciphers[i] = deciphers[i].split(';')[1].split('.')[0]
			if len(decipherPatterns.split(deciphers[i])) >= 2:
				deciphers = deciphers[i]
				break
			else:
				print('Failed to get deciphers function')
				sys.exit(1)
		decipher = decipherScript.split(deciphers+'={')[1]
		decipher = decipher.replace('\\n','').replace('\\r','')
		decipher = decipher.split('}}')[0]

		sFunc = 'var ' + deciphers + '={' + decipher + ';}}; '
		mFunc = 'main=function(' + decipherPatterns + ';}; '
		deJS = execjs.compile(sFunc + mFunc)
		return deJS
"""Ends decipher"""

def streamURL(afmts):
	streams = {}
	info = {}
	fmtsl = afmts.split(',')
	for i in fmtsl:
		var = i.split('&')
		for v1 in var:
			inf = v1.split('=')
			info[inf[0]] = inf[1]
		streams[info['itag']] = info.copy()
		info.clear()
	return streams


def qsToJson(qs):
	res = {}
	pars = qs.split('&')
	for i in pars:
		dic = i.split('=')
		res[dic[0]] = urllib.parse.unquote(dic[1])
	return res


def main(video_id):
	response = urllib.request.urlopen('https://www.youtube.com/get_video_info?video_id={}&asv=3&el=detailpage&hl=en_US'.format(video_id))
	out = str(response.read())
	jsonOutput = qsToJson(out)
	if 'url_encoded_fmt_stream_map' in jsonOutput:
		url_encoded_fmt_stream_map=streamURL(jsonOutput['url_encoded_fmt_stream_map'])
		adaptive_fmts=streamURL(jsonOutput['adaptive_fmts'])
	else:
		print('Error!!!')
		print('Caused by ' + out)
		sys.exit(1)
		
	if 's' in next(iter(adaptive_fmts.values())):
		decipherPlayer = urllib.request.urlopen('https://youtube.com/yts/jsbin/player-{}'.format(getPlayerInfoById(video_id)))
		decipherScript = str(decipherPlayer.read())
		sigDep = decipherFunction(decipherScript)

	print('===================url_encoded_fmt_stream_map===========================')

	for i, a in url_encoded_fmt_stream_map.items():
		print('----------------------------------------------')
		print('Itag: ' + i)
		print('Type: ' + urllib.parse.unquote(a['type']))
		if 's' in a:
			signature = urllib.parse.unquote(a['s'])
			dsignature = sigDep.call('main',signature)
			print('Signature: ' + signature)
			print('Deciphered Signature: '+ dsignature)
			print('URL: ' + urllib.parse.unquote(a['url'])+'&signature='+ dsignature)
		else:
			print('URL: ' + urllib.parse.unquote(a['url']))

	print('===================Adaptive_fmts===========================')

	for i, a in adaptive_fmts.items():
		print('----------------------------------------------')
		print('Itag: ' + i)
		print('Type: ' + urllib.parse.unquote(a['type']))
		if 'quality_label' in a:
			print('Quality: ' + a['quality_label'])
			print('FPS: ' + a['fps'])
		else:
			print('<Audio>')
		print('Bitrate: ' + a['bitrate'])
		if 's' in a:
			signature = urllib.parse.unquote(a['s'])
			dsignature = sigDep.call('main', signature)
			print('Signature: ' + signature)
			print('Deciphered Signature: ' + dsignature)
			print('URL: ' + urllib.parse.unquote(a['url'])+'&ratebypass=yes&signature='+ dsignature )
		else:
			print('URL: ' + urllib.parse.unquote(a['url'])+'&ratebypass=yes')


if (len(sys.argv[1:]) == 1) and (len(sys.argv[1]) == 11):
		main(sys.argv[1])
else:
		print("Syntax\nPySyuf.py JaAWdljhD5o")
