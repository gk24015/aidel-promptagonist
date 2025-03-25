from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

completion = client.chat.completions.create(
    extra_headers={
        "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>",     # Optional. Site title for rankings on openrouter.ai.
    },
    extra_body={},
    model="deepseek/deepseek-chat-v3-0324:online",  # Appending ':online' enables web search
    messages=[
        {
            "role": "user",
            "content": """ 
            determine the risk score of this entity "23 and Me"
            base_dict = {
            "Transaction ID": self.transaction_id,
            "Extracted Entity": self.extracted_entity,
            "Entity Type": self.entity_type,
            "Risk Score": self.risk_score,
            "Supporting Evidence": self.supporting_evidence,
            "Confidence Score": self.confidence_score,
            "Reason": self.reason
            }
        }"""
        }
    ]
)
print(completion.choices[0].message.content)
