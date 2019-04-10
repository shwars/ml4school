# Cognitive Services Vision API mini-client

import requests
import time

NumRetries = 4

# taken from https://github.com/Microsoft/Cognitive-Vision-Python/blob/master/Jupyter%20Notebook/Computer%20Vision%20API%20Example.ipynb
def processRequest(url, json, data, headers, params):
    """
    Helper function to process the request to Project Oxford

    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """
    retries = 0
    result = None

    while True:
        response = requests.request('post', url, json=json, data=data, headers=headers, params=params)
        if response.status_code == 429:
            print("Message: %s" % (response.json()))
            if retries <= NumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break

        elif response.status_code == 200 or response.status_code == 201:
            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            print("Error code: %d" % (response.status_code))
            print("Message: %s" % (response.json()))

        break
    return result

class CognitiveServicesVision():

    def __init__(self,key,region):
        self.key = key
        self.region = region
        self.url = 'https://{}.api.cognitive.microsoft.com/vision/v2.0/analyze'.format(region)
        self.features = 'Categories,Faces,Tags,Color,Adult,Description,Objects'

    def _postproc(self,result):
        return result


    def analyze_image(self,img, features=None):

        # Computer Vision parameters
        params = {'visualFeatures': self.features if features is None else features }

        headers = dict()
        headers['Ocp-Apim-Subscription-Key'] = self.key
        headers['Content-Type'] = 'application/octet-stream'

        result = processRequest(self.url,None, img, headers, params)

        return self._postproc(result)

    def analyze_file(self,filename):
        with open(filename, 'rb') as f:
            data = f.read()
        return self.analyze_image(data)

    def analyze_url(self,image_url, features=None):

        params = {'visualFeatures': self.features if features is None else features }

        headers = dict()
        headers['Ocp-Apim-Subscription-Key'] = self.key
        headers['Content-Type'] = 'application/json'

        json = {'url': image_url }

        result = processRequest(json, None, headers, params)

        return self._postproc(result)
