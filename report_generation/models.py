"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Implement a chatbot model selection function that returns an appropriate
       model instance based on the specified parameters
"""
from openai import OpenAI
from langchain_openai.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from keys import openai_key, deepseek_key, efund_key
import traceback
import warnings
try:
    from luluai.langchain_contrib.chat_models.openai import EFundChatModel
except ImportError as e:
    traceback.print_exc()  # Optionally print the traceback for debugging
    print('a')
    warnings.warn(f"Failed to import EFundChatModel: {e}", UserWarning)

models_list = ["deepseek-chat", "deepseek-r1",
               "gpt-4", "gpt-3.5-turbo", "gpt-4o-mini",
               "efund",
               "g4f"]


def model_invoke(system_prompt, instruction, model="deepseek-chat", chatbot=None, temperature=0,
                 model_name=None):
    """
    Invoke a chatbot model with a given system prompt and instruction.

    Args:
        system_prompt (str): The system prompt for the model.
        instruction (str): The user instruction.
        model (str, optional): The model to use (default: "deepseek-chat").
        chatbot (object, optional): A chatbot instance if applicable.
        temperature (float, optional): The temperature setting for response randomness (default: 0).
        model_name (str, optional): The name of the model to use (default: None).
    Returns:
        str: The response from the model or chatbot.

    Raises:
        Exception: If an error occurs more than 5 times.
    """
    errors = 0
    max_retry = 5
    while 1:
        try:
            if system_prompt is None:
                system_prompt = ""
            if chatbot == 'g4f':
                model = 'g4f'
                chatbot = None
            if chatbot:
                if temperature != 0:
                    chatbot.temperature = temperature
                prompt = [SystemMessage(content=system_prompt), HumanMessage(content=instruction)]
                response = chatbot.invoke(prompt).content
                chatbot.temperature = 0
                return response
            elif model:
                if model in ["deepseek-chat"]:
                    client = OpenAI(api_key=deepseek_key, base_url='Pro/deepseek-ai/DeepSeek-R1')
                    response = client.chat.completions.create(
                        model='Pro/deepseek-ai/DeepSeek-R1',
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": instruction},
                        ],
                        temperature=temperature,
                    )
                elif model in ["deepseek-r1"]:
                    client = OpenAI(api_key=deepseek_key,
                                    base_url='https://api.siliconflow.cn/v1/')
                    response = client.chat.completions.create(
                        model='Pro/deepseek-ai/DeepSeek-R1',
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": instruction},
                        ],
                        temperature=temperature,
                    )
                elif model in ["gpt-4", "gpt-3.5-turbo", "gpt-4o-mini"]:
                    client = OpenAI(api_key=openai_key)
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": instruction},
                        ],
                        temperature=temperature,
                    )
                elif model in ['efund']:
                    if model_name == None:
                        model_name = 'gpt-4o'
                    chatbot = EFundChatModel(
                        model_name=model_name,
                        efunds_user_name='baiyun',
                        openai_api_base='http://luluai.efundsdemo.com/oneapi/v1',
                        openai_api_key=efund_key
                    )
                    data_message = [SystemMessage(content=system_prompt), HumanMessage(content=instruction)]
                    response = chatbot.invoke(data_message).content
                    return response
                elif model in ["g4f"]:
                    from g4f.client import Client
                    client = Client()
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": instruction},
                        ],
                        web_search=False,
                    )
                return response.choices[0].message.content
        except Exception as e:
            errors += 1
            print(f"Error occurred: {e}")
            print(traceback.format_exc())  # Print detailed error traceback
            print(f"Retrying {errors}/{max_retry}...")
            if errors > max_retry:
                print("Max retries reached. Exiting...")
                break


def get_model(model="deepseek-chat", max_tokens=16384, temp=0, model_name=None):
    """
    Returns a chatbot model instance based on the specified model type.

    Args:
        model (str, optional): The model to use. Default is "deepseek-chat".
            Available options:
            - "deepseek-chat": Uses DeepSeek API.
            - "deepseek-r1": Uses DeepSeek-R1 API.
            - "gpt-4", "gpt-3.5-turbo", "gpt-4o-mini": Uses OpenAI API.
            - "efund": Uses EFund custom model.
            - "g4f": Returns 'g4f' (not an instance).
        max_tokens (int, optional): The maximum number of tokens for the model response. Default is 16,384.
        temp (float, optional): The temperature for response randomness. Default is 0.
        model_name (str, optional): The model name to use. Default is None.
    Returns:
        object: An instance of the selected chatbot model, or 'g4f' if using "g4f".

    Raises:
        ValueError: If an unsupported model type is specified.
    """
    if model == "deepseek-chat":
        chatbot = ChatOpenAI(
            model_name='Pro/deepseek-ai/DeepSeek-R1',
            temperature=temp,
            max_tokens=max_tokens,
            openai_api_key=deepseek_key,
            base_url='https://api.siliconflow.cn/v1/',
        )
    elif model == "deepseek-r1":
        chatbot = ChatOpenAI(
            model_name='Pro/deepseek-ai/DeepSeek-R1',
            temperature=temp,
            max_tokens=max_tokens,
            openai_api_key=deepseek_key,
            base_url='https://api.siliconflow.cn/v1/'
        )
    elif model in ["gpt-4", "gpt-3.5-turbo", "gpt-4o-mini"]:
        chatbot = ChatOpenAI(
            model_name=model,
            temperature=temp,
            max_tokens=max_tokens,
            openai_api_key=openai_key,
        )
    elif model in ["efund"]:
        if model_name is None:
            model_name = 'gpt-4o'
        chatbot = EFundChatModel(
            model_name=model_name,
            efunds_user_name='baiyun',
            openai_api_base='http://luluai.efundsdemo.com/oneapi/v1',
            openai_api_key=efund_key,
        )
    elif model in ["g4f"]:
        return 'g4f'
    else:
        raise ValueError(f"Unsupported model type: {model}")

    return chatbot


if __name__ == '__main__':
    # model_name = "g4f"
    model_name = "efund"
    chatbot = get_model(model=model_name, max_tokens=16384, temp=0)
    # model = get_model(model="g4f", max_tokens=16384, temp=0)
    response = model_invoke("", "what is capital of France?", chatbot=chatbot, temperature=0)
    print(response)
    #response = model_invoke("", "what is capital of France?", model=model_name, temperature=0)
    #print(response)
