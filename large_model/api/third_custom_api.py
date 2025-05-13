from math import trunc
import os
import requests,json
from large_model.abstract_api import AbstractApi

class ThirdCustomApi(AbstractApi):

    def __init__(self):
        self.params = {}
        self.response = None

    def set_config(self, api_config: dict) -> bool:
        if api_config is None:
            raise ValueError("api_config is None")
        
        if api_config['api_key'] is None:
            raise ValueError("api_key is None")
        
        if api_config['api_base'] is None:
            raise ValueError("api_base is None")
        
        if api_config['model'] is None:
            raise ValueError("model is None")
        
        if api_config['provider'] is None:
            raise ValueError("provider is None")
        
        for key in api_config:
            # 如果为大写，则写入环境变量
            if key.isupper():
                os.environ[key] = api_config[key]
                continue
            self.params[key] = api_config[key]
        print(f"API请求参数: {self.params}")  # 调试信息
  
        return True

    def generate_text(self, messages: list) -> bool:
        url = self.params['api_base']
        api_key = self.params['api_key']

        headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
        }

        payload = json.dumps({
            "model": self.params['model'],
            "messages": messages,
            "stream": False,
            "temperature": 0.9,
            "max_tokens": 2048,
        })

        try:
            self.response = requests.request("POST",  url, headers=headers, data=payload).json()
            print("响应数据 Response:", self.response)
        except Exception as e:
            raise e
        return True

    def get_respond_content(self) -> str:
        return self.response['choices'][0]['message']['content']

    def get_respond_tokens(self) -> int:
        return trunc(int(self.response['usage']['total_tokens']))