from __future__ import annotations
from yandex_cloud_ml_sdk import YCloudML
from core import settings
import time
from model_message import messages

sdk = YCloudML(
        folder_id=str(settings.llm_set.folder_id),
        auth=str(settings.llm_set.auth),
    )



def get_answer(): 
    start_time = time.time()

    model = sdk.models.completions("yandexgpt")

    operation = model.configure(temperature=0.5).run_deferred(messages)
    result = operation.wait()

    end_time = time.time()

    execute_time = end_time-start_time

    print(f"ОТВЕТ МОДЕЛИ: {result.alternatives[0].text}")
    print(f"Время выполнения {execute_time:.2f} секунд!")


    


get_answer()