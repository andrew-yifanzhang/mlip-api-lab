from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
import time

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Get credentials from environment variables
endpoint = os.getenv("AZURE_COMPUTER_VISION_ENDPOINT")
key = os.getenv("AZURE_COMPUTER_VISION_KEY")

if not endpoint or not key:
    raise ValueError("Missing endpoint or key. Please set AZURE_COMPUTER_VISION_ENDPOINT and AZURE_COMPUTER_VISION_KEY in your environment.")

# Hard-coding credentials is a bad idea because it exposes sensitive data to potential security risks, such as accidental inclusion in version control systems or access by unauthorized users. It complicates updates, as changing credentials requires code modifications and redeployment, making it error-prone and non-scalable for environments like development, staging, and production. Additionally, it violates security best practices and compliance standards, increasing the risk of misuse, resource overuse, or legal repercussions. Using environment variables or secure configuration files is a safer and more flexible alternative.

# Examples with curl:
    
# curl -X GET http://127.0.0.1:3000/api/v1/analysis/ \
# -H "Content-Type: application/json" \
# -d '{"uri": "https://cdn.jetphotos.com/full/6/1165013_1733337015.jpg"}' 


# curl -X GET http://127.0.0.1:3000/api/v1/analysis/ \
# -H "Content-Type: application/json" \
# -d '{"uri": "https://cdn.jetphotos.com/full/5/922530_1724257282.jpg"}' 

credentials = CognitiveServicesCredentials(key)

client = ComputerVisionClient(
    endpoint=endpoint,
    credentials=credentials
)

def read_image(uri):
    numberOfCharsInOperationId = 36
    maxRetries = 10

    # SDK call
    rawHttpResponse = client.read(uri, language="en", raw=True)

    # Get ID from returned headers
    operationLocation = rawHttpResponse.headers["Operation-Location"]
    idLocation = len(operationLocation) - numberOfCharsInOperationId
    operationId = operationLocation[idLocation:]

    # SDK call
    result = client.get_read_result(operationId)
    
    # Try API
    retry = 0
    
    while retry < maxRetries:
        if result.status.lower () not in ['notstarted', 'running']:
            break
        time.sleep(1)
        result = client.get_read_result(operationId)
        
        retry += 1
    
    if retry == maxRetries:
        return "max retries reached"

    if result.status == OperationStatusCodes.succeeded:
        res_text = " ".join([line.text for line in result.analyze_result.read_results[0].lines])
        return res_text
    else:
        return "error"
