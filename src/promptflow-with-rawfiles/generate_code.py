from promptflow import tool
from openai import AzureOpenAI
import base64

def create_response(image_base64:str, system_prompt:str, text_input:str) -> str:
    client = AzureOpenAI(
    api_version="2024-08-01-preview",
    azure_endpoint="https://aihcoderag8407652435.openai.azure.com/",
    azure_deployment="gpt-4o",
    api_key="Fe5hlHO6erqgbuMVKPJGsb3xB06u9SwT04FwT6RIFL4lMvZxFffeJQQJ99AJACYeBjFXJ3w3AAAAACOGLbFD"
    )

    # path to the image
    # image_path = "UI.png"

    # Getting the base64 string of the image
    # image_base64 = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text_input},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}",
                            "detail": "high"
                        },
                    },
                ],
            }
        ],
        max_tokens=4096,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def inquiry_genai(image_base64: str,system_prompt:str,text_input:str) -> str:
    response = create_response(image_base64, system_prompt,text_input)
    return response