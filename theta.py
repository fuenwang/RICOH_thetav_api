import io
import sys
import cv2
import json 
import time
import requests
import PIL.Image
import numpy as np



body = {
    "name": "camera.getOptions", 
    "parameters": { 
        "optionNames": [ 
            #"fileFormat"
            "_wlanFrequency"
            #"previewFormat"
        ] 
    } 
}

def dumps(js):
    return json.dumps(js, indent=4)

def packet(cmd, params={}):
    out = {}
    out['name'] = cmd
    out['parameters'] = params
    return out

class theta:
    def __init__(self, root='http://192.168.1.1:80'):
        self.url = '%s/osc/commands/execute'%root
        self.url_status = '%s/osc/state'%root
    
    def status(self):
        r = requests.post(self.url_status).json()
        print (dumps(r))
        return r

    def preview(self):
        cmd = packet('camera.getLivePreview')
        r = requests.post(self.url, json=cmd, stream=True)
        if r.status_code == 200:
            bytes=''
            cv2.namedWindow('Preview')
            for block in r.iter_content(None):
                bytes += block
                a = bytes.find('\xff\xd8')
                b = bytes.find('\xff\xd9')
                if a !=- 1 and b != -1:
                    jpg = bytes[a:b+2]
                    picture_stream = io.BytesIO(jpg)
                    pic = PIL.Image.open(picture_stream)
                    bytes = bytes[b+2:]
                    img = np.asarray(pic)
                    cv2.imshow('Preview', cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                    cv2.waitKey(1)

    def get_preview_format(self):
        # https://developers.theta360.com/en/docs/v2.1/api_reference/options/preview_format.html
        # {"width": 1920, "height": 960, "framerate": 8}
        # {"width": 1024, "height": 512, "framerate": 30} 
        # {"width": 1024, "height": 512, "framerate": 8}
        # {"width": 640, "height": 320, "framerate": 30} 
        # {"width": 640, "height": 320, "framerate": 8}

        cmd = packet('camera.getOptions', {'optionNames': ['previewFormat']})
        r = requests.post(self.url, json=cmd).json()
        print (dumps(r))
        return r
    
    def set_preview_format(self, height, width, fps):
        buf = {
                'options': {
                        'previewFormat': {
                                "width": width, 
                                "height": height, 
                                "framerate": fps
                            }
                    }
                }
        cmd = packet('camera.setOptions', buf)
        r = requests.post(self.url, json=cmd).json()
        print (dumps(r))
        return r

    def set_sleep_delay(self, second=65535):
        #
        # 60 to 65534, or 65535 (to disable the sleep mode).
        #
        cmd = packet('camera.setOptions', {'options':{'sleepDelay': second}})
        r = requests.post(self.url, json=cmd).json()
        print (dumps(r))
        return r

if __name__ == '__main__':
    tmp = theta()
    #tmp.preview()
    tmp.get_preview_format()
    tmp.set_preview_format(512, 1024, 30)
    tmp.set_sleep_delay()
    tmp.status()















