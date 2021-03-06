#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmcaddon,socket
import SimpleDownloader as downloader
import os
downloader = downloader.SimpleDownloader()


socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
settings = xbmcaddon.Addon(id='plugin.video.myspass_de')
translation = settings.getLocalizedString

downloadFolder=settings.getSetting("downloadFolder")

forceViewMode=settings.getSetting("forceViewMode")
if forceViewMode=="true":
  forceViewMode=True
else:
  forceViewMode=False
viewMode=str(settings.getSetting("viewMode"))

def index():
        addDir(translation(30002),"tvshows",'listShows',"")
        addDir(translation(30003),"webshows",'listShows',"")
        addDir(translation(30004),"full_episodes",'listOrderType',"")
        addDir(translation(30005),"clips",'listOrderType',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode==True:
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listShows(type):
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        content=getUrl("http://www.myspass.de/")
        match=re.compile('<li><a href="(.+?)" title="(.+?)"', re.DOTALL).findall(content)
        for url, title in match:
          if url.find("/myspass/shows/"+type+"/")>=0:
            addDir(title,"http://www.myspass.de"+url,"listMediaTypes","",title)
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode==True:
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listMediaTypes(url):
        addDir(translation(30004),url+"#seasonlist_full_episode",'listSeasons',"")
        addDir(translation(30005),url+"#seasonlist_clip",'listSeasons',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode==True:
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listOrderType(type):
        addDir(translation(30007),"http://www.myspass.de/myspass/includes/php/ajax.php?action=getVideoList&sortBy=newest&category="+type+"&ajax=true&timeSpan=all&pageNumber=0",'listVideos',"")
        addDir(translation(30008),"http://www.myspass.de/myspass/includes/php/ajax.php?action=getVideoList&sortBy=views&category="+type+"&ajax=true&timeSpan=all&pageNumber=0",'listVideos',"")
        addDir(translation(30009),"http://www.myspass.de/myspass/includes/php/ajax.php?action=getVideoList&sortBy=votes&category="+type+"&ajax=true&timeSpan=all&pageNumber=0",'listVideos',"")
        addDir(translation(30010),"http://www.myspass.de/myspass/includes/php/ajax.php?action=getVideoList&sortBy=comments&category="+type+"&ajax=true&timeSpan=all&pageNumber=0",'listVideos',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode==True:
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listSeasons(url):
        spl=url.split("#")
        url=spl[0]
        type=spl[1]
        content=getUrl(url)
        spl=content.split('<ul class="episodeListSeasonList">')
        content=""
        for str in spl:
          if str.find(type)>0:
            content = str
        if content!="":
          content = content[:content.find('<div class="refresh"></div>')]
          spl=content.split('<li')
          urlNewVideos=""
          for i in range(1,len(spl),1):
              entry=spl[i]
              match=re.compile(';">(.+?)</a>', re.DOTALL).findall(entry)
              title=match[0]
              title=cleanTitle(title)
              match=re.compile("'getEpisodeListFromSeason(.+?)'", re.DOTALL).findall(entry)
              url=match[0].replace("&amp;","&")
              if url.find("&sortBy=votes&")>0:
                urlNewVideos="http://www.myspass.de/myspass/includes/php/ajax.php?action=getEpisodeListFromSeason"+url.replace("&sortBy=votes&","&sortBy=episode_desc&")+"&pageNumber=0"
              url="http://www.myspass.de/myspass/includes/php/ajax.php?action=getEpisodeListFromSeason"+url+"&pageNumber=0"
              if url.find("&sortBy=views&")==-1 and url.find("&sortBy=votes&")==-1:
                addDir(title,url,'listVideosAZ',"",params.get('show'),i)
          if urlNewVideos!="":
            addDir(translation(30007),urlNewVideos,'listVideosAZ',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode==True:
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listVideosAZ(url):
        urlMain=url
        content = getUrl(url)
        spl=content.split('<td class="title" onclick=')
        for i in range(1,len(spl),1):
            entry=spl[i]
            match=re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
            title=match[0]
            title=cleanTitle(title)
            match=re.compile('</h5>(.+?)</div>', re.DOTALL).findall(entry)
            desc=match[0]
            desc=cleanTitle(desc)
            match=re.compile('&amp;id=(.+?)&', re.DOTALL).findall(entry)
            id=match[0]
            match=re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb="http://www.myspass.de"+match[0]
            entry=entry[entry.find('<td class="duration"'):]
            entry=entry[entry.find('<a href='):]
            match=re.compile('>(.+?)<', re.DOTALL).findall(entry)
            duration=match[0]
            addLink(title,id,'playVideo',thumb,desc,duration, params.get('show'), params.get('season'), i)
        match=re.compile("setPageByAjaxTextfield\\('(.+?)', '(.+?)'", re.DOTALL).findall(content)
        if len(match)>0:
          currentPage=int(match[0][0])
          maxPage=int(match[0][1])
          if currentPage<maxPage:
            urlNext=urlMain.replace("&pageNumber="+str(currentPage-1),"&pageNumber="+str(currentPage))
            addDir(translation(30001)+" ("+str(currentPage)+")",urlNext,'listVideosAZ',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode==True:
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listVideos(url):
        urlMain=url
        content = getUrl(url)
        spl=content.split('<div class="videoTeaserList"')
        for i in range(1,len(spl),1):
            entry=spl[i]
            match=re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            title=match[0]
            title=cleanTitle(title)
            match=re.compile('href="/myspass/shows/(.+?)/(.+?)/(.+?)/(.+?)/"', re.DOTALL).findall(entry)
            id=match[0][3]
            match=re.compile('<img src="(.+?)"', re.DOTALL).findall(entry)
            thumb="http://www.myspass.de"+match[0]
            match=re.compile('<span class="length">(.+?)</span>', re.DOTALL).findall(entry)
            duration=match[0]
            addLink(title,id,'playVideo',thumb,"",duration, params.get('show'), params.get('season'), i)
        match=re.compile("setPageByAjaxTextfield\\('(.+?)', '(.+?)'", re.DOTALL).findall(content)
        if len(match)>0:
          currentPage=int(match[0][0])
          maxPage=int(match[0][1])
          if currentPage<maxPage:
            urlNext=urlMain.replace("&pageNumber="+str(currentPage-1),"&pageNumber="+str(currentPage))
            addDir(translation(30001)+" ("+str(currentPage)+")",urlNext,'listVideos',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode==True:
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def playVideo(id):
        content = getUrl("http://www.myspass.de/myspass/includes/apps/video/getvideometadataxml.php?id="+id)
        match=re.compile('<url_flv><!\\[CDATA\\[(.+?)\\]\\]></url_flv>', re.DOTALL).findall(content)
        listitem = xbmcgui.ListItem(path=match[0])
        return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def cleanTitle(title):
        title=title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#039;","\\").replace("&quot;","\"").replace("&szlig;","ß").replace("&ndash;","-")
        title=title.replace("&Auml;","Ä").replace("&Uuml;","Ü").replace("&Ouml;","Ö").replace("&auml;","ä").replace("&uuml;","ü").replace("&ouml;","ö")
        title=title.strip()
        return title

def getUrl(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/14.0')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link

def parameters_string_to_dict(parameters):
        ''' Convert parameters encoded in a URL to a dict. '''
        paramDict = {}
        if parameters:
            paramPairs = parameters[1:].split("&")
            for paramsPair in paramPairs:
                paramSplits = paramsPair.split('=')
                if (len(paramSplits)) == 2:
                    paramDict[paramSplits[0]] = paramSplits[1]
        return paramDict

def addLink(name,url,mode,iconimage,desc="",duration="",show='none',season=0,episode=0):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
	if show == 'none':
	    show = params.get('show')
	if not show is None:
	    u = u+"&show="+show
	if season == 0:
	    season = params.get('season')
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": desc, "Duration": duration, "tvshowtitle": show, "season": season, "episode": episode } )
        liz.setProperty('IsPlayable', 'true')
	liz.addContextMenuItems([ ( 'Download', "XBMC.RunPlugin(%s?mode=download&url=%s&show=%s&season=%s&episode=%s&title=%s)" % ( sys.argv[0], urllib.quote_plus(url), urllib.quote_plus(show), season, episode, name ) )] )  
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage,show='none',season=0):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&season="+str(season)
	if show == 'none':
	    show = params.get('show')
	if not show is None:
	    u = u+"&show="+show
	if season == 0:
	    season = params.get('season')
	u = u+"&season="+str(season)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
         
def download(url, params):
	#episode = xbmc.getInfoLabel('ListItem.Episode')
	#season = xbmc.getInfoLabel('ListItem.Season')
	#show = xbmc.getInfoLabel('ListItem.TVShowTitle')
	#title = xbmc.getInfoLabel('ListItem.Title') 
	episode = params.get('episode')
	show = urllib.unquote_plus(params.get('show'))
	title = urllib.unquote_plus(params.get('title'))
	season = params.get('season')
	folder = downloadFolder + "/" + show + "/" + 'Season ' + params.get('season') + "/"
	content = getUrl("http://www.myspass.de/myspass/includes/apps/video/getvideometadataxml.php?id="+url)
        match=re.compile('<url_flv><!\\[CDATA\\[(.+?)\\]\\]></url_flv>', re.DOTALL).findall(content)
	url = path=match[0]

	params = {"url": url, "download_path": folder, "Title": title}
	if len(str(episode)) < 2:
	    episode = '0'+episode
	if len(str(season)) < 2:
	    season = '0'+season
	filename = show + ".s" + season + ".e" + episode  + "." + title + ".mp4"

	if not os.path.exists(folder):
	    os.makedirs(folder)
        downloader.download(filename, params)
	return True


params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')

if type(url)==type(str()):
  url=urllib.unquote_plus(url)

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listVideosAZ':
    listVideosAZ(url)
elif mode == 'listVideosSearch':
    listVideosSearch(url)
elif mode == 'listShows':
    listShows(url)
elif mode == 'listMediaTypes':
    listMediaTypes(url)
elif mode == 'listSeasons':
    listSeasons(url)
elif mode == 'listOrderType':
    listOrderType(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'download':
    download(url,params)
else:
    index()
