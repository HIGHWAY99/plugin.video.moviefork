### ############################################################################################################
###	#	
### # Project: 			#		MovieFork.com - by The Highway 2013.
### # Author: 			#		The Highway
### # Version:			#		v0.2.7
### # Description: 	#		http://www.moviefork.com
###	#	
### ############################################################################################################
### ############################################################################################################
##### Imports #####
import xbmc,xbmcplugin,xbmcgui,xbmcaddon,xbmcvfs
#import requests ### (Removed in v0.2.1b to fix scripterror on load on Mac OS.) ### 
try: import requests ### <import addon="script.module.requests" version="1.1.0"/> ### 
except: t=''				 ### See https://github.com/kennethreitz/requests ### 


import urllib,urllib2,re,os,sys,htmllib,string,StringIO,logging,random,array,time,datetime
try: import urlresolver
except: t=''
import copy
###
#import cookielib
#import base64
#import threading
###
#import unicodedata ### I don't want to use unless I absolutely have to. ### 
#import zipfile ### Removed because it caused videos to not play. ### 
import HTMLParser, htmlentitydefs
try: 		import StorageServer
except: import storageserverdummy as StorageServer
try: 		from t0mm0.common.addon 				import Addon
except: from t0mm0_common_addon 				import Addon
try: 		from t0mm0.common.net 					import Net
except: from t0mm0_common_net 					import Net
try: 		from sqlite3 										import dbapi2 as sqlite; print "Loading sqlite3 as DB engine"
except: from pysqlite2 									import dbapi2 as sqlite; print "Loading pysqlite2 as DB engine"
try: 		from script.module.metahandler 	import metahandlers
except: from metahandler 								import metahandlers
### 
from teh_tools 		import *
from config 			import *
##### /\ ##### Imports #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
__plugin__=ps('__plugin__'); __authors__=ps('__authors__'); __credits__=ps('__credits__'); _addon_id=ps('_addon_id'); _domain_url=ps('_domain_url'); _database_name=ps('_database_name'); _plugin_id=ps('_addon_id')
_database_file=os.path.join(xbmc.translatePath("special://database"),ps('_database_name')+'.db'); 
### 
_addon=Addon(ps('_addon_id'), sys.argv); addon=_addon; _plugin=xbmcaddon.Addon(id=ps('_addon_id')); cache=StorageServer.StorageServer(ps('_addon_id'))
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Paths #####
### # ps('')
_addonPath	=xbmc.translatePath(_plugin.getAddonInfo('path'))
_artPath		=xbmc.translatePath(os.path.join(_addonPath,ps('_addon_path_art')))
_datapath 	=xbmc.translatePath(_addon.get_profile()); _artIcon		=_addon.get_icon(); _artFanart	=_addon.get_fanart()
##### /\ ##### Paths #####
##### Important Functions with some dependencies #####
def art(f,fe=ps('default_art_ext')): return xbmc.translatePath(os.path.join(_artPath,f+fe)) ### for Making path+filename+ext data for Art Images. ###
##### /\ ##### Important Functions with some dependencies #####
##### Settings #####
_setting={}; _setting['enableMeta']	=	_enableMeta			=tfalse(addst("enableMeta"))
_setting['debug-enable']=	_debugging			=tfalse(addst("debug-enable")); _setting['debug-show']	=	_shoDebugging		=tfalse(addst("debug-show"))
_setting['meta.movie.domain']=ps('meta.movie.domain'); _setting['meta.movie.search']=ps('meta.movie.search')
_setting['meta.tv.domain']   =ps('meta.tv.domain');    _setting['meta.tv.search']   =ps('meta.tv.search')
_setting['meta.tv.page']=ps('meta.tv.page'); _setting['meta.tv.fanart.url']=ps('meta.tv.fanart.url'); _setting['meta.tv.fanart.url2']=ps('meta.tv.fanart.url2'); _setting['label-empty-favorites']=tfalse(addst('label-empty-favorites'))
CurrentPercent=0; CancelDownload=False

##### /\ ##### Settings #####
##### Variables #####
_art404=art('notfound','.gif')
_art150=art('notfound','.gif')
_artDead=ps('art_dead'); _artSun=ps('art_sun'); 
COUNTRIES=ps('COUNTRIES'); GENRES=ps('GENRES'); _default_section_=ps('default_section'); net=Net(); DB=_database_file; BASE_URL=_domain_url;
#_artFanart=xbmc.translatePath(os.path.join(_addonPath,'fanart5.jpg'))
##### /\ ##### Variables #####
deb('Addon Path',_addonPath);  deb('Art Path',_artPath); deb('Addon Icon Path',_artIcon); deb('Addon Fanart Path',_artFanart)
### ############################################################################################################
def eod(): _addon.end_of_directory()
def deadNote(header='',msg='',delay=5000,image=_artDead): _addon.show_small_popup(title=header,msg=msg,delay=delay,image=image)
def sunNote( header='',msg='',delay=5000,image=_artSun):
	header=cFL(header,ps('cFL_color')); msg=cFL(msg,ps('cFL_color2'))
	_addon.show_small_popup(title=header,msg=msg,delay=delay,image=image)
def messupText(t,_html=False,_ende=False,_a=False,Slashes=False):
	if (_html==True): t=ParseDescription(HTMLParser.HTMLParser().unescape(t))
	if (_ende==True): t=t.encode('ascii', 'ignore'); t=t.decode('iso-8859-1')
	if (_a==True): t=_addon.decode(t); t=_addon.unescape(t)
	if (Slashes==True): t=t.replace( '_',' ')
	return t
def name2path(name):  return (((name.lower()).replace('.','-')).replace(' ','-')).replace('--','-')
def name2pathU(name): return (((name.replace(' and ','-')).replace('.','-')).replace(' ','-')).replace('--','-')
### ############################################################################################################
### ############################################################################################################
##### Queries #####
_param={}
_param['mode']=addpr('mode',''); _param['url']=addpr('url',''); _param['pagesource'],_param['pageurl'],_param['pageno'],_param['pagecount']=addpr('pagesource',''),addpr('pageurl',''),addpr('pageno',0),addpr('pagecount',1)
_param['img']=addpr('img',''); _param['fanart']=addpr('fanart',''); _param['thumbnail'],_param['thumbnail'],_param['thumbnail']=addpr('thumbnail',''),addpr('thumbnailshow',''),addpr('thumbnailepisode','')
_param['section']=addpr('section','movies'); _param['title']=addpr('title',''); _param['year']=addpr('year',''); _param['genre']=addpr('genre','')
_param['by']=addpr('by',''); _param['letter']=addpr('letter',''); _param['showtitle']=addpr('showtitle',''); _param['showyear']=addpr('showyear',''); _param['listitem']=addpr('listitem',''); _param['infoLabels']=addpr('infoLabels',''); _param['season']=addpr('season',''); _param['episode']=addpr('episode','')
_param['pars']=addpr('pars',''); _param['labs']=addpr('labs',''); _param['name']=addpr('name',''); _param['thetvdbid']=addpr('thetvdbid','')
_param['plot']=addpr('plot',''); _param['tomode']=addpr('tomode',''); _param['country']=addpr('country','')
_param['thetvdb_series_id']=addpr('thetvdb_series_id',''); _param['dbid']=addpr('dbid',''); _param['user']=addpr('user','')
_param['subfav']=addpr('subfav',''); _param['episodetitle']=addpr('episodetitle',''); _param['special']=addpr('special',''); _param['studio']=addpr('studio','')

#_param['']=_addon.queries.get('','')
#_param['']=_addon.queries.get('','')
##_param['pagestart']=addpr('pagestart',0)
##### /\
### ############################################################################################################
### ############################################################################################################
def initDatabase():
	print "Building solarmovie Database"
	if ( not os.path.isdir( os.path.dirname(_database_file) ) ): os.makedirs( os.path.dirname( _database_file ) )
	db=sqlite.connect(_database_file); cursor=db.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS seasons (season UNIQUE, contents);')
	cursor.execute('CREATE TABLE IF NOT EXISTS favorites (type, name, url, img);')
	db.commit(); db.close()

### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Player Functions #####
def PlayVideo(url, infoLabels, listitem):
	#WhereAmI('@ PlayVideo -- Getting ID From:  %s' % url); My_infoLabels=eval(infoLabels)
	WhereAmI('@ GetVideo -- url: %s' % url)
	html=''
	try: html=net.http_GET(url).content
	except: 
		try: html=getURL(url)
		except: 
			try: html=getURLr(url,_domain_url)
			except: html=''
	#print html_
	if (html=='') or (html=='none') or (html==None): 
		deb('Error','Problem with page'); deadNote('Results:  '+section,'No results were found.')
		return
	deb('Length of HTML',str(len(html)))
	#html=ParseDescription(html); html=remove_accents(html) #if (_debugging==True): print html
	try:		iitems=re.compile('"http://www.youtube.com/embed/([0-9A-Za-z\_\-]+)"').findall(html)[0]
	except:	iitems=None
	if (iitems is not None):
		deb('Youtube Video ID',iitems)
		url_youtube='plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=%s'
		#url_youtube='plugin://plugin.video.youtube/?action=play_video&videoid=%s'
		pug=url_youtube % iitems
		#xbmc.executebuiltin('XBMC.Container.Update(%s)' % pug )
		#xbmc.executebuiltin('XBMC.RunPlugin(%s)' % pug )
		#_addon.resolve_url(pug)
		play=xbmc.Player(xbmc.PLAYER_CORE_AUTO)
		play.play(pug)
	#
	#'plugin://plugin.video.youtube/?action=play_video&videoid='+permalinkId
	#
	#stream_url=urlresolver.HostedMediaFile(url=url).resolve()
	#stream_url=urlresolver.HostedMediaFile(url).resolve()
	#_addon.resolve_url(stream_url)
	#infoLabels={ "Studio": addpr('title',''), 'Title': addpr('studio',''), 'url': url } ### yes i switched title and studio on purpose.
	#li=xbmcgui.ListItem(_param['title'], iconImage=_param['img'], thumbnailImage=_param['img'])
	#li.setInfo(type="Video", infoLabels=infoLabels ); li.setProperty('IsPlayable', 'true')
	#_addon.end_of_directory()
	#play=xbmc.Player(xbmc.PLAYER_CORE_AUTO) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
	#play.play(stream_url, li); xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)


def PlayLibrary(section, url, showtitle='', showyear=''): ### Menu for Listing Hosters (Host Sites of the actual Videos)
	WhereAmI('@ Play Library: %s' % url); sources=[]; listitem=xbmcgui.ListItem()
	#eod()
	#_addon.resolve_url(url)
	if (url==''): return
	html=net.http_GET(url).content; html=html.encode("ascii", "ignore")
	##if (_debugging==True): print html
	#if  ( section == 'tv'): ## TV Show ## Title (Year) - Info
	#	match=re.compile(ps('LLinks.compile.show_episode.info'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0] ### <title>Watch The Walking Dead Online for Free - Prey - S03E14 - 3x14 - SolarMovie</title>
	#	if (_debugging==True): print match
	#	if (match==None):  return
	#	ShowYear=_param['year'] #ShowYear=showyear
	#	ShowTitle=match[0].strip(); EpisodeTitle=match[1].strip(); Season=match[2].strip(); Episode=match[3].strip()
	#	ShowTitle=HTMLParser.HTMLParser().unescape(ShowTitle); ShowTitle=ParseDescription(ShowTitle); ShowTitle=ShowTitle.encode('ascii', 'ignore'); ShowTitle=ShowTitle.decode('iso-8859-1'); EpisodeTitle=HTMLParser.HTMLParser().unescape(EpisodeTitle); EpisodeTitle=ParseDescription(EpisodeTitle); EpisodeTitle=EpisodeTitle.encode('ascii', 'ignore'); EpisodeTitle=EpisodeTitle.decode('iso-8859-1')
	#	if ('<p id="plot_' in html):
	#		ShowPlot=(re.compile(ps('LLinks.compile.show.plot'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]).strip(); ShowPlot=HTMLParser.HTMLParser().unescape(ShowPlot); ShowPlot=ParseDescription(ShowPlot); ShowPlot=ShowPlot.encode('ascii', 'ignore'); ShowPlot=ShowPlot.decode('iso-8859-1')
	#	else: ShowPlot=''
	#	match=re.compile(ps('LLinks.compile.imdb.url_id'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]
	#	if (_debugging==True): print match
	#	(IMDbURL,IMDbID)=match; IMDbURL=IMDbURL.strip(); IMDbID=IMDbID.strip(); My_infoLabels={ "Studio": ShowTitle+'  ('+ShowYear+'):  '+Season+'x'+Episode+' - '+EpisodeTitle, "Title": ShowTitle, "ShowTitle": ShowTitle, "Year": ShowYear, "Plot": ShowPlot, 'Season': Season, 'Episode': Episode, 'EpisodeTitle': EpisodeTitle, 'IMDbURL': IMDbURL, 'IMDbID': IMDbID, 'IMDb': IMDbID }; listitem.setInfo(type="Video", infoLabels=My_infoLabels )
	#else:	#################### Movie ## Title (Year) - Info
	#	match=re.compile(ps('LLinks.compile.show.title_year'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]
	#	if (_debugging==True): print match
	#	if (match==None): return
	#	ShowYear=match[1].strip(); ShowTitle=match[0].strip(); ShowTitle=HTMLParser.HTMLParser().unescape(ShowTitle); ShowTitle=ParseDescription(ShowTitle); ShowTitle=ShowTitle.encode('ascii', 'ignore'); ShowTitle=ShowTitle.decode('iso-8859-1'); ShowPlot=(re.compile(ps('LLinks.compile.show.plot'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]).strip(); ShowPlot=HTMLParser.HTMLParser().unescape(ShowPlot); ShowPlot=ParseDescription(ShowPlot); ShowPlot=ShowPlot.encode('ascii', 'ignore'); ShowPlot=ShowPlot.decode('iso-8859-1'); match=re.compile(ps('LLinks.compile.imdb.url_id'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]
	#	if (_debugging==True): print match
	#	(IMDbURL,IMDbID)=match; IMDbURL=IMDbURL.strip(); IMDbID=IMDbID.strip(); My_infoLabels={ "Studio": ShowTitle+'  ('+ShowYear+')', "Title": ShowTitle, "ShowTitle": ShowTitle, "Year": ShowYear, "Plot": ShowPlot, 'IMDbURL': IMDbURL, 'IMDbID': IMDbID, 'IMDb': IMDbID }; listitem.setInfo(type="Video", infoLabels=My_infoLabels )
	### Both -Movies- and -TV Shows- ### Hosters
	try:		matchH=re.compile(ps('LLinks.compile.hosters2'), re.MULTILINE | re.DOTALL | re.IGNORECASE).findall(html)
	except:	matchH=''
	#deb('length of matchH',str(len(matchH)))
	#print matchH
	if (len(matchH) > 0):
		oList=[]; hList=[]; matchH=sorted(matchH, key=lambda item: item[3], reverse=True)
		for url, host, quality, age in matchH:
			url=url.strip(); host=host.strip(); quality=quality.strip(); age=age.strip()
			try:		mID=re.compile('/.+?/.+?/([0-9]+)/', re.DOTALL | re.IGNORECASE).findall(url)[0]
			except: mID=''
			#deb('Media Passed',str(host)+' | '+str(quality)+' | '+str(age)+' | '+str(url)+' | '+str(mID))
			if (mID is not ''):
				oList.append(host+'  ['+quality+']  ('+age+')')
				hList.append([url,host,quality,age,mID])
		try:		rt=askSelection(oList,'Select Source:')
		except:	rt=''
		print rt
		if (rt==None) or (rt=='none') or (rt==False) or (rt==''): return
		hItem=hList[rt]
		deb('ID',hItem[4])
		urlB='%s/link/play/%s/' % (ps('_domain_url'),hItem[4])
		html=net.http_GET(urlB).content
		try: url=re.compile('<iframe.+?src="(.+?)"', re.MULTILINE | re.DOTALL | re.IGNORECASE).findall(html)[0]
		except: url=''
		url=url.replace('/embed/', '/file/'); deb('hoster url',url)
		#oList=[]
		#for url, host, quality, age in match:
		#	url=url.strip(); host=host.strip(); quality=quality.strip(); age=age.strip()
		#	print 'Media Failed:  '+str(host)+' | '+str(quality)+' | '+str(age)+' | '+url
		#	if (urlresolver.HostedMediaFile(url=url.strip()).valid_url()):
		#		try:		MediaID=urlresolver.HostedMediaFile(url=url).get_media_url()
		#		except: MediaID=''
		#		try:		MediaHost=urlresolver.HostedMediaFile(url=url).get_host()
		#		except: MediaHost=''
		#		print 'Media Passed:  '+str(MediaHost)+' | '+str(MediaID)+' | '+url
		#		if (MediaHost is not '') and (MediaID is not ''):
		#			oList.append(urlresolver.HostedMediaFile(host=MediaHost, media_id=MediaID))
		##
		#
		#try: url=urlresolver.choose_source(oList)
		#except: return
		#
		#MediaID=urlresolver.HostedMediaFile(url=url).get_media_url()
		#MediaHost=urlresolver.HostedMediaFile(url=url).get_host()
		#print 'Media:  '+str(MediaHost)+' | '+str(MediaID)+' | '+url
		#print str(urlresolver.HostedMediaFile(url=url.strip()).valid_url())
		#if (urlresolver.HostedMediaFile(url=url.strip()).valid_url()):
		#
		#
		#
		#
		#videoId=match.group(1); deb('Solar ID',videoId); url=BASE_URL + '/link/play/' + videoId + '/' ## Example: http://www.solarmovie.so/link/play/1052387/ ##
		#html=net.http_GET(url).content; match=re.search( '<iframe.+?src="(.+?)"', html, re.IGNORECASE | re.MULTILINE | re.DOTALL); link=match.group(1); link=link.replace('/embed/', '/file/'); deb('hoster link',link)
		#
		deb('video',url)
		liz=xbmcgui.ListItem(_param['showtitle'], iconImage="DefaultVideo.png", thumbnailImage=_param['img'])
		if  ( section == 'tv'): ## TV Show ## Title (Year) - Info
			liz.setInfo( type="Video", infoLabels={ "Title": _param['showtitle']+'  ('+_param['showyear']+')', "Studio": 'SolarMovie.so' } )
		else:	#################### Movies ### Title (Year) - Info
			liz.setInfo( type="Video", infoLabels={ "Title": _param['showtitle']+'  ('+_param['showyear']+')', "Studio": 'SolarMovie.so' } )
		liz.setProperty("IsPlayable","true")
		##pl=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		##pl.clear()
		##pl.add(url, liz)
		##xbmc.Player().play(pl)
		play=xbmc.Player(xbmc.PLAYER_CORE_AUTO) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
		print url
		stream_url = urlresolver.HostedMediaFile(url).resolve()
		print stream_url
		play.play(stream_url, liz)
		#play.play(url, liz)
		liz.setPath(url)
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
		_addon.resolve_url(url)
		_addon.resolve_url(stream_url)
		##
		##
		##
		##count=1
		##for url, host, quality, age in match:
		##	host=host.strip(); quality=quality.strip(); name=str(count)+". "+host+' - [[B]'+quality+'[/B]] - ([I]'+age+'[/I])'
		##	if urlresolver.HostedMediaFile(host=host, media_id='xxx'):
		##		img=ps('Hosters.icon.url')+host; My_infoLabels['quality']=quality; My_infoLabels['age']=age; My_infoLabels['host']=host; _addon.add_directory({'section': section, 'img': _param['img'], 'mode': 'PlayVideo', 'url': url, 'quality': quality, 'age': age, 'infoLabels': My_infoLabels, 'listitem': listitem}, {'title':  name}, img=img, is_folder=False); count=count+1 
		eod()
	else: return
	### ################################################################

def DownloadStop():  ## Testing ## Doesn't work yet.
	global CancelDownload
	CancelDownload=True
	#global CancelDownload
	eod()
	#download_method=addst('download_method') ### 'Progress|ProgressBG|Hidden'
	#if   (download_method=='Progress'):
	#	dp=xbmcgui.DialogProgress()   ## For Frodo and earlier.
	#	dp.close()
	#elif (download_method=='ProgressBG'):
	#	dp=xbmcgui.DialogProgressBG() ## Only works on daily build of XBMC.
	#	dp.close()
	#elif (download_method=='Test'):
	#	t=''
	#elif (download_method=='Hidden'):
	#	t=''
	#else: deb('Download Error','Incorrect download method.'); myNote('Download Error','Incorrect download method.'); return
	#try:		t=''
	#except: t=''

def DownloadStatus(numblocks, blocksize, filesize, dlg, download_method, start_time, section, url, img, LabelName, ext, LabelFile):
	if (CancelDownload==True):
		try:
			if   (download_method=='Progress'): ## For Frodo and earlier.
				dlg.close()
			elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
				dlg.close()
			elif (download_method=='Test'): t=''
			elif (download_method=='Hidden'): t=''
		except: t=''
	try:
		percent = min(numblocks * blocksize * 100 / filesize, 100)
		currently_downloaded = float(numblocks) * blocksize / (1024 * 1024)
		kbps_speed = numblocks * blocksize / (time.time() - start_time)
		if kbps_speed > 0:	eta = (filesize - numblocks * blocksize) / kbps_speed
		else:								eta = 0
		kbps_speed /= 1024
		total = float(filesize) / (1024 * 1024)
		#if   (download_method=='Progress'): ## For Frodo and earlier.
		#	line1 = '%.02f MB of %.02f MB' % (currently_downloaded, total)
		#	line1 +='  '+percent+'%'
		#	line2 = 'Speed: %.02f Kb/s ' % kbps_speed
		#	line3 = 'ETA: %02d:%02d' % divmod(eta, 60)
		#	dlg.update(percent, line1, line2, line3)
		#elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
		#	line1  ='%.02f MB of %.02f MB' % (currently_downloaded, total)
		#	line1 +='  '+percent+'%'
		#	line2  ='Speed: %.02f Kb/s ' % kbps_speed
		#	line2 +='ETA: %02d:%02d' % divmod(eta, 60)
		#	dlg.update(percent, line1, line2)
		#elif (download_method=='Test'):
		#	mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total)
		#	spd = 'Speed: %.02f Kb/s ' % kbps_speed
		#	est = 'ETA: %02d:%02d' % divmod(eta, 60)
		#	Header=		ext+'  '+mbs+'  '+percent+'%'
		#	Message=	est+'  '+spd
		#elif (download_method=='Hidden'): t=''
		#if (time.time()==start_time) or (int(str(time.time())[-5:1]) == 0): # and (int(str(time.time())[-5:2]) < 10):
		#if (int(time.strptime(time.time(),fmt='%S')) == 0):
		#if (str(percent) in ['0','1','5','10','15','20','25','30','35','40','45','50','55','60','65','70','75','80','85','90','91','92','93','94','95','96','97','98','99','100']):
		#if (str(percent) == '0' or '1' or '5' or '10' or '15' or '20' or '25' or '30' or '35' or '40' or '45' or '50' or '55' or '60' or '65' or '70' or '75' or '80' or '85' or '90' or '91' or '92' or '93' or '94' or '95' or '96' or '97' or '98' or '99' or '100'):
		#if ('.' in str(percent)): pCheck=int(str(percent).split('.')[0])
		#else: pCheck=percent
		#pCheck=int(str(percent)[1:])
		#if (CurrentPercent is not pCheck):
		#	global CurrentPercent
		#	CurrentPercent=pCheck
		#	myNote(header=Header,msg=Message,delay=100,image=img)
		##myNote(header=Header,msg=Message,delay=1,image=img)
	except:
		percent=100
		if   (download_method=='Progress'): ## For Frodo and earlier.
			t=''
			dlg.update(percent)
		elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
			t=''
			dlg.update(percent)
		elif (download_method=='Test'): t=''
		#myNote(header='100%',msg='Download Completed',delay=15000,image=img)
		elif (download_method=='Hidden'): t=''
	if   (download_method=='Progress'): ## For Frodo and earlier.
		line1 = '%.02f MB of %.02f MB' % (currently_downloaded, total)
		line1 +='  '+str(percent)+'%'
		line2 = 'Speed: %.02f Kb/s ' % kbps_speed
		line3 = 'ETA: %02d:%02d' % divmod(eta, 60)
		dlg.update(percent, line1, line2, line3)
	elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
		line1  ='%.02f MB of %.02f MB' % (currently_downloaded, total)
		line1 +='  '+str(percent)+'%'
		line2  ='Speed: %.02f Kb/s ' % kbps_speed
		line2 +='ETA: %02d:%02d' % divmod(eta, 60)
		dlg.update(percent, line1, line2)
	elif (download_method=='Test'):
		mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total)
		spd = 'Speed: %.02f Kb/s ' % kbps_speed
		est = 'ETA: %02d:%02d' % divmod(eta, 60)
		Header=		ext+'  '+mbs+'  '+str(percent)+'%'
		Message=	est+'  '+spd
	elif (download_method=='Hidden'): t=''
	if   (download_method=='Progress'): ## For Frodo and earlier.
		try:
			if dlg.iscanceled(): ## used for xbmcgui.DialogProgress() but causes an error with xbmcgui.DialogProgressBG()
				dlg.close()
				#deb('Download Error','Download canceled.'); myNote('Download Error','Download canceled.')
				#raise StopDownloading('Stopped Downloading')
		except: t=''
	elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
		try:
			if (dlg.isFinished()): 
				dlg.close()
		except: t=''

def DownloadRequest(section, url,img,LabelName):
	if (LabelName=='') and     (_param['title'] is not ''): LabelName==_param['title']
	if (LabelName=='') and (_param['showtitle'] is not ''): LabelName==_param['showtitle']
	LabelFile=clean_filename(LabelName)
	deb('LabelName',LabelName)
	if (LabelName==''): deb('Download Error','Missing Filename String.'); myNote('Download Error','Missing Filename String.'); return
	if (section==ps('section.wallpaper')):	FolderDest=xbmc.translatePath(addst("download_folder_wallpapers"))
	elif (section==ps('section.tv')):				FolderDest=xbmc.translatePath(addst("download_folder_tv"))
	elif (section==ps('section.movie')):		FolderDest=xbmc.translatePath(addst("download_folder_movies"))
	else:																		FolderDest=xbmc.translatePath(addst("download_folder_movies"))
	if os.path.exists(FolderDest)==False: os.mkdir(FolderDest)
	if os.path.exists(FolderDest):
		if (section==ps('section.tv')) or (section==ps('section.movie')):
			### param >> url:  /link/show/1466546/
			match=re.search( '/.+?/.+?/(.+?)/', url) ## Example: http://www.solarmovie.so/link/show/1052387/ ##
			videoId=match.group(1); deb('Solar ID',videoId); url=BASE_URL + '/link/play/' + videoId + '/' ## Example: http://www.solarmovie.so/link/play/1052387/ ##
			html=net.http_GET(url).content; match=re.search( '<iframe.+?src="(.+?)"', html, re.IGNORECASE | re.MULTILINE | re.DOTALL); link=match.group(1); link=link.replace('/embed/', '/file/'); deb('hoster link',link)
			try: stream_url = urlresolver.HostedMediaFile(link).resolve()
			except: stream_url=''
			ext=Download_PrepExt(stream_url,'.flv')
		else:
			stream_url=url
			ext=Download_PrepExt(stream_url,'.jpg')
		t=1; c=1
		if os.path.isfile(xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext))):
			t=LabelFile
			while t==LabelFile:
				if os.path.isfile(xbmc.translatePath(os.path.join(FolderDest,LabelFile+'['+str(c)+']'+ext)))==False:
					LabelFile=LabelFile+'['+str(c)+']'
				c=c+1
		start_time = time.time()
		deb('start_time',str(start_time))
		download_method=addst('download_method') ### 'Progress|ProgressBG|Hidden'
		urllib.urlcleanup()
		if   (download_method=='Progress'):
			dp=xbmcgui.DialogProgress(); dialogType=12 ## For Frodo and earlier.
			dp.create('Downloading', LabelFile+ext)
			urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
			myNote('Download Complete',LabelFile+ext,15000)
		elif (download_method=='ProgressBG'):
			dp=xbmcgui.DialogProgressBG(); dialogType=13 ## Only works on daily build of XBMC.
			dp.create('Downloading', LabelFile+ext)
			urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
			myNote('Download Complete',LabelFile+ext,15000)
		elif (download_method=='Test'):
			dp=xbmcgui.DialogProgress()
			myNote('Download Started',LabelFile+ext,15000)
			urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
			myNote('Download Complete',LabelFile+ext,15000)
		elif (download_method=='Hidden'):
			dp=xbmcgui.DialogProgress()
			myNote('Download Started',LabelFile+ext,15000)
			urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
			myNote('Download Complete',LabelFile+ext,15000)
		elif (download_method=='jDownloader (StreamURL)'):
			myNote('Download','sending to jDownloader plugin',15000)
			xbmc.executebuiltin("XBMC.RunPlugin(plugin://plugin.program.jdownloader/?action=addlink&url=%s)" % stream_url)
			#return
		elif (download_method=='jDownloader (Link)'):
			myNote('Download','sending to jDownloader plugin',15000)
			xbmc.executebuiltin("XBMC.RunPlugin(plugin://plugin.program.jdownloader/?action=addlink&url=%s)" % link)
			#return
		else: deb('Download Error','Incorrect download method.'); myNote('Download Error','Incorrect download method.'); return
		##
		##urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
		##
		#myNote('Download Complete',LabelFile+ext,15000)
		##
		#### xbmc.translatePath(os.path.join(FolderDest,localfilewithpath+ext))
		_addon.resolve_url(url)
		_addon.resolve_url(stream_url)
		#
		#
	else:	deb('Download Error','Unable to create destination path.'); myNote('Download Error','Unable to create destination path.'); return

def PlayTrailer(url,_title,_year,_image): ### Not currently used ###
	WhereAmI('@ PlayVideo:  %s' % url) #; sources=[]; url=url.decode('base-64')
	#if ('<h2>Movie trailer</h2>' not in url): eod(); return
	EmbedID=''; html=net.http_GET(url).content #getURL(url)
	html=messupText(html,True,True,True,False)
	#print str(html)
	if ('traileraddict.com/emd/' in html):
		deb('Found','traileraddict.com/emd/')
		#EmbedID=re.compile('traileraddict.com/emd/(\d+)"', re.DOTALL).findall(html)[0].strip()
		try: 		EmbedID=re.compile('traileraddict.com/emd/(\d+)"', re.DOTALL).findall(html)[0].strip()
		except: EmbedID=''
	if (EmbedID==''):
		#print html
		#ImdbID=re.compile('<strong>IMDb ID:</strong>[\n]\s+<a href=".+?">(\d+)</a>"', re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0].strip()
		try:		ImdbID=re.compile('%2Ftitle%2Ftt(\d+)%2F"', re.DOTALL).findall(html)[0].strip()
		except:	ImdbID=''
		if (ImdbID==''): eod(); deb('Error Playing Trailer','No Imdb ID.'); deadNote('Problem with the Trailer','Trailer is Unavailable.'); return
		deb('ImdbID',ImdbID)
		thtml=getURL('http://api.traileraddict.com/?imdb='+ImdbID)
		try: 		EmbedID=re.compile('"http://www.traileraddict.com/emd/([0-9]+)"', re.DOTALL).findall(thtml)[0].strip()
		except: EmbedID=''
	if (EmbedID==''): eod(); deb('Error Playing Trailer','No Embed Video ID.'); deadNote('Problem with the Trailer','Trailer is Unavailable.'); return
	deb('EmbedID',EmbedID)
	vhtml=getURL('http://www.traileraddict.com/fvar.php?tid='+EmbedID) #vhtml=getURL('http://www.traileraddict.com/fvarhd.php?tid='+EmbedID)
	#print vhtml
	if ('Error: Trailer is (Possibly Temporarily) Unavailable' in vhtml): deadNote('Problem with the Trailer','Trailer is Unavailable.'); return
	try:		thumb=re.compile('&image=(.+?)&', re.DOTALL).findall(vhtml)[0].strip()
	except:	thumb=_param['img']
	try: 		title=re.compile('&filmtitle=(.+?)&', re.DOTALL).findall(vhtml)[0].strip()
	except: title=_param['title']
	try: 			url=re.compile('&fileurl=(.+?)&', re.DOTALL).findall(vhtml)[0].strip()
	except: 
		try: 		url=re.compile('&fileurl=(.+?)[\n]\s+&', re.DOTALL).findall(vhtml)[0].strip()
		except: url=''
	if (url==''): eod(); deb('Error Playing Trailer','No Url was found from vhtml.'); deadNote('Problem with the Trailer','Trailer is Unavailable.'); return
	url=urllib.unquote_plus(url)
	deb('video',url)
	liz=xbmcgui.ListItem(_param['showtitle'], iconImage=thumb, thumbnailImage=_image)
	liz.setInfo( type="Video", infoLabels={ "Title": title, "Studio": _title+'  ('+_year+')' } )
	liz.setProperty("IsPlayable","true")
	play=xbmc.Player(xbmc.PLAYER_CORE_AUTO) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
	play.play(url, liz)
	#liz.setPath(url)
	#xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
	_addon.resolve_url(url)
	#eod(); return

##### /\ ##### Player Functions #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Weird, Stupid, or Plain up Annoying Functions. #####
def netURL(url): ### Doesn't seem to work.
	return net.http_GET(url).content
def remove_accents(input_str): ### Not even sure rather this one works or not.
	#nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
	#return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
	return input_str
##### /\ ##### Weird, Stupid, or Plain up Annoying Functions. #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################

def mGetItemPage(url):
	deb('Fetching html from Url',url)
	try: html=net.http_GET(url).content
	except: html=''
	if (html=='') or (html=='none') or (html==None) or (html==False): return ''
	else:
		html=HTMLParser.HTMLParser().unescape(html); html=_addon.decode(html); html=_addon.unescape(html); html=ParseDescription(html); html=html.encode('ascii', 'ignore'); html=html.decode('iso-8859-1'); deb('Length of HTML fetched',str(len(html)))
	return html

def mGetDataTest(html,toGet): ## For Testing Only
	resultCnt=0; results={}; debob(toGet)
	for item in toGet:
		parseTag='<p id="plot_\d+">(.+?)</p>'; item=item.lower()
		results[item]=(re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]).strip()
		return results

def mGetDataPlot(html,parseTag='<p id=\"plot_\d+\">(.+?)</p>'): ## Working Temp-Fix
	if ('<p id="plot_' in html):
		try: return (re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]).strip()
		except: return ''
	else: return ''

def mGetDataGroup2String(html,parseTag='',ifTag='',startTag='',endTag='',Topic=''):
	if (ifTag in html):
		html=(((html.split(startTag)[1])).split(endTag)[0]).strip()
		try: results=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)
		except: return ''
		i=0; r=''
		for result in results:
			if (i==0): 	r=result.strip()
			else: 			r=r+', '+result.strip()
			i=i+1
		deb(Topic,r); return r
	else: return ''
def mGetDataGenre(html,parseTag='<a href=".+?watch-.+?-.+?s.html">[\n]\s+(.+?)</a>',ifTag='.html">',startTag='<div class="mediaDescription">',endTag='<div class="buttonsLine">',Topic='Genre'): ## Think I'll keep this one since it needs the outside part parsed out.
	return mGetDataGroup2String(html,parseTag,ifTag,startTag,endTag,Topic)
def mGetDataCountry(html,parseTag='<a href=".+?s-from.+?.html">(.+?)</a>',ifTag='.html">',startTag='<div class="mediaDescription">',endTag='<div class="buttonsLine">',Topic='Country'): ## Think I'll keep this one since it needs the outside part parsed out.
	return mGetDataGroup2String(html,parseTag,ifTag,startTag,endTag,Topic)
def mGetDataDirector(html,parseTag='<a href="/watch-movies-by-.+?.html">[\n]\s+(.+?)</a>',ifTag='<h4>Director</h4>',startTag='<h4>Director</h4>',endTag='</div>',Topic='Director'): ## Think I'll keep this one since it needs the outside part parsed out.
	return mGetDataGroup2String(html,parseTag,ifTag,startTag,endTag,Topic)
def mGetDataCast(html,parseTag='<a href="/watch-movies-with-.+?.html">[\n]\s+(.+?)</a>',ifTag='<h4>Cast</h4>',startTag='<h4>Cast</h4>',endTag='</div>',Topic='Cast'): ## Think I'll keep this one since it needs the outside part parsed out.
	return mGetDataGroup2String(html,parseTag,ifTag,startTag,endTag,Topic)
def mGetDataKeywords(html,parseTag='<a href="/watch-movies-tagged-as-.+?.html">[\n]\s+(.+?)</a>',ifTag='<h4>Keywords</h4>',startTag='<h4>Keywords</h4>',endTag='</div>',Topic='Keywords'): ## Think I'll keep this one since it needs the outside part parsed out.
	return mGetDataGroup2String(html,parseTag,ifTag,startTag,endTag,Topic)

def mdGetTV(html,toGet):
	resultCnt=0; results={}; debob(toGet)
	for item in toGet:
		item=item.lower();parseMethod=''; parseTag=''; parseTag2=''; parseTag3=''; parsePreResult=''; rCheck=False
		if (item=='result.url'): ### 
			parseMethod='re.compile.prefix'; parsePreResult=_setting['meta.tv.page']; parseTag='<tr><td class="\D+">\d+</td>.+?href="/index.php.+?tab=series.+?id=(\d+)&.+?lid=7">'
			if ('>English</td>' in html): rCheck=True
		elif (item=='result.id'): ### 
			parseMethod='re.compile'; parseTag='<tr><td class="\D+">\d+</td>.+?href="/index.php.+?tab=series.+?id=(\d+)&lid=7">' ## &amp; 's were parsed out earlier. ##
			if ('>English</td>' in html): rCheck=True
		elif (item=='fanart'): ### 
			parseMethod='re.compile.group'; parsePreResult=_setting['meta.tv.domain']; parseTag='<tr><td></td><td align=right><a href="(.+?)" target="_blank">View Full Size</a></td></tr>'
			if ('" target="_blank">View Full Size</a></td></tr>' in html): rCheck=True
		elif (item=='thetvdb.episode.overviews'): ### 
			parseMethod='split'; parseTag='<td>Overview: </td>'; parseTag2='</tr>'; deb('get item',item)
			if ('<td>Overview: </td>' in html): rCheck=True
		elif (item=='thetvdb.episode.overview1'): ### 
			parseMethod='split'; parseTag='<textarea rows="10" cols="45" name="Overview_7" style="display: inline">'; parseTag2='</textarea>'; deb('get item',item)
			if ('<td>Overview: </td>' in html): rCheck=True
		elif (item=='thetvdb.episode.overview'): ### 
			parseMethod='re.compile'; parseTag='<textarea rows="10" cols="45" name="Overview_7" style="display: inline">(.+?)</textarea>'; deb('get item',item)
			if ('<td>Overview: </td>' in html): rCheck=True
		#else: rCheck=False
		#if (rCheck==False): print html
		deb('rCheck',str(rCheck))
		if (rCheck==True): ## Trying to do away with errors for results that dont contain the requested information.
			if   (parseMethod=='re.compile2'): ## returns 2nd result
				resultCnt=resultCnt+1; results[item]=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[1].strip()
				if (results[item]==''): results[item]=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0].strip()
			elif (parseMethod=='re.compile'): ## returns 1st result
				resultCnt=resultCnt+1; results[item]=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0].strip()
			elif (parseMethod=='re.compile.fanart'): ## returns 1st result
				resultCnt=resultCnt+1; html2=(html.split('<h1>Fan Art</h1>')[1]).split('</table>')[0]
				if ('View Full Size' in html2): results[item]=parsePreResult+re.compile(parseTag, re.IGNORECASE | re.DOTALL).findall(html2)[0].strip()
				else: results[item]=''
			elif (parseMethod=='re.compile.prefix'): ## returns 1st result
				try: results[item]=parsePreResult+re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0].strip()
				except: results[item]=''
				resultCnt=resultCnt+1
			elif (parseMethod=='re.compile.group'): ## returns a group of results
				resultCnt=resultCnt+1; results[item]=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)
			elif (parseMethod=='split'):
				resultCnt=resultCnt+1; results[item]=(((html.split(parseTag)[1])).split(parseTag2)[0]).strip()
			elif (parseMethod=='re.search2'): ## returns 2nd result
				resultCnt=resultCnt+1; match=re.search(parseTag, html, re.IGNORECASE | re.MULTILINE | re.DOTALL); results[item]=match.group(2)
			elif (parseMethod=='re.search'): ## returns 1st result
				resultCnt=resultCnt+1; match=re.search(parseTag, html, re.IGNORECASE | re.MULTILINE | re.DOTALL); results[item]=match.group(1)
			elif (parseMethod=='re.search.group'): ## returns a group of results
				resultCnt=resultCnt+1; match=re.search(parseTag, html, re.IGNORECASE | re.MULTILINE | re.DOTALL); results[item]=match.group()
			else: 
				resultCnt=resultCnt+1; results[item]=''
		else: 
			resultCnt=resultCnt+1; results[item]=''
	if debugging==True: print results
	return results

def mdGetSplitFindGroup(html,ifTag='', parseTag='',startTag='',endTag=''): 
	if (ifTag=='') or (parseTag=='') or (startTag=='') or (endTag==''): return ''
	if (ifTag in html):
		html=(((html.split(startTag)[1])).split(endTag)[0]).strip()
		try: return re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)
		except: return ''
	else: return ''

def mdGetMovie(html,toGet):
	resultCnt=0; results={}; debob(toGet)
	for item in toGet:
		item=item.lower();parseMethod=''; parseTag=''; parseTag2=''; parseTag3=''; parsePreResult=''; rCheck=False
		if (item=='result.poster'): ### 
			parseTag='<div class="poster">[\n]\s+<a href=".+?" title=".+?"><img class="right_shadow" src="(.+?)" width="\d+" height="\d+" /></a>'
			parseMethod='re.compile'
			if ('<div class="poster">' in html): rCheck=True
		elif (item=='result.url'): ### 
			parsePreResult=_setting['meta.movie.domain']
			parseTag='<div class="poster">[\n]\s+<a href="(.+?)" title=".+?"><img class="right_shadow" src=".+?" width="\d+" height="\d+" /></a>'
			parseMethod='re.compile.prefix'
			if ('<div class="poster">' in html): rCheck=True
		elif (item=='og.image'): ### 
			parseTag='<meta property="og:image" content="(.+?)" />'
			parseMethod='re.compile'
			if ('<meta property="og:image" content="' in html): rCheck=True
		elif (item=='og.image2'): ### 
			parseTag='<meta property="og:image" content="(.+?)" />'
			parseMethod='re.compile2'
			if ('<meta property="og:image" content="' in html): rCheck=True
		elif (item=='og.plot'): ### 
			parseTag='<meta property="og:description" content="(.+?)" />'
			parseMethod='re.compile'
			if ('<meta property="og:description" content="' in html): rCheck=True
		#if (item=='fanart'): ### 
		#	parseTag='<strong>IMDb rating:</strong>[\n]\s+(.+?)\s+\(.+? votes\)'
		#	parseMethod='re.compile.group'
		#	if ('<strong>IMDb rating:</strong>' in html): rCheck=True
		#else: rCheck=False
		deb('rCheck',str(rCheck))
		if (rCheck==True): ## Trying to do away with errors for results that dont contain the requested information.
			if   (parseMethod=='re.compile2'): ## returns 2nd result
				resultCnt=resultCnt+1; results[item]=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[1].strip()
				if (results[item]==''): results[item]=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0].strip()
			elif (parseMethod=='re.compile'): ## returns 1st result
				resultCnt=resultCnt+1; results[item]=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0].strip()
			elif (parseMethod=='re.compile.prefix'): ## returns 1st result
				resultCnt=resultCnt+1; results[item]=parsePreResult+re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0].strip()
			elif (parseMethod=='re.compile.group'): ## returns a group of results
				resultCnt=resultCnt+1; results[item]=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)
			elif (parseMethod=='split'):
				resultCnt=resultCnt+1; results[item]=(((html.split(parseTag)[1])).split(parseTag2)[0]).strip()
			elif (parseMethod=='re.search2'): ## returns 2nd result
				resultCnt=resultCnt+1; match=re.search(parseTag, html, re.IGNORECASE | re.MULTILINE | re.DOTALL); results[item]=match.group(2)
			elif (parseMethod=='re.search'): ## returns 1st result
				resultCnt=resultCnt+1; match=re.search(parseTag, html, re.IGNORECASE | re.MULTILINE | re.DOTALL); results[item]=match.group(1)
			elif (parseMethod=='re.search.group'): ## returns a group of results
				resultCnt=resultCnt+1; match=re.search(parseTag, html, re.IGNORECASE | re.MULTILINE | re.DOTALL); results[item]=match.group()
			else: 
				resultCnt=resultCnt+1; results[item]=''
		else: 
			resultCnt=resultCnt+1; results[item]=''
	if debugging==True: print results
	return results

def mGetData(html,toGet):
	#if (html=='') or (html=='none') or (html==None) or (html==False): 
	#	deb('mGetData','html is empty')
	#	return None
	resultCnt=0; results={}; debob(toGet)
	for item in toGet:
		item=item.lower();parseMethod=''; parseTag=''; parseTag2=''; parseTag3=''; rCheck=False
		if (item=='plot') or (item=='movieplot') or (item=='showplot'): ### 
			parseTag='<p id="plot_\d+">(.+?)</p>'
			parseMethod='re.compile'
			if ('<p id="plot_' in html): 
				rCheck=True; deb("found","'<p id=\"plot_'")
		elif (item=='imdbrating'): ### 7.3
			parseMethod='re.compile'; parseTag='<strong>IMDb rating:</strong>[\n]\s+(.+?)\s+\(.+? votes\)'
			if ('<strong>IMDb rating:</strong>' in html): rCheck=True
		elif (item=='episodeplot'): ### 
			parseMethod='re.compile2'; parseTag='<p id="plot_\d+">(.+?)</p>'
			if ('<p id="plot_' in html): rCheck=True
		elif (item=='latestepisodeplot'): ### 
			parseMethod='re.compile2'; parseTag='<p id="plot_\d+">(.+?)</p>'
			if ('<p id="plot_' in html): rCheck=True
		elif (item=='imdbid'): ### 0816711
			parseMethod='re.compile'; parseTag='<strong>IMDb ID:</strong>[\n]\s+<a href=".+?">(\d+)</a>'
			if ('<strong>IMDb ID:</strong>' in html): rCheck=True
		elif (item=='imdburl'): ### http://anonym.to/?http%3A%2F%2Fwww.imdb.com%2Ftitle%2Ftt0816711%2F
			parseMethod='re.compile'; parseTag='<strong>IMDb ID:</strong>[\n]\s+<a href="(.+?)">\d+</a>'
			if ('<strong>IMDb ID:</strong>' in html): rCheck=True
		elif (item=='imdbvotes'): ### 2,814
			parseMethod='re.compile'; parseTag='<strong>IMDb rating:</strong>[\n]\s+.+?\s+\((.+?) votes\)'
			if ('<strong>IMDb rating:</strong>' in html): rCheck=True
		elif (item=='duration'): ### 116 min
			parseMethod='re.compile'; parseTag='<strong>Duration:</strong>[\n]\s+(.+?)<'
			if ('<strong>Duration:</strong>' in html): rCheck=True
		elif (item=='duration2'):
			parseMethod='strip'; parseTag='<strong>Duration:</strong>'; parseTag2='<'
			if ('<strong>Duration:</strong>' in html): rCheck=True
		elif (item=='premiered'): ### June 21, 2013
			parseMethod='re.compile'; parseTag='<strong>Release Date:</strong>[\n]\s+(.+?)\s+[\n]\s+</div>'
			if ('<strong>Release Date:</strong>' in html): rCheck=True
		elif (item=='premiered2'):
			parseMethod='strip'; parseTag='<strong>Release Date:</strong>'; parseTag2='<'
			if ('<strong>Release Date:</strong>' in html): rCheck=True
		elif (item=='reelasedate'): ### June 21, 2013
			parseMethod='re.compile'; parseTag='<strong>Release Date:</strong>[\n]\s+(.+?)\s+[\n]\s+</div>'
			if ('<strong>Release Date:</strong>' in html): rCheck=True
		elif (item=='reelasedate2'):
			parseMethod='strip'; parseTag='<strong>Release Date:</strong>'; parseTag2='<'
			if ('<strong>Release Date:</strong>' in html): rCheck=True
		elif (item=='Votes'): ### 86
			parseMethod='re.compile'; parseTag='<strong>Solar rating:</strong>[\n]\s+<span class="js-votes"[\n]\s+>(\d+\s+votes</span>'
			if ('<strong>Solar rating:</strong>' in html) and ('<span class="js-votes"' in html) and ('votes</span>' in html): rCheck=True
		elif (item=='coverimage'): ### http://static.solarmovie.so/images/movies/0460681_150x220.jpg
			parseMethod='re.search'; parseTag='coverImage">.+?src="(.+?)"'
			if ('coverImage">' in html): rCheck=True
		elif (item=='season'): ### 
			parseMethod='re.search'; parseTag="toggleSeason\('(\d+)'\)"
			if ('toggleSeason' in html): rCheck=True
		elif (item=='seasons'): ### 
			parseMethod='re.search.group'; parseTag="toggleSeason\('(\d+)'\)"
			if ('toggleSeason' in html): rCheck=True
		elif (item=='episode'): ### 
			parseMethod='re.compile'; parseTag='<span class="epname">[\n].+?<a href="(.+?)"[\n]\s+title=".+?">(.+?)</a>[\n]\s+<a href="/.+?/season-(\d+)/episode-(\d+)/" class=".+?">[\n]\s+(\d+) links</a>'
			if ('<span class="epname">' in html) and (' links</a>' in html): rCheck=True
		elif (item=='episodes'): ### 
			parseMethod='re.compile.group'; parseTag='<span class="epname">[\n].+?<a href="(.+?)"[\n]\s+title=".+?">(.+?)</a>[\n]\s+<a href="/.+?/season-(\d+)/episode-(\d+)/" class=".+?">[\n]\s+(\d+) links</a>'
			if ('<span class="epname">' in html): rCheck=True
		else: rCheck=False
		### Year
		#                    Fantasy</a>                                    produced in
		#        <a href="/tv/watch-tv-shows-2005.html">
		#                2005</a>
		### Country
		#                    [<a href="/tv/tv-shows-from-usa.html">USA</a>]
		### Latest Episode
		#            <div class="mediaDescription latestTvEpisode">
		#        <h5>Latest Episode:
		#            <a href="/tv/supernatural-2005/season-8/episode-23/">
		#                Sacrifice                (<span>s08e23</span>)</a>
		#              <em class="releaseDate">May 15, 2013</em>
		#        </h5>
		#<p id="plot_476403">Sam and Dean capture Crowley to finish the trials and close the gates of Hell. Castiel and Metatron continue the trials to close the gates of Heaven. Sam is left with a huge decision.</p>
		#                        </div>
		### Genres
		#<meta name="description" content="Watch full The Heat movie produced in 2013. Genres are Comedy, Crime, Action." />
		deb('rCheck',str(rCheck))
		if (rCheck==True): ## Trying to do away with errors for results that dont contain the requested information.
			if (parseMethod=='re.compile2'): ## returns 2nd result
				try: results[item]=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[1].strip()
				except: results[item]=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0].strip()
				resultCnt=resultCnt+1
			elif (parseMethod=='re.compile'): ## returns 1st result
				resultCnt=resultCnt+1; results[item]=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0].strip()
			elif (parseMethod=='re.compile.group'): ## returns a group of results
				resultCnt=resultCnt+1; results[item]=re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)
			elif (parseMethod=='split'):
				resultCnt=resultCnt+1; results[item]=(((html.split(parseTag)[1])).split(parseTag2)[0]).strip()
			elif (parseMethod=='re.search2'): ## returns 2nd result
				resultCnt=resultCnt+1; match=re.search(parseTag, html, re.IGNORECASE | re.MULTILINE | re.DOTALL); results[item]=match.group(2)
			elif (parseMethod=='re.search'): ## returns 1st result
				resultCnt=resultCnt+1; match=re.search(parseTag, html, re.IGNORECASE | re.MULTILINE | re.DOTALL); results[item]=match.group(1)
			elif (parseMethod=='re.search.group'): ## returns a group of results
				resultCnt=resultCnt+1; match=re.search(parseTag, html, re.IGNORECASE | re.MULTILINE | re.DOTALL); results[item]=match.group()
			else: 
				resultCnt=resultCnt+1; results[item]=''
		else: 
			resultCnt=resultCnt+1; results[item]=''
	if debugging==True: print results
	return results

def Library_SaveTo_TV(section,url,img,name,year,country,season_number,episode_number,episode_title):
	##def listEpisodes(section, url, img='', season='') #_param['img']
	show_name=name
	xbmcplugin.setContent( int( sys.argv[1] ), 'episodes' ); WhereAmI('@ the Episodes List for TV Show -- url: %s' % url); html=net.http_GET(url).content
	if (html=='') or (html=='none') or (html==None):
		if (_debugging==True): print 'Html is empty.'
		return
	if (img==''):
		match=re.search( 'coverImage">.+?src="(.+?)"', html, re.IGNORECASE | re.MULTILINE | re.DOTALL); img=match.group(1)
	episodes=re.compile('<span class="epname">[\n].+?<a href="(.+?)"[\n]\s+title=".+?">(.+?)</a>[\n]\s+<a href="/.+?/season-(\d+)/episode-(\d+)/" class=".+?">[\n]\s+(\d+) links</a>', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(html) #; if (_debugging==True): print episodes
	if not episodes: 
		if (_debugging==True): print 'couldn\'t find episodes'
		return
	if (_param['thetvdb_series_id']=='') or (_param['thetvdb_series_id']=='none') or (_param['thetvdb_series_id']==None) or (_param['thetvdb_series_id']==False): thetvdb_episodes=None
	else: thetvdb_episodes=thetvdb_com_episodes2(_param['thetvdb_series_id'])
	#print 'thetvdb_episodes',thetvdb_episodes
	woot=False
	for ep_url, episode_name, season_number, episode_number, num_links in episodes:
		labs={}; s_no=season_number; e_no=episode_number
		if (int(episode_number) > -1) and (int(episode_number) < 10): episode_number='0'+episode_number
		labs['thumbnail']=img; labs['fanart']=_param['fanart']
		labs['EpisodeTitle']=episode_name #; labs['ShowTitle']=''
		labs['title']=season_number+'x'+episode_number+' - '+episode_name+'  [[I]'+num_links+' Links [/I]]'
		ep_url=_domain_url+ep_url; episode_name=messupText(episode_name,True,True,True,True)
		if (thetvdb_episodes==None) or (_param['thetvdb_series_id']==None) or (_param['thetvdb_series_id']==False) or (_param['thetvdb_series_id'] is not '') or (_param['thetvdb_series_id']=='none'): t=''
		if (thetvdb_episodes):
			for db_ep_url, db_sxe_no, db_ep_url2, db_ep_name, db_dateYear, db_dateMonth, db_dateDay, db_hasImage in thetvdb_episodes:
				db_ep_url=ps('meta.tv.domain')+db_ep_url
				db_ep_url2=ps('meta.tv.domain')+db_ep_url2
				if (db_sxe_no.strip()==(s_no+' x '+e_no)):
					if ('Episode #' in episode_name): episode_name=db_ep_name.strip()
					labs['Premeired']=labs['DateAired']=labs['Date']=db_dateYear+'-'+db_dateMonth+'-'+db_dateDay
					labs['year']=db_dateYear; labs['month']=db_dateMonth; labs['day']=db_dateDay
					(db_thumb,labs['thetvdb_series_id'],labs['thetvdb_episode_id']) = Episode__get_thumb(db_ep_url2.strip(),img)
					if (check_ifUrl_isHTML(db_thumb)==True): labs['thumbnail']=db_thumb
					labs['title']=cFL(season_number+cFL('x',ps('cFL_color4'))+episode_number,ps('cFL_color5'))+' - '+cFL(episode_name,ps('cFL_color4'))+cFL('  [[I]'+cFL(num_links+' Links ',ps('cFL_color3'))+'[/I]]',ps('cFL_color'))
					ep_html=mGetItemPage(db_ep_url2); deb('thetvdb - episode - url',db_ep_url2)
					deb('Length of ep_html',str(len(ep_html)))
					if (ep_html is not None) or (ep_html is not False) or (ep_html is not '') or (ep_html is not 'none'):
						labs['PlotOutline']=labs['plot']=mdGetTV(ep_html,['thetvdb.episode.overview1'])['thetvdb.episode.overview1']
		contextMenuItems=[]; labs['season']=season_number; labs['episode']=episode_number
		#contextMenuItems.append((ps('cMI.showinfo.name'),ps('cMI.showinfo.url')))
		#contextMenuItems.append(('Add - Library','XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&showtitle=%s&showyear=%s&url=%s&img=%s&season=%s&episode=%s&episodetitle=%s)' % ( sys.argv[0],'LibrarySaveEpisode',section, urllib.quote_plus(_param['title']), urllib.quote_plus(_param['showtitle']), urllib.quote_plus(_param['year']), urllib.quote_plus(ep_url), urllib.quote_plus(labs['thumbnail']), urllib.quote_plus(season_number), urllib.quote_plus(episode_number), urllib.quote_plus(episode_name) )))
		labs['title']=messupText(labs['title'],True,True,True,False)
		deb('Episode Name',labs['title'])
		deb('episode thumbnail',labs['thumbnail'])
		#
		Library_SaveTo_Episode(ep_url,labs['thumbnail'],show_name,year,country,season_number,episode_number,episode_name)
		### Library_SaveTo_Episode(url,iconimage,name,year,country,season_number,episode_number,episode_title)
		#
		#if (season==season_number) or (season==''): _addon.add_directory({'mode': 'GetLinks', 'year': _param['year'], 'section': section, 'img': img, 'url': ep_url, 'season': season_number, 'episode': episode_number, 'episodetitle': episode_name}, labs, img=labs['thumbnail'], fanart=labs['fanart'], contextmenu_items=contextMenuItems)
	set_view('episodes',ps('setview.episodes')); eod()


### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Menus #####

def Menu_BrowseByGenre(section=_default_section_):
	url=''; WhereAmI('@ the Genre Menu')#print 'Browse by genres screen'
	browsebyImg=checkImgLocal(art('genre','.jpg'))
	ItemCount=len(GENRES) # , total_items=ItemCount
	for genre in GENRES:
		img=''; imgName=genre #; pre='http://icons.iconarchive.com/icons/sirubico/movie-genre/128/'
		if (img==''): img=checkImgLocal(os.path.join(ps('special.home'),'addons','skin.primal','extras','moviegenresposter',imgName+'.jpg'))
		if (img==''): img=checkImgLocal(os.path.join(ps('special.home'),'addons','skin.tangency','extras','moviegenresposter',imgName+'.jpg'))
		if (img==''): img=checkImgLocal(os.path.join(ps('special.home'),'addons','plugin.video.1channel','art','themes','PrimeWire',imgName+'.png'))
		if (img==''): img=checkImgLocal(os.path.join(ps('special.home'),'addons','plugin.video.1channel','art','themes','Glossy_Black',imgName+'.png'))
		if (img=='') and (browsebyImg is not ''): img=browsebyImg
		#C:\Users\HIGHWAY 99\AppData\Roaming\XBMC\addons\plugin.video.1channel\art\themes\PrimeWire
		#
		#
		#if (img==''): img=checkImgLocal(os.path.join('special://home/addons/','',imgName+'.jpg'))
		#if (img==''): img=checkImgUrl(pre+imgName+'-5-icon.png')
		#if (img==''): img=checkImgUrl(pre+imgName+'-4-icon.png')
		#if (img==''): img=checkImgUrl(pre+imgName+'-3-icon.png')
		#if (img==''): img=checkImgUrl(pre+imgName+'-2-icon.png')
		#if (img==''): img=checkImgUrl(pre+imgName+'-1-icon.png')
		#if (img==''): img=checkImgUrl(pre+imgName+'-icon.png')
		#if (img==''): img=checkImgUrl(''+genre+'-2-icon.png')
		if (img==''): img=_artSun
		url=ps('_category_url') % ('MovieGenre='+genre.replace(' ','+').replace('&','%26')+'&search=Find+a+Movie')
		deb('url',url)
		_addon.add_directory({'section': section,'mode': 'GetTitles','url': url,'genre': genre,'bygenre': genre,'pageno': '1','pagecount': addst('pages')}, {'title':  genre},img=img,fanart=_artFanart, total_items=ItemCount)
	set_view('list',addst('default-view')); eod()

def Menu_BrowseByYear(section=_default_section_):
	url=''; WhereAmI('@ the Genre Menu')#print 'Browse by genres screen'
	browsebyImg=checkImgLocal(art('year','.gif'))
	ItemCount=len(ps('YEARS')) # , total_items=ItemCount
	for genre in ps('YEARS'):
		img=''; imgName=genre #; pre='http://icons.iconarchive.com/icons/sirubico/movie-genre/128/'
		if (img=='') and (browsebyImg is not ''): img=browsebyImg
		if (img==''): img=_artSun
		url=ps('_category_url') % ('MovieYear='+genre.replace(' ','+').replace('&','%26')+'&search=Find+a+Movie')
		deb('url',url)
		_addon.add_directory({'section': section,'mode': 'GetTitles','url': url,'genre': genre,'bygenre': genre,'pageno': '1','pagecount': addst('pages')}, {'title':  genre},img=img,fanart=_artFanart, total_items=ItemCount)
	set_view('list',addst('default-view')); eod()

def Menu_BrowseByRating(section=_default_section_):
	url=''; WhereAmI('@ the Genre Menu')#print 'Browse by genres screen'
	ItemCount=len(ps('RATINGS')) # , total_items=ItemCount
	for genre in ps('RATINGS'):
		url=ps('_category_url') % ('MovieRating='+genre.replace(' ','+').replace('&','%26')+'&search=Find+a+Movie')
		deb('url',url)
		_addon.add_directory({'section': section,'mode': 'GetTitles','url': url}, {'title':  genre},total_items=ItemCount)
	set_view('list',addst('default-view')); eod()

def Menu_BrowseByScore(section=_default_section_):
	url=''; WhereAmI('@ the Genre Menu')#print 'Browse by genres screen'
	ItemCount=len(ps('SCORES')) # , total_items=ItemCount
	for genre in ps('SCORES'):
		url=ps('_category_url') % ('MovieScore='+genre.replace(' ','+').replace('&','%26')+'&search=Find+a+Movie')
		deb('url',url)
		_addon.add_directory({'section': section,'mode': 'GetTitles','url': url}, {'title':  genre},total_items=ItemCount)
	set_view('list',addst('default-view')); eod()

##def listItems(section=_default_section_, url='', html='', episode=False, startPage='1', numOfPages='1', genre='', year='', stitle=''): # List: Movies or TV Shows
def listItems(section=_default_section_, url='', startPage='1', numOfPages='1', genre='', year='', stitle='', season='', episode='', html='', chck=''): # List: Movies or TV Shows
	if (url==''): return
	#if (chck=='Latest'): url=url+chr(35)+'latest'
	WhereAmI('@ the Item List -- url: %s' % url)
	html=''
	try: html=net.http_GET(url).content
	except: 
		try: html=getURL(url)
		except: 
			try: html=getURLr(url,_domain_url)
			except: html=''
	#print html_
	if (html=='') or (html=='none') or (html==None): 
		deb('Error','Problem with page'); deadNote('Results:  '+section,'No results were found.')
		return
	deb('Length of HTML',str(len(html)))
	html=messupText(html,True,True,True,False)
	#html=ParseDescription(html); html=remove_accents(html) #if (_debugging==True): print html
	try:		iitems=re.compile('<a href="MovieDetails\.cfm\?Movie=(\d+)"\s*>\s*<img\s*src="posters.+?.jpg"\s*alt=".*?"\s*/>\s*</a>\s*\n\s*<h2>(.+?)[\n]\s*Score').findall(html)
	except:	iitems=None
	if (iitems is not None):
		ItemCount=len(iitems)
		for item_id, item_name in iitems:
			contextMenuItems=[]; labs={}; labs['title']=item_name
			#item_name=ParseDescription(HTMLParser.HTMLParser().unescape(item_name)); item_name=item_name.encode('ascii', 'ignore'); item_name=item_name.decode('iso-8859-1'); item_name=item_name.strip() #; item_name = remove_accents(item_name)
			#item_name=_addon.decode(name); item_name=_addon.unescape(name)
			pars={'mode': 'PlayVideo', 'section': section, 'url': ps('_play_url') % item_id, 'img': ps('_image_url') % item_id, 'title': item_name }
			year='0'; 
			contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(item_name),year,urllib.quote_plus(ps('_image_url') % item_id),urllib.quote_plus(ps('_image_url') % item_id),'','','',urllib.quote_plus(ps('_play_url') % item_id), '' )))
			contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.2.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(item_name),year,urllib.quote_plus(ps('_image_url') % item_id),urllib.quote_plus(ps('_image_url') % item_id),'','','',urllib.quote_plus(ps('_play_url') % item_id), '2' )))
			_addon.add_directory(pars, labs, img=ps('_image_url') % item_id, fanart=ps('_image_url') % item_id, contextmenu_items=contextMenuItems, total_items=ItemCount)
	set_view('movies',addst('movies-view')); eod()





def Menu_LoadCategories(section=_default_section_): #Categories
	WhereAmI('@ the Category Menu')
	### ###################################################################################################################################################################################################################################
	### ###################################################################################################################################################################################################################################
	### 
	set_view('list',addst('default-view')); eod()
	### 
	### 

def Menu_MainMenu(): #The Main Menu
	WhereAmI('@ the Main Menu')
	_addon.add_directory({'mode': 'GetTitles', 'section': ps('section.movie'), 'url': 'http://moviefork.com/Results.cfm?LatestMovies=Yes'}, {'title': cFL('L',ps('cFL_color'))+'atest Movies'}, img=art('movies'), fanart=_artFanart)
	_addon.add_directory({'section': ps('section.movie'), 'mode': 'FavoritesList'},	 										{'title':  cFL('F',ps('cFL_color'))+'avorites '+addst('fav.movies.1.name')},fanart=_artFanart,img=art('movies'))
	_addon.add_directory({'section': ps('section.movie'), 'mode': 'FavoritesList', 	'subfav': '2'},	 		{'title':  cFL('F',ps('cFL_color'))+'avorites '+addst('fav.movies.2.name')},fanart=_artFanart,img=art('movies'))
	_addon.add_directory({'section': ps('section.movie'), 'mode': 'BrowseGenre'},	 				{'title':  cFL('G',ps('cFL_color'))+'enre'}, 			fanart=_artFanart,img=art('genre','.jpg'))
	_addon.add_directory({'section': ps('section.movie'), 'mode': 'BrowseYear'}, 					{'title':  cFL('D',ps('cFL_color'))+'ecade'}, 			fanart=_artFanart,img=art('year','.gif'))
	_addon.add_directory({'section': ps('section.movie'), 'mode': 'BrowseRating'},	 			{'title':  cFL('R',ps('cFL_color'))+'ating'}, 			fanart=_artFanart,img=_artSun)
	_addon.add_directory({'section': ps('section.movie'), 'mode': 'BrowseScore'},	 				{'title':  cFL('S',ps('cFL_color'))+'core'}, 			fanart=_artFanart,img=_artDead)
	##_addon.add_directory({'mode': 'LoadCategories', 'section': ps('section.movie')},		{'title':  cFL('M',ps('cFL_color'))+'ovies'}  ,img=art('movies')				,fanart=_artFanart)
	##_addon.add_directory({'mode': 'LoadCategories', 'section': ps('section.tv')}, 			{'title':  cFL('T',ps('cFL_color'))+'V Shows'},img=art('television')		,fanart=_artFanart)
	##_addon.add_directory({'mode': 'LoadCategories', 'section': ps('section.trailers')},	{'title':  cFL('C',ps('cFL_color'))+'oming Soon'},img=ps('img.comingsoon'),fanart=_artFanart)
	##_addon.add_directory({'mode': 'LoadCategories', 'section': ps('section.users')},		{'title':  cFL('U',ps('cFL_color'))+'sers'}		,img=ps('img.usersection'),fanart=_artFanart)
	##_addon.add_directory({'mode': 'GetLatestSearches', 'section': 'Both'},		{'title':  cFL('L',ps('cFL_color'))+'atest Searches'}		,img=art('icon-search')		,fanart=_artFanart)
	#_addon.add_directory({'mode': 'ResolverSettings'}, {'title':  cFL('U',ps('cFL_color'))+'rl-Resolver Settings'},is_folder=False		,img=art('turtle','.jpg')	,fanart=_artFanart)
	_addon.add_directory({'mode': 'YoutubeSettings'}, {'title':  cFL('Y',ps('cFL_color'))+'outube Settings'},is_folder=False		,img=ps('art_youtube')	,fanart=_artFanart)
	_addon.add_directory({'mode': 'Settings'}, 				 {'title':  cFL('P',ps('cFL_color'))+'lugin Settings'}			,is_folder=False		,img=_artDead							,fanart=_artFanart)
	##_addon.add_directory({'mode': 'DownloadStop'}, 		 {'title':  cFL('S',ps('cFL_color'))+'top Current Download'},is_folder=False		,img=_artDead							,fanart=_artFanart)
	#_addon.add_directory({'mode': 'TextBoxFile',  'title': "[COLOR cornflowerblue]Local Change Log:[/COLOR]  %s"  % (__plugin__), 'url': ps('changelog.local')}, 	{'title': cFL('L',ps('cFL_color'))+'ocal Change Log'},					img=art('thechangelog','.jpg'), is_folder=False ,fanart=_artFanart)
	#_addon.add_directory({'mode': 'TextBoxUrl',   'title': "[COLOR cornflowerblue]Latest Change Log:[/COLOR]  %s" % (__plugin__), 'url': ps('changelog.url')}, 		{'title': cFL('L',ps('cFL_color'))+'atest Online Change Log'},	img=art('thechangelog','.jpg'), is_folder=False ,fanart=_artFanart)
	#_addon.add_directory({'mode': 'TextBoxUrl',   'title': "[COLOR cornflowerblue]Latest News:[/COLOR]  %s"       % (__plugin__), 'url': ps('news.url')}, 				{'title': cFL('L',ps('cFL_color'))+'atest Online News'},				img=_art404										, is_folder=False ,fanart=_artFanart)
	##_addon.add_directory({'mode': 'LatestThreads','title': "[COLOR cornflowerblue]Latest Threads[/COLOR]", 'url': ps('LatestThreads.url')}, 											{'title': cFL('L',ps('cFL_color'))+'atest Threads'},						img=_art404										, is_folder=False ,fanart=_artFanart)
	##_addon.add_directory({'mode': 'PrivacyPolicy','title': "", 'url': ''}, 																																												{'title': cFL('P',ps('cFL_color'))+'rivacy Policy'},						img=_art404										, is_folder=False ,fanart=_artFanart)
	##_addon.add_directory({'mode': 'TermsOfService','title': "", 'url': ''}, 																																											{'title': cFL('T',ps('cFL_color'))+'erms of Service'},					img=_art404										, is_folder=False ,fanart=_artFanart)
	### ############ 
	set_view('list',addst('default-view')); eod()
	### ############ 
	### _addon.show_countdown(9000,'Testing','Working...') ### Time seems to be in seconds.

##### /\ ##### Menus #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Favorites #####
def fav__empty(section,subfav=''):
  WhereAmI('@ Favorites - Empty - %s%s' % (section,subfav)); favs=[]; cache.set('favs_'+section+subfav+'__', str(favs)); sunNote(bFL('Favorites'),bFL('Your Favorites Have Been Wiped Clean. Bye Bye.'))
def fav__remove(section,name,year,subfav=''):
	WhereAmI('@ Favorites - Remove - %s%s' % (section,subfav)); deb('fav__remove() '+section,name+'  ('+year+')'); saved_favs=cache.get('favs_'+section+subfav+'__'); tf=False
	if saved_favs:
		favs=eval(saved_favs)
		if favs:
			for (_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid) in favs: 
				if (name==_name) and (year==_year):
					favs.remove((_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid)); cache.set('favs_'+section+subfav+'__', str(favs)); tf=True; sunNote(bFL(name.upper()+'  ('+year+')'),bFL('Removed from Favorites')); deb(name+'  ('+year+')','Removed from Favorites. (Hopefully)'); xbmc.executebuiltin("XBMC.Container.Refresh"); return
			if (tf==False): sunNote(bFL(name.upper()),bFL('not found in your Favorites'))
		else: sunNote(bFL(name.upper()+'  ('+year+')'),bFL('not found in your Favorites'))
def fav__add(section,name,year='',img=_art150,fanart=_artFanart,subfav=''):
	WhereAmI('@ Favorites - Add - %s%s' % (section,subfav))
	if (debugging==True): print 'fav__add()',section,name+'  ('+year+')',img,fanart
	saved_favs=cache.get('favs_'+section+subfav+'__'); favs=[]; fav_found=False
	if saved_favs:
		if (debugging==True): print saved_favs
		favs=eval(saved_favs)
		if favs:
			if (debugging==True): print favs
			for (_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid) in favs:
				if (name==_name) and (year==_year): 
					fav_found=True; sunNote(bFL(section+':  '+name.upper()+'  ('+year+')'),bFL('Already in your Favorites')); return
	if   (section==ps('section.tv')):    favs.append((name,year,img,fanart,_param['country'],_param['url'],_param['plot'],_param['genre'],_param['dbid']))
	elif (section==ps('section.movie')): favs.append((name,year,img,fanart,_param['country'],_param['url'],_param['plot'],_param['genre'],''))
	cache.set('favs_'+section+subfav+'__', str(favs)); sunNote(bFL(name+'  ('+year+')'),bFL('Added to Favorites'))
def fav__list(section,subfav=''):
	WhereAmI('@ Favorites - List - %s%s' % (section,subfav)); saved_favs=cache.get('favs_'+section+subfav+'__'); favs=[]
	if saved_favs:
		if (debugging==True): print saved_favs
		favs=sorted(eval(saved_favs), key=lambda fav: (fav[1],fav[0]),reverse=True)
		ItemCount=len(favs) # , total_items=ItemCount
		if favs:
			#if   (section==ps('section.tv')): 		xbmcplugin.setContent( int( sys.argv[1] ), 'tvshows' )
			#elif (section==ps('section.movie')): 	xbmcplugin.setContent( int( sys.argv[1] ), 'movies' )
			for (name,year,img,fanart,country,url,plot,genre,dbid) in favs:
				if (debugging==True): print '----------------------------'
				if (debugging==True): print name,year,img,fanart,country,url,plot,genre,dbid #,pars,labs
				contextMenuItems=[]; labs2={}; labs2['fanart']=''
				if   (section==ps('section.tv')):
					return
				elif (section==ps('section.movie')):
					#labs2['title']=cFL(name+'  ('+cFL(year,ps('cFL_color2'))+')',ps('cFL_color')); 
					labs2['title']=cFL(name[0:1],ps('cFL_color2'))+cFL(name[1:],ps('cFL_color')); 
					labs2['image']=img; labs2['fanart']=fanart; labs2['ShowTitle']=name; labs2['year']=year; pars2={'mode': 'PlayVideo', 'section': section, 'url': url, 'img': img, 'image': img, 'fanart': fanart, 'title': name, 'year': year }; labs2['plot']=plot
					##### Right Click Menu for: TV #####
					contextMenuItems.append((ps('cMI.showinfo.name'),ps('cMI.showinfo.url')))
					#contextMenuItems.append((ps('cMI.favorites.tv.remove.name'), 	   ps('cMI.favorites.movie.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),year,urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url), '' )))
					contextMenuItems.append((ps('cMI.favorites.tv.remove.name'),ps('cMI.favorites.movie.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),year,urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url),subfav )))
					if (fanart is not ''): contextMenuItems.append(('Download Wallpaper', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url( { 'mode': 'Download' , 'section': ps('section.wallpaper') , 'studio': name+' ('+year+')' , 'img': img , 'url': fanart } ) ))
					##### Right Click Menu for: TV ##### /\ #####
					#pars={'mode': 'PlayVideo', 'section': section, 'url': ps('_play_url') % item_id, 'img': ps('_image_url') % item_id, 'title': item_name }
					#try: _addon.add_directory(pars2, labs2, img=ps('_image_url') % item_id, fanart=ps('_image_url') % item_id, contextmenu_items=contextMenuItems, total_items=ItemCount)
					try: _addon.add_directory(pars2, labs2, img=img, fanart=fanart, contextmenu_items=contextMenuItems)
					except: deb('Error Listing Item',name+'  ('+year+')')
			if   (section==ps('section.tv')): 		set_view('tvshows',ps('setview.tv')			,True)
			elif (section==ps('section.movie')): 	set_view('movies' ,ps('setview.movies')	,True)
		else: sunNote('Favorites:  '+section,'No favorites found *'); set_view('list',addst('default-view')); eod(); return
	else: sunNote('Favorites:  '+section,'No favorites found **'); set_view('list',addst('default-view')); eod(); return
	#set_view('list',addst('default-view')); 
	eod()

def ChangeFanartUpdate(section,subfav,fanart,dbid):
	WhereAmI('@ Favorites - Update Fanart - %s%s' % (section,subfav))
	saved_favs=cache.get('favs_'+section+subfav+'__'); favs=[]; favs_new=[]; fav_found=False; name=''; year=''
	if saved_favs:
		if (debugging==True): print saved_favs
		favs=eval(saved_favs)
		if favs:
			for (_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid) in favs:
				if (dbid==_dbid):	favs_new.append((_name,_year,_img, fanart,_country,_url,_plot,_genre,_dbid)); name=_name; year=_year
				else:							favs_new.append((_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid))
			cache.set('favs_'+section+subfav+'__', str(favs_new)); sunNote(bFL(name+'  ('+year+')'),bFL('Updated Fanart'))
	eod(); #xbmc.executebuiltin('XBMC.Container.Update(%s)' % _addon.build_plugin_url({'mode': 'FavoritesList' , 'section': section , 'subfav': subfav}))

def ChangeFanartList(section,subfav,dbid,current,img,title):
	WhereAmI('@ Favorites - List - %s%s - %s' % (section,subfav,dbid)); 
	if   (section==ps('section.tv')):
		url=ps('meta.tv.fanart.all.url') % dbid
		html=mGetItemPage(url)
		deb('length of HTML',str(len(html)))
		try:		iitems=re.compile(ps('meta.tv.fanart.all.match')).findall(html)
		except:	iitems=None
		if (iitems==None) or (iitems==''): deb('Error','No Items Found.'); return
		ItemCount=len(iitems) # , total_items=ItemCount
		deb('Items Found',str(ItemCount))
		parsC={'section':section,'subfav':subfav,'mode':'ChangeFanartUpdate','url':current, 'title': dbid}
		#_addon.add_directory(parsC,{ 'title': title, 'studio': title },img=img,fanart=current)
		_addon.add_directory(parsC,{ 'title': title, 'studio': title },img=current,fanart=current)
		#_addon.add_item(parsC,{ 'title': title, 'studio': title },img=img,fanart=current)
		#_addon.add_directory({'mode':'test'}, {'title':title}, img=img)
		#_addon.add_directory({'mode':'test'}, {'title':'title'})
		#_addon.end_of_directory(); return
		iitems=sorted(iitems, key=lambda item: item[0], reverse=False)
		#print iitems
		for fanart_url,fanart_name in iitems:
			fanart_url=ps('meta.tv.fanart.all.prefix')+fanart_url
			pars={ 'section': section, 'subfav': subfav, 'mode': 'ChangeFanartUpdate', 'url': fanart_url, 'title': dbid }
			deb('fanart url ',fanart_url); deb('fanart name',fanart_name); #print pars
			#_addon.add_directory(pars, {'title':'Fanart No. '+fanart_name}, img=img, fanart=fanart_url, total_items=ItemCount)
			_addon.add_directory(pars, {'title':'Fanart No. '+fanart_name}, img=fanart_url, fanart=fanart_url, total_items=ItemCount)
			#_addon.add_directory(pars, {'title':'Fanart No. '+fanart_name}, img=img, fanart=fanart_url)
			#_addon.add_directory(pars, {'title':'Fanart No. '+str(fanart_name)})
		#eod()
		#sunNote('Testing - '+section,'lala a la la la!')
		set_view('list',addst('default-view')); 
		eod()
		#xbmc.executebuiltin("XBMC.Container.Refresh")
	elif (section==ps('section.movie')):
		url=''
		return
	else: return
	set_view('list',addst('default-view')); eod()


##### /\ ##### Favorites #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Search #####
def doSearchNormal (section,title=''):
	if (section=='tv'): SearchPrefix=ps('domain.search.tv')
	else: SearchPrefix=ps('domain.search.movie')
	if (title==''):
		title=showkeyboard(txtMessage=title,txtHeader="Title:  ("+section+")")
		if (title=='') or (title=='none') or (title==None) or (title==False): return
	_param['url']=SearchPrefix+title; deb('Searching for',_param['url']); listItems(section, _param['url'], _param['pageno'], addst('pages'), _param['genre'], _param['year'], _param['title'])

def doSearchAdvanced (section,title=''):
	txtHeader='Advanced Search'; options={}; r= -1
	#########################
	options[ps('AdvSearch.tags.1')]				=''
	options[ps('AdvSearch.tags.2')]				=''
	options[ps('AdvSearch.tags.3')]				=''
	options[ps('AdvSearch.tags.4')]				='0'
	options[ps('AdvSearch.tags.5')]				=str(ps('BrowseByYear.earliestyear'))
	options[ps('AdvSearch.tags.6')]				=str(int(datetime.date.today().strftime("%Y"))+1)
	options[ps('AdvSearch.tags.7')]				=''						### &q[genre][]=2&q[genre][]=13
	#########################
	options['startPage']		='1'
	options['numOfPages']		=addst('pages') #'1'
	#########################
	if   (section==ps('section.tv')   ): options[ps('AdvSearch.tags.0')]='1'; options['url']=ps('AdvSearch.url.tv')
	elif (section==ps('section.movie')): options[ps('AdvSearch.tags.0')]='0'; options['url']=ps('AdvSearch.url.movie')
	else: 															 options[ps('AdvSearch.tags.0')]='0'; options['url']=ps('AdvSearch.url.movie')
	options['url']+='['+ps('AdvSearch.tags.0')+']='+options[ps('AdvSearch.tags.0')]; _param['url']=options['url']
	#options['']=''
	#options['']=''
	### [year_from]=2013&q[year_to]=2014&q[country]=132&q[genre][]=2&q[genre][]=13
	### http://www.solarmovie.so/advanced-search/?q[title]=maveric&q[is_series]=0&q[actor]=&q[description]=&q[year_from]=2013&q[year_to]=2014&q[country]=0
	### http://www.solarmovie.so/advanced-search/?q[title]=maveric&q[is_series]=0&q[actor]=testb&q[description]=testa&q[year_from]=2013&q[year_to]=2014&q[country]=132&q[genre][]=2&q[genre][]=13
	while (r is not 0):
		option_list=[]
		option_list.append(																						 ps('AdvSearch.menu.0'))
		if (''==options[ps('AdvSearch.tags.1')]): 	option_list.append(ps('AdvSearch.menu.1'))
		else:																				option_list.append(ps('AdvSearch.menu.1')+':  '+options[ps('AdvSearch.tags.1')])
		if (''==options[ps('AdvSearch.tags.2')]): 	option_list.append(ps('AdvSearch.menu.2'))
		else:																				option_list.append(ps('AdvSearch.menu.2')+':  '+options[ps('AdvSearch.tags.2')])
		if (''==options[ps('AdvSearch.tags.3')]): 	option_list.append(ps('AdvSearch.menu.3'))
		else:																				option_list.append(ps('AdvSearch.menu.3')+':  '+options[ps('AdvSearch.tags.3')])
		if (''==options[ps('AdvSearch.tags.4')]): 	option_list.append(ps('AdvSearch.menu.4'))
		else:																				option_list.append(ps('AdvSearch.menu.4')+':  '+options[ps('AdvSearch.tags.4')])
		if (''==options[ps('AdvSearch.tags.5')]): 	option_list.append(ps('AdvSearch.menu.5'))
		else:																				option_list.append(ps('AdvSearch.menu.5')+':  '+options[ps('AdvSearch.tags.5')])
		if (''==options[ps('AdvSearch.tags.6')]): 	option_list.append(ps('AdvSearch.menu.6'))
		else:																				option_list.append(ps('AdvSearch.menu.6')+':  '+options[ps('AdvSearch.tags.6')])
		if (''==options[ps('AdvSearch.tags.7')]): 	option_list.append(ps('AdvSearch.menu.7'))
		else:																				option_list.append(ps('AdvSearch.menu.7')+':  '+options[ps('AdvSearch.tags.7')])
		option_list.append(																						 ps('AdvSearch.menu.8'))
		r=askSelection(option_list,txtHeader)
		if   (r==0): ### Do Advanced Search
			_param['url']+='&q['+ps('AdvSearch.tags.1')+']='+options[ps('AdvSearch.tags.1')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.2')+']='+options[ps('AdvSearch.tags.2')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.3')+']='+options[ps('AdvSearch.tags.3')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.5')+']='+options[ps('AdvSearch.tags.5')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.6')+']='+options[ps('AdvSearch.tags.6')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.4')+']='+options[ps('AdvSearch.tags.4')]; 
			### if (options['year_to'] is not ''): _param['url']+='&q[year_to]='+options['year_to']; 
			deb('Advanced Searching',_param['url'])
			listItems(section, _param['url'], startPage=options['startPage'], numOfPages=options['numOfPages'], chck='AdvancedSearch')
			### listItems(section, _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'],chck='AdvancedSearch')
			### listItems(section=, url=, startPage='1', numOfPages='1', genre='', year='', stitle='', season='', episode='', html='', chck=''): # List: Movies or TV Shows
		elif (r==1): ### Change Title
			r2=showkeyboard(txtMessage=options[ps('AdvSearch.tags.1')],txtHeader="Title:  "+options[ps('AdvSearch.tags.1')],passwordField=False)
			if (r2 is not False): options[ps('AdvSearch.tags.1')]=r2
		elif (r==2): ### Change Description
			r2=showkeyboard(txtMessage=options['description'],txtHeader="Description:  "+options['description'],passwordField=False)
			if (r2 is not False): options['description']=r2
		elif (r==3): ### Change Actor
			r2=showkeyboard(txtMessage=options[ps('AdvSearch.tags.2')],txtHeader="Actor:  "+options[ps('AdvSearch.tags.2')],passwordField=False)
			if (r2 is not False): options[ps('AdvSearch.tags.2')]=r2
		#elif (r==4): ### Change Country
		elif (r==5): ### Change Year From
			r2=dialogbox_number(Header='Year From:'+options[ps('AdvSearch.tags.5')],n='01/01/'+options[ps('AdvSearch.tags.5')],type=0)
			if (r2 is not False) and (len(r2)==4): options[ps('AdvSearch.tags.5')]=r2
			if (r2 is not False) and ('/' in r2):  options[ps('AdvSearch.tags.5')]=r2.split('/')[2] ## <<<
			if (r2 is not False) and ('-' in r2):  options[ps('AdvSearch.tags.5')]=r2.split('-')[2]
		elif (r==6): ### Change Year To
			r2=dialogbox_number(Header='Year To:'  +options[ps('AdvSearch.tags.6')],n='01/01/'+options[ps('AdvSearch.tags.6')],type=0)
			if (r2 is not False) and (len(r2)==4): options[ps('AdvSearch.tags.6')]=r2
			if (r2 is not False) and ('/' in r2):  options[ps('AdvSearch.tags.6')]=r2.split('/')[2] ## <<<
			if (r2 is not False) and ('-' in r2):  options[ps('AdvSearch.tags.6')]=r2.split('-')[2]
		#elif (r==7): ### Change Genre
		elif (r==8): ### Cancel Advanced Search
			eod(); return
		#elif (r== -1): ### escape // right click or such.
		#	eod(); return
		## 
		## 
	#
	#
	#
	eod()
	return



##### /\ ##### Search #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Modes #####
def check_mode(mode=''):
	deb('Mode',mode)
	if (mode=='') or (mode=='main') or (mode=='MainMenu'): Menu_MainMenu()
	elif (mode=='PlayVideo'): 						PlayVideo(_param['url'], _param['infoLabels'], _param['listitem'])
	elif (mode=='PlayTrailer'): 					PlayTrailer(_param['url'], _param['title'], _param['year'], _param['img'])
	elif (mode=='Settings'): 							_addon.addon.openSettings() #_plugin.openSettings()
	elif (mode=='ResolverSettings'): 			urlresolver.display_settings()
	elif (mode=='LoadCategories'): 				Menu_LoadCategories(_param['section'])
	#elif (mode=='BrowseAtoZ'): 					BrowseAtoZ(_param['section'])
	elif (mode=='BrowseYear'): 						Menu_BrowseByYear(_param['section'])
	elif (mode=='BrowseGenre'): 					Menu_BrowseByGenre(_param['section'])
	elif (mode=='BrowseRating'): 					Menu_BrowseByRating(_param['section'])
	elif (mode=='BrowseScore'): 					Menu_BrowseByScore(_param['section'])
	elif (mode=='BrowseCountry'): 				Menu_BrowseByCountry(_param['section'])
	#elif (mode=='BrowseLatest'): 				BrowseLatest(_param['section'])
	#elif (mode=='BrowsePopular'): 				BrowsePopular(_param['section'])
	#elif (mode=='GetResults'): 					GetResults(_param['section'], genre, letter, page)
	elif (mode=='GetTitles'): 						listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'])
	#elif (mode=='GetTitlesLatest'): 			listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.tv.latest.check'))
	#elif (mode=='GetTitlesLatestWatched'): listItems(_param['section'],_param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.tv.latest.watched.check'))
	#elif (mode=='GetTitlesPopular'): 			listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.tv.popular.all.check'))
	#elif (mode=='GetTitlesHDPopular'): 		listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.movies.popular.hd.check'))
	#elif (mode=='GetTitlesOtherPopular'): listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.movies.popular.other.check'))
	#elif (mode=='GetTitlesNewPopular'): 	listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.movies.popular.new.check'))
	#elif (mode=='GetLinks'): 							listLinks(_param['section'], _param['url'], showtitle=_param['showtitle'], showyear=_param['showyear'])
	#elif (mode=='GetSeasons'): 						listSeasons(_param['section'], _param['url'], _param['img'])
	#elif (mode=='GetEpisodes'): 					listEpisodes(_param['section'], _param['url'], _param['img'], _param['season'])
	elif (mode=='TextBoxFile'): 					TextBox2().load_file(_param['url'],_param['title']); eod()
	elif (mode=='TextBoxUrl'):  					TextBox2().load_url( _param['url'],_param['title']); eod()
	#elif (mode=='SearchForAirDates'):  		search_for_airdates(_param['title']); eod()
	elif (mode=='Search'):  							doSearchNormal(_param['section'],_param['title'])
	elif (mode=='AdvancedSearch'):  			doSearchAdvanced(_param['section'],_param['title'])
	elif (mode=='FavoritesList'):  		  	fav__list(_param['section'],_param['subfav'])
	elif (mode=='FavoritesEmpty'):  	 		fav__empty(_param['section'],_param['subfav'])
	elif (mode=='FavoritesRemove'):  			fav__remove(_param['section'],_param['title'],_param['year'],_param['subfav'])
	elif (mode=='FavoritesAdd'):  		  	fav__add(_param['section'],_param['title'],_param['year'],_param['img'],_param['fanart'],_param['subfav'])
	elif (mode=='sunNote'):  		   				sunNote( header=_param['title'],msg=_param['plot'])
	elif (mode=='deadNote'):  		   			deadNote(header=_param['title'],msg=_param['plot'])
	elif (mode=='LibrarySaveMovie'):  		Library_SaveTo_Movies(_param['url'],_param['img'],_param['showtitle'],_param['showyear'])
	#elif (mode=='LibrarySaveTV'):  				Library_SaveTo_TV(_param['section'], _param['url'],_param['img'],_param['showtitle'],_param['showyear'],_param['country'],_param['season'],_param['episode'],_param['episodetitle'])
	#elif (mode=='LibrarySaveEpisode'):  	Library_SaveTo_Episode(_param['url'],_param['img'],_param['title'],_param['showyear'],_param['country'],_param['season'],_param['episode'],_param['episodetitle'])
	elif (mode=='PlayLibrary'): 					PlayLibrary(_param['section'], _param['url'], showtitle=_param['showtitle'], showyear=_param['showyear'])
	elif (mode=='Download'): 							print _param; DownloadRequest(_param['section'], _param['url'],_param['img'],_param['studio']); eod()
	elif (mode=='DownloadStop'): 					DownloadStop(); eod()
	#elif (mode=='TrailersGenres'): 				Trailers_Genres(_param['section'], _param['url'])
	#elif (mode=='TrailersList'): 					Trailers_List(_param['section'], _param['url'], _param['genre'])
	#elif (mode=='LatestThreads'): 				News_LatestThreads(_param['url'],_param['title'])
	#elif (mode=='listUsers'): 						UsersList(_param['section'],_param['url'])
	#elif (mode=='UsersChooseSection'): 		UsersChooseSection(_param['section'],_param['url'])
	#elif (mode=='UsersShowFavorites'): 		UsersShowFavorites(_param['section'],_param['url'])
	##elif (mode=='UsersShowWatchList'): 		UsersShowWatchList(_param['section'],_param['url'])
	#elif (mode=='UsersShowUploads'): 			UsersShowUploads(_param['section'],_param['url'])
	#elif (mode=='PrivacyPolicy'): 				Site__PrivacyPolicy()
	#elif (mode=='TermsOfService'): 				Site__TermsOfService()
	#elif (mode=='GetLatestSearches'): 		listLatestSearches(_param['section'],_param['url'])
	#elif (mode=='UsersShowProfileAccountInfo'): UsersShowPersonInfo(mode, _param['section'],_param['url'])
	elif (mode=='YoutubeSettings'):
		url_youtube='plugin://plugin.video.youtube/?action=settings'
		#xbmc.executebuiltin('XBMC.Container.Update(%s)' % url_youtube )
		xbmc.executebuiltin('XBMC.RunPlugin(%s)' % url_youtube )
	elif (mode=='ChangeFanartList'):			ChangeFanartList(_param['section'],_param['subfav'],_param['url'],_param['fanart'],_param['img'],_param['studio'])
	elif (mode=='ChangeFanartUpdate'):		ChangeFanartUpdate(_param['section'],_param['subfav'],_param['url'],_param['title'])
	else: deadNote(header='Mode:  "'+mode+'"',msg='[ mode ] not found.'); initDatabase(); Menu_MainMenu()

# {'showyear': '', 'infoLabels': "
# {'Plot': '', 'Episode': '11', 'Title': u'Transformers Prime', 'IMDbID': '2961014', 'host': 'filenuke.com', 
# 'IMDbURL': 'http://anonym.to/?http%3A%2F%2Fwww.imdb.com%2Ftitle%2Ftt2961014%2F', 
# 'ShowTitle': u'Transformers Prime', 'quality': 'HDTV', 'Season': '3', 'age': '25 days', 
# 'Studio': u'Transformers Prime  (2010):  3x11 - Persuasion', 'Year': '2010', 'IMDb': '2961014', 
# 'EpisodeTitle': u'Persuasion'}", 'thetvdbid': '', 'year': '', 'special': '', 'plot': '', 
# 'img': 'http://static.solarmovie.so/images/movies/1659175_150x220.jpg', 'title': '', 'fanart': '', 'dbid': '', 'section': 'tv', 'pagesource': '', 'listitem': '<xbmcgui.ListItem object at 0x14C799B0>', 'episodetitle': '', 'thumbnail': '', 'thetvdb_series_id': '', 'season': '', 'labs': '', 'pageurl': '', 'pars': '', 'user': '', 'letter': '', 'genre': '', 'by': '', 'showtitle': '', 'episode': '', 'name': '', 'pageno': 0, 'pagecount': 1, 'url': '/link/show/1466546/', 'country': '', 'subfav': '', 'mode': 'Download', 'tomode': ''}

##### /\ ##### Modes #####
### ############################################################################################################
deb('param >> studio',_param['studio'])
deb('param >> season',_param['season'])
deb('param >> section',_param['section'])
deb('param >> img',_param['img'])
deb('param >> showyear',_param['showyear'])
deb('param >> showtitle',_param['showtitle'])
deb('param >> title',_param['title'])
deb('param >> url',_param['url']) ### Simply Logging the current query-passed / param -- URL
check_mode(_param['mode']) ### Runs the function that checks the mode and decides what the plugin should do. This should be at or near the end of the file.
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
### 
### ** Currently Used: **
### 
### Menu_MainMenu
### Menu_BrowseByCountry
### Menu_BrowseByYear
### Menu_BrowseByScore
### Menu_BrowseByRating
### listItems
### PlayVideo
### 
### 
### 
### 
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
