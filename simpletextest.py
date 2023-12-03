import requests
api_url = "https://www.simpletex.cn/ai/latex_ocr"
data = {...}
header = {"token":"t1t2n2obpYJ4FxFZnsLXAVO3M29gD2B9lgrDf12Cpwb8YRKSCXyUV74gIYbGk7UF"}
file = [("file",("test.png",open("test.png", 'rb')))]
res = requests.post(api_url, files=file, data=data, headers=header)
print(res.status_code)
print(res.text)