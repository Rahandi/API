import json, requests, pafy, sys, os
from flask import Flask, request, abort, redirect, jsonify
from bs4 import BeautifulSoup, SoupStrainer
from data.InstagramAPI import InstagramAPI
from data.clarifaiapi import ClarifaiAPI

app = Flask(__name__)

instaAPI = InstagramAPI('jogedt', 'jogedjoged')
marker = instaAPI.login()
if marker == False:
    instaAPI = InstagramAPI('bolinebot', 'bot321tob')
    marker = instaAPI.login()

imgurlogindata = [
        '19bd6586ad07952',
        '7cff9b3396b1b461b64d923e45d37ceff1e801fe',
        '663137659dbab6d44a9a1a2cb3f8af6c63b68762',
        '660b76c28420af23ce2e5e23b7a317c7a96a8907'
    ]
clarifai = ClarifaiAPI('c469606b715140bcbca2660c886d5220', imgurlogindata)

key = ['randi123', 'betakey']

def humansize(nbytes):
    try:
        i = 0
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        while nbytes >= 1024 and i < len(suffixes)-1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, suffixes[i])
    except Exception as e:
        return str(e)

def shorten(url):
    try:
        api_key = 'AIzaSyB2JuzKCAquSRSeO9eiY6iNE9RMoZXbrjo'
        req_url = 'https://www.googleapis.com/urlshortener/v1/url?key=' + api_key
        payload = {'longUrl': url}
        headers = {'content-type': 'application/json'}
        r = requests.post(req_url, data=json.dumps(payload), headers=headers)
        resp = json.loads(r.text)
        return resp['id']
    except Exception as e:
        return str(e)

@app.route('/', methods=['GET'])
def root():
    if marker == True:
        return str('it works !!!')
    else:
        return str('instagram is not logged in :(')

@app.route('/usage', methods=['GET'])
def usage():
    file = open('usage', 'r')
    data = file.read()
    file.close()
    return str(data)

@app.route('/instainfo/<username>', methods=['GET'])
def instainfo(username):
    result = {}
    try:
        keys = request.args.get('key')
        if keys not in key:
            result['error'] = 'need auth key'
        else:
            result['error'] = None
            query = instaAPI.searchUsername(username)
            if query['status'] == 'ok':
                result['find'] = True
                result['result'] = {}
                query = query['user']
                result['result']['username'] = query['username']
                result['result']['mediacount'] = query['media_count']
                result['result']['following'] = query['following_count']
                result['result']['bio'] = query['biography']
                result['result']['name'] = query['full_name']
                result['result']['follower'] = query['follower_count']
                result['result']['private'] = query['is_private']
                result['result']['url'] = query['hd_profile_pic_url_info']['url']
            else:
                result['find'] = False
        return jsonify(result)
    except Exception as e:
        result['error'] = str(e)
        return jsonify(result)

@app.route('/instastory/<username>', methods=['GET'])
def instastory(username):
    result = {}
    try:
        keys = request.args.get('key')
        if keys not in key:
            result['error'] = 'need auth key'
        else:
            result['error'] = None
            query = instaAPI.searchUsername(username)
            if query['status'] == 'ok':
                result['find'] = True
                userID = query['user']['pk']
                query = instaAPI.getStory(userID)
                data = query['items']
                if len(data) == 0:
                    result['url'] = []
                    if query['user']['is_private'] == True:
                        if 'friendship_status' in query['user']:
                            if query['user']['friendship_status']['following'] == True:
                                result['reason'] = 1
                        else:
                            result['reason'] = 2
                            instaAPI.follow(userID)
                    else:
                        result['reason'] = 1
                else:
                    result['url'] = []
                    for a in data:
                        items = {}
                        tipe = a['media_type']
                        items['tipe'] = tipe
                        if tipe == 1:
                            items['link'] = a['image_versions2']['candidates'][0]['url']
                        elif tipe == 2:
                            items['link'] = a['video_versions'][0]['url']
                            items['preview'] = a['image_versions2']['candidates'][1]['url']
                        result['url'].append(items)
            else:
                result['find'] = False
        return jsonify(result)
    except Exception as e:
        result['error'] = str(e)
        return jsonify(result)

@app.route('/instapost/<username>/<post_ke>', methods=['GET'])
def instapost(username, post_ke):
    result = {}
    try:
        keys = request.args.get('key')
        post_ke = int(post_ke)
        if keys not in key:
            result['error'] = 'need auth key'
        else:
            query = instaAPI.searchUsername(username)
            if query['status'] == 'ok':
                result['find'] = True
                userID = query['user']['pk']
                query = instaAPI.getUserFeed(userID)
                if query['status'] == 'ok':
                    result['see'] = True
                    if post_ke > len(query['items']):
                        user_feed = insta.getTotalUserFeed(userID, post_ke)
                    else:
                        user_feed = query['items']
                    mediacount = len(user_feed)
                    if post_ke <= mediacount:
                        result['banyak'] = True
                        post_ke = post_ke - 1
                        mediatype = user_feed[post_ke]['media_type']
                        result['media'] = {}
                        result['media']['mediatype'] = mediatype
                        result['media']['like_count'] = user_feed[post_ke]['like_count']
                        if 'comments_disabled' not in user_feed[post_ke]:
                            result['media']['comment_count'] = user_feed[post_ke]['comment_count']
                        else:
                            result['media']['comment_count'] = 'Disabled'
                        try:
                            result['media']['caption'] = user_feed[post_ke]['caption']['text']
                        except Exception as e:
                            result['media']['caption'] = ''
                        if mediatype == 1:
                            result['media']['url'] = user_feed[post_ke]['image_versions2']['candidates'][0]['url']
                        elif mediatype == 2:
                            result['media']['url'] = user_feed[post_ke]['video_versions'][1]['url']
                            result['media']['preview'] = user_feed[post_ke]['image_versions2']['candidates'][0]['url']
                        elif mediatype == 8:
                            result['media']['url'] = []
                            for a in user_feed[post_ke]['carousel_media']:
                                med = a['media_type']
                                items = {}
                                items['mediatype'] = med
                                if med == 1:
                                    items['url'] = a['image_versions2']['candidates'][0]['url']
                                elif med == 2:
                                    items['url'] = a['video_versions'][1]['url']
                                    items['preview'] =a['image_versions2']['candidates'][0]['url']
                                result['media']['url'].append(items)
                    else:
                        result['banyak'] = False
                else:
                    result['see'] = False
                    instaAPI.follow(userID)
            else:
                result['find'] = False
        return jsonify(result)
    except Exception as e:
        result['error'] = str(e)
        return jsonify(result)

@app.route('/imageapi', methods=['GET'])
def imageapi():
    result = {}
    try:
        keys = request.args.get('key')
        if keys not in key:
            result['error'] = 'need auth key'
        else:
            query = request.args.get('q')
            if query == None or query == '':
                result['error'] = 'query must be specified'
            else:
                query = query.replace(' ', '+')
                link = 'https://www.google.co.id/search?q=' + query +'&dcr=0&source=lnms&tbm=isch&sa=X&ved=0ahUKEwje9__4z6nXAhVMKY8KHUFCCbwQ_AUICigB&biw=1366&bih=672'
                headers = {}
                headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
                data = requests.get(link, headers=headers)
                data = data.text.encode('utf-8').decode('ascii', 'ignore')
                filtered = SoupStrainer('div', {'class':'rg_meta notranslate'})
                soup = BeautifulSoup(data, 'lxml', parse_only = filtered)
                result = {}
                result['result'] = [] 
                for a in soup.find_all('div', {'class':'rg_meta notranslate'}):
                    try:
                        json1 = json.loads(str(a.text))
                        result['result'].append(json1['ou'])
                    except Exception as e:
                        pass
                result['error'] = None
        return jsonify(result)
    except Exception as e:
        result['error'] = str(e)
        return jsonify(result)

@app.route('/lyricapi', methods=['GET'])
def lyric():
    result = {}
    try:
        keys = request.args.get('key')
        if keys not in key:
            result['error'] = 'need auth key'
        else:
            query = request.args.get('q')
            if query == None or query == '':
                result['error'] = 'query must be specified'
            else:
                link = 'http://api.genius.com/search?q=%s&page=1' % (requests.utils.requote_uri(query))
                header = {
                    'Authorization':'Bearer Rx2zXIU-H5ntF5p7XnkaJSCr8HIG4Q7ObeXcTRoL2oatuE_e4eEFK1HVgdyjtQh7',
                    'User-Agent':'CompuServe Classic/1.22',
                    'Accept':'application/json',
                    'Host':'api.genius.com'
                }
                data = json.loads(requests.get(link, headers=header).text)
                if len(data['response']['hits']) == 0:
                    result['find'] = False
                    return result
                result['find'] = True
                result['title'] = data['response']['hits'][0]['result']['full_title']
                link = data['response']['hits'][0]['result']['url']
                data = requests.get(link).text
                lyricsf = []
                soup = BeautifulSoup(data, 'lxml')
                for a in soup.find_all('div', {'class':'lyrics'}):
                    for b in a.find_all('p'):
                        lyricsf.append(b.text)
                result['lyric'] = '\n'.join(lyricsf)
                result['error'] = None
        return jsonify(result)
    except Exception as e:
        result['error'] = str(e)
        return jsonify(result)

@app.route('/youtubeapi/search', methods=['GET'])
def youtubesearch():
    result = {}
    try:
        try:
        keys = request.args.get('key')
        if keys not in key:
            result['error'] = 'need auth key'
        else:
            query = request.args.get('q')
            if query == None or query == '':
                result['error'] = 'query must be specified'
            else:
                query = query.replace(' ', '+')
                link = 'https://www.youtube.com/results?search_query=' + query
                page = requests.get(link).text
                prefered = SoupStrainer('a', {'rel':'spf-prefetch'})
                soup = BeautifulSoup(page, 'lxml', parse_only=prefered)
                hitung = 0
                url = []
                result['result'] = []
                for a in soup.find_all('a', {'rel':'spf-prefetch'}):
                    if '/watch?' in a['href']:
                        hitung += 1
                        url.append('https://youtube.com' + str(a['href']) + '&t')
                        result['result'].append(youtubeapi(url='https://youtube.com' + str(a['href']) + '&t')['result'])
                        if hitung >= 5:
                            break
                result['error'] = None
        return jsonify(result)
    except Exception as e:
        result['error'] = str(e)
        return jsonify(result)

@app.route('/youtubeapi', methods=['GET'])
def youtubeapi(url=None):
    result = {}
    try:
        keys = request.args.get('key')
        if keys not in key:
            result['error'] = 'need auth key'
        else:
            query = request.args.get('q')
            if url is not None:
                query = url
            if query == None or query == '':
                result['error'] = 'query must be specified'
            else:
                data = pafy.new(query)
                result['result'] = {}
                result['result']['title'] = data.title
                result['result']['thumbnail'] = shorten('https://img.youtube.com/vi/%s/maxresdefault.jpg' % data.videoid)
                result['result']['author'] = data.author
                result['result']['rating'] = data.rating
                result['result']['duration'] = data.duration
                result['result']['viewcount'] = data.viewcount
                result['result']['likes'] = data.likes
                result['result']['dislikes'] = data.dislikes
                result['result']['description'] = data.description
                result['result']['videolist'] = []
                result['result']['audiolist'] = []
                videolist = data.streams
                audiolist = data.audiostreams
                for a in videolist:
                    ape = {}
                    realreso = a.resolution.split('x')
                    ape['resolution'] = '%sp' % (realreso[1])
                    ape['size'] = humansize(a.get_filesize())
                    ape['extension'] = a.extension
                    ape['url'] = shorten(a.url)
                    result['result']['videolist'].append(ape)
                for a in audiolist:
                    ape = {}
                    ape['resolution'] = a.bitrate
                    ape['size'] = humansize(a.get_filesize())
                    ape['extension'] = a.extension
                    ape['url'] = shorten(a.url)
                    result['result']['audiolist'].append(ape)
                result['error'] = None
        return jsonify(result)
    except Exception as e:
        result['error'] = str(e)
        return jsonify(result)

@app.route('/visionAI/<model>', methods=['GET'])
def visionAI(model):
    result = {}
    try:
        keys = request.args.get('key')
        if keys not in key:
            result['error'] = 'need auth key'
        else:
            query = request.args.get('link')
            if query == None or query == '':
                result['error'] = 'link must be specified'
            else:
                if model == 'general':
                    result = clarifai.modelGeneral(query)
                    result['error'] = None
                elif model == 'food':
                    result = clarifai.modelFood(query)
                    result['error'] = None
                elif model == 'demographic':
                    result = clarifai.modelDemographic(query)
                    result['error'] = None
                elif model == 'celebrity':
                    result = clarifai.modelCelebrity(query)
                    result['error'] = None
                else:
                    result['error'] = 'model not exist'
        return jsonify(result)
    except Exception as e:
        result['error'] = str(e)
        return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)