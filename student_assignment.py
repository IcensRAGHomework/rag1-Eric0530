import json
import traceback
import requests # for calling Calendarific API in hw02

from model_configurations import get_model_configuration

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage

gpt_chat_version = 'gpt-4o'
gpt_config = get_model_configuration(gpt_chat_version)

format_output = """
{
    "Result": 
        {
            "date": "2024-10-10",
            "name": "國慶日"
        }
}
"""
def generate_hw01(question):
    
    print("generate_hw01 請回答台灣特定月份的紀念日有哪些(請用JSON格式呈現)")
    print(question)  
    question += "我希望的輸出格式是符合json格式的如下字串"+ format_output + "，不需要其他說明也不需要轉成markdown，若有多個節日，請放在\"Result\"" 
    
       
    llm = AzureChatOpenAI(
            model=gpt_config['model_name'],
            deployment_name=gpt_config['deployment_name'],
            openai_api_key=gpt_config['api_key'],
            openai_api_version=gpt_config['api_version'],
            azure_endpoint=gpt_config['api_base'],
            temperature=gpt_config['temperature'] 
    )
    message = HumanMessage(
            content=[
                {"type": "text" , "text": question},
            ]
    )
    response = llm.invoke([message])
    
    return response.content
   
    
    
def generate_hw02(question):

    print(question)
    llm = AzureChatOpenAI(
            model=gpt_config['model_name'],
            deployment_name=gpt_config['deployment_name'],
            openai_api_key=gpt_config['api_key'],
            openai_api_version=gpt_config['api_version'],
            azure_endpoint=gpt_config['api_base'],
            temperature=gpt_config['temperature']
    )
    BASE_URL = "https://calendarific.com/api/v2/holidays"
    API_KEY = "5katB68lvhmreRn93S070n9UgoPxPLEt"

    params = {
    "api_key": API_KEY,
    "country": "TW",   # 台灣
    "year": 2024,      # 查詢年份
    "month": 10         # 選填：查詢10月份
    }

    holidays_message = requests.get(BASE_URL, params=params)
    #prompt = "請將" + holidays_message.text + "資料中的所有節日資訊，重新整理為" + format_output + "格式，並輸出格式符合 JSON 格式不需要其他說明也不需要轉成markdown。若有多個節日，請將它們以數組形式放入Result鍵中，確保每個節日的date 和 name 按照" + format_output + "格式呈現。請僅返回 JSON 格式的結果，無需其他說明或描述"
    prompt = "請將" + holidays_message.text + "資料中的所有節日資訊，重新整理為" + format_output + "格式，並輸出格式符合 JSON 格式不需要其他說明也不需要轉成markdown。若有多個節日，請將它們以數組形式放入Result鍵中，確保每個節日的date 和 name 按照" + format_output + "格式呈現，無需其他說明或描述"
    message = HumanMessage(
            content=[
                {"type": "text" , "text": prompt},
            ]
        )
    response = llm.invoke([message])

    return response.content


def generate_hw03(question2, question3):
    pass
    
def generate_hw04(question):
    pass
    
def demo(question):
    llm = AzureChatOpenAI(
            model=gpt_config['model_name'],
            deployment_name=gpt_config['deployment_name'],
            openai_api_key=gpt_config['api_key'],
            openai_api_version=gpt_config['api_version'],
            azure_endpoint=gpt_config['api_base'],
            temperature=gpt_config['temperature']
    )
    message = HumanMessage(
            content=[
                {"type": "text", "text": question},
            ]
    )
    response = llm.invoke([message])
    
    return response
    

#print(generate_hw01("2024年台灣10月紀念日有哪些?"))
print(generate_hw02("2024年台灣10月紀念日有哪些?"))
