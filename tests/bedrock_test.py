import boto3
import json

# Configure the model and region
MODEL_ID = "meta.llama3-70b-instruct-v1:0"
REGION = "us-east-1"

# Define your structured prompt
PROMPT = (
    "You are a strict document parser.\n"
    "Extract the following fields from the input text and output them as a raw JSON object with exactly these keys:\n"
    "['Invoice Number', 'Invoice Date', 'Total Amount', 'Customer Name']\n\n"
    "If any field is missing, set it to null. Do not include any explanation or extra text — only return raw JSON.\n\n"
    "Input text:\n"
    "Invoice #12345 dated April 25, 2025. Billed to Rinku Sharma. Amount due: $398.25.\n"
)

def invoke_llama3(prompt):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    body = {
        "prompt": f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n{prompt}\n<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n",
        "max_gen_len": 512,
        "temperature": 0.2,
        "top_p": 0.9
    }

    try:
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )
        raw = response["body"].read().decode("utf-8")
        parsed = json.loads(raw)
        print("\n--- LLaMA 3-70B Output ---\n")
        print(parsed["generation"])
        return parsed["generation"]
    except Exception as e:
        print(f"\n❌ Error invoking LLaMA 3: {e}")
        return None

if __name__ == "__main__":
    invoke_llama3(PROMPT)
