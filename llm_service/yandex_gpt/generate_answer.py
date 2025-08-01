from __future__ import annotations
from yandex_cloud_ml_sdk import YCloudML
from core import settings
from yandex_gpt.model_message import messages
from copy import deepcopy

sdk = YCloudML(
        folder_id=str(settings.llm_set.folder_id),
        auth=str(settings.llm_set.auth),
    )



def get_answer(text_post: str) -> str:
    local_message = deepcopy(messages)

    local_message.append({
        "role": "user",
        "text":  text_post
    })

    model = sdk.models.completions("yandexgpt")
    operation = model.configure(temperature=0.5).run_deferred(local_message)
    
    
    result = operation.wait()
    print(type(result.alternatives[0].text))
    return result.alternatives[0].text
    


    
