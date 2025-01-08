import json
import traceback

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
    question += "我希望的輸出格式是符合json格式的如下字串"+ format_output + "，不需要其他說明也不需要轉成markdown，若有多個節日，請放在\"Results\"" 
    
       
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
    pass
    
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
    

print(generate_hw01("2024年台灣10月紀念日有哪些?"))

