import requests

class GoogleTranslateAPI():
    def __init__(self, accesskey:str, proxies:dict):
        self.accesskey = accesskey
        self.proxies = proxies
    
    def translate(self, q:str,target:str,source:str=None):
        url = "https://translation.googleapis.com/language/translate/v2"
        data = {k: v for k, v in dict(q=q,target=target,source=source).items() if v is not None}
        params = dict(key=self.accesskey)
        headers = {"Content-Type":"application/json; charset=utf-8"}
        r = requests.post(url,json=data,params=params,headers=headers,proxies=self.proxies)
        return r
        

    def get_supported_language(self,target:str):
        url = "https://translation.googleapis.com/language/translate/v2/languages"
        data = {}
        if target:
            data["target"]=target
        params = dict(key=self.accesskey)
        headers = {"Content-Type":"application/json; charset=utf-8"}
        r = requests.post(url,json=data,params=params,headers=headers,proxies=self.proxies)
        return r

if __name__ == "__main__":
    t = GoogleTranslateAPI()