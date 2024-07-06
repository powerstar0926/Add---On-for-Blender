import time
import requests

api_token = "msy_9a7pGswKXXAfouDj1PFIs6WgvAymPGzQp2Yk"
task_id = "01907e96-636a-79c7-a1bd-19b252933b04"

headers = {
    "Authorization": f"Bearer {api_token}"
}

while True:
    response = requests.get(
        f"https://api.meshy.ai/v1/text-to-texture/{task_id}",
        headers=headers,
    )

    response.raise_for_status()
    result = response.json()
    print(result)
    
    if result['status'] == 'SUCCEEDED':
        print("Task succeeded!")
        break
    elif result['status'] == 'FAILED':
        print("Task failed!")
        break
    else:
        print(f"Task status: {result['status']}. Checking again in 10 seconds...")
        time.sleep(10)

