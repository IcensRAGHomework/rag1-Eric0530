import json
import traceback
import requests # for calling Calendarific API in hw02
import base64 #For hw04

from model_configurations import get_model_configuration
from openai import AzureOpenAI
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory # For hw03 to record the message of hw02
from langchain_core.prompts import MessagesPlaceholder , ChatPromptTemplate #For hw03
from langchain.agents import create_tool_calling_agent , AgentExecutor #For hw03
from langchain_community.chat_message_histories import ChatMessageHistory #For hw03
from typing import List #For hw03
from langchain.output_parsers import PydanticOutputParser #For hw03
from pydantic import BaseModel , Field #For hw03
from mimetypes import guess_type #For hw04

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

score_format = """
{
    "Result": 
        {
            "score": 6666
        }
}
"""

class Hw03_Reason(BaseModel):
    add: bool = Field(description="這是一個布林值，表示是否需要將節日新增到節日清單中。根據問題判斷該節日是否存在於清單中，如果不存在，則為 true；否則為 false")
    reason: str = Field(description="描述為什麼需要或不需要新增節日，具體說明是否該節日已經存在於清單中，以及當前清單的內容")

class Result_Data(BaseModel):
    Result : Hw03_Reason

def local_image_to_data_url(image_path):
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"


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
    prompt = "請將" + holidays_message.text + "資料中的所有節日資訊，重新整理為" + format_output + "格式，並輸出格式符合 JSON 格式且為繁體中文另不需要其他說明也不需要轉成markdown。若有多個節日，請將它們以數組形式放入Result鍵中，確保每個節日的date 和 name 按照" + format_output + "格式呈現，無需其他說明或描述"
    message = HumanMessage(
            content=[
                {"type": "text" , "text": prompt},
            ]
        )
    response = llm.invoke([message])
    
    return response.content


def generate_hw03(question2, question3):
    llm = AzureChatOpenAI(
            model=gpt_config['model_name'],
            deployment_name=gpt_config['deployment_name'],
            openai_api_key=gpt_config['api_key'],
            openai_api_version=gpt_config['api_version'],
            azure_endpoint=gpt_config['api_base'],
            temperature=gpt_config['temperature']
    )
    parser = PydanticOutputParser(pydantic_object=Hw03_Reason)
    format_instructions = parser.get_format_instructions()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system","你是個台灣假日查詢助理，可以根據問題回答某假日是否在查詢列表中並描述為什麼需要或不需要新增節日，具體說明是否該節日已經存在於清單中，以及當前清單的內容，並用Json格式回覆,\n" "{format_instructions}"),
            MessagesPlaceholder(variable_name="history"),
            ("human","{input}"),
        ]
    ) 
    
    memories={'0': ChatMessageHistory()}

    chain = prompt | llm
    chat_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: memories["0"],
        input_messages_key="input",
        history_messages_key="history",
    )

    result_1=chat_history.invoke(
        {"input":generate_hw02(question2), "format_instructions": format_instructions },
        config={"configurable": {"session_id": "0"}}
    )
    
    result = chat_history.invoke(
        {"input": question3 , "format_instructions": format_instructions},
        config={"configurable": {"session_id": "0"}}
    )
    result_parsed = parser.parse(result.content)
    result_wrapped = Result_Data(Result=result_parsed)
    #return result_wrapped.json(indent=4)
    #return json.dumps(result_wrapped.dict(), indent=4, ensure_ascii=False)
    return json.dumps(result_wrapped.model_dump(), indent=4, ensure_ascii=False)

def generate_hw04(question):
    client = AzureOpenAI(
        api_key=gpt_config['api_key'],
        api_version=gpt_config['api_version'],
        base_url=f"{gpt_config['api_base']}openai/deployments/{gpt_config['deployment_name']}"
        )
    
    data_url = local_image_to_data_url("baseball.png")
    response = client.chat.completions.create(
    model=gpt_config['deployment_name'],
    messages=[
        { "role": "system", "content": "你可以識別圖片上各國的積分分數，並用此" + score_format + "格式回覆." },
        { "role": "user", "content": "請問中華台北的積分是多少?" },
        #{ "role": "assistant", "content": '{\n"Result":\n{\n"score": 5498\n}' },
        { "role": "assistant", "content": score_format },
        { "role": "user", "content": [  
            { 
                "type": "text", 
                "text": "question:" 
            },
            { 
                "type": "image_url",
                "image_url": {
                    "url": data_url
                }
            }
        ] } 
    ],
    max_tokens=2000 
    )
    return response.choices[0].message.content
    


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
#print(generate_hw02("2024年台灣10月紀念日有哪些?"))
print(generate_hw03("2024年台灣10月紀念日有哪些?" , '根據先前的節日清單，這個節日{"date": "10-31", "name": "蔣公誕辰紀念日"}是否有在該月份清單？'))
#print(generate_hw04("請問中華台北的積分是多少"))
