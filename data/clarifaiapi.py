from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
from PIL import Image, ImageDraw, ImageFont
from imgurpython import ImgurClient
import os, string, requests, shutil

class ClarifaiAPI():
    def __init__(self, clarifaikey, imgurkey):
        try:
            self.clarifai = ClarifaiApp(api_key = clarifaikey)
            self.imgur = ImgurClient(imgurkey[0], imgurkey[1], imgurkey[2], imgurkey[3])
            self.workdir = os.getcwd()
        except Exception as e:
            raise e

    def getContent(self, link):
        try:
            allchar = string.ascii_letters + string.digits
            path = "".join(choice(allchar) for x in range(10)) + '.jpg'
            data = requests.get(link, stream=True)
            if data.status_code == 200:
                with open(path, 'wb') as f:
                    shutil.copyfileobj(data.raw, f)
                return path
            else:
                raise 'failed to get image'
        except Exception as e:
            raise e

    def uploadImgur(self, path):
        try:
            data = imgur.upload_from_path(path, config=None, anon=False)
            os.remove(path)
            return data['link']
        except Exception as e:
            raise e

    def getDataModel(self, model, path):
        try:
            worker = clarifai.models.get(model)
            content = ClImage(file_obj=open(path, 'rb'))
            data = worker.predict([img])
            return data
        except Exception as e:
            raise e

    def modelGeneral(self, link):
        try:
            path = self.getContent(link)
            data = self.getDataModel('general-v1.3', path)
            data = data['outputs'][0]['data']['concepts']
            back = {}
            back['result'] = []
            for a in range(len(data)):
                b = {}
                b['name'] = data[a]['name']
                b['precentage'] = format(float(data[a]['value']) * 100, '.2f')
                back['result'].append(b)
            back['image_link'] = self.uploadImgur(path)
            return back
        except Exception as e:
            raise e

    def modelFood(self, link):
        try:
            path = self.getContent(link)
            data = self.getDataModel('food-items-v1.0', path)
            data = data['outputs'][0]['data']['concepts']
            back = {}
            back['result'] = []
            for a in range(len(data)):
                b = {}
                b['name'] = data[a]['name']
                b['precentage'] = format(float(data[a]['value']) * 100, '.2f')
                back['result'].append(b)
            back['image_link'] = self.uploadImgur(path)
            return back
        except Exception as e:
            raise e

    def modelDemographic(self, link):
        try:
            path = self.getContent(link)
            data = self.getDataModel('demographics', path)
            back = {}
            back['result'] = []
            try:
                data = data['outputs'][0]['data']['regions']
            except Exception as e:
                back['image_link'] = self.uploadImgur(path)
                return back
            img = Image.open(path)
            draw = ImageDraw.Draw(img)
            width, height = img.size
            for a in range(len(data)):
                b = {}
                top_row = data[a]['region_info']['bounding_box']['top_row']
                left_col = data[a]['region_info']['bounding_box']['left_col']
                bottom_row = data[a]['region_info']['bounding_box']['bottom_row']
                right_col = data[a]['region_info']['bounding_box']['right_col']
                cor = (left_col*width, top_row*height, right_col*width, bottom_row*height)
                draw.rectangle(cor, outline="red")
                draw.text((right_col*width, bottom_row*height), '%s' % (str(a+1)), font=ImageFont.truetype("%s/data/arial.ttf" % (self.workdir)))
                b['number'] = a+1
                b['age'] = data[a]['data']['face']['age_appearance']['concepts'][0]['name']
                b['gender'] = data[a]['data']['face']['gender_appearance']['concepts'][0]['name']
                b['race'] = data[a]['data']['face']['multicultural_appearance']['concepts'][0]['name']
                back['result'].append(b)
            img.save(path)
            back['image_link'] = self.uploadImgur(path)
            return back
        except Exception as e:
            raise e

    def modelCelebrity(self, link):
        try:
            path = self.getContent(link)
            data = self.getDataModel('celeb-v1.3', path)
            back = {}
            back['result'] = []
            try:
                data = data['outputs'][0]['data']['regions']
            except Exception as e:
                back['image_link'] = self.uploadImgur(path)
                return back
            img = Image.open(path)
            draw = ImageDraw.Draw(img)
            width, height = img.size
            for a in range(len(data)):
                b = {}
                top_row = data[a]['region_info']['bounding_box']['top_row']
                left_col = data[a]['region_info']['bounding_box']['left_col']
                bottom_row = data[a]['region_info']['bounding_box']['bottom_row']
                right_col = data[a]['region_info']['bounding_box']['right_col']
                cor = (left_col*width, top_row*height, right_col*width, bottom_row*height)
                draw.rectangle(cor, outline="red")
                draw.text((right_col*width, bottom_row*height), '%s' % (str(a+1)), font=ImageFont.truetype("%s/data/arial.ttf" % (self.workdir)))
                b['number'] = a+1
                b['similiar'] = data[a]['data']['face']['identity']['concepts'][0]['name']
                back['result'].append(b)
            img.save(path)
            back['image_link'] = self.uploadImgur(path)
            return back
        except Exception as e:
            raise e