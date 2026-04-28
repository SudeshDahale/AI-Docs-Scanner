from openai import OpenAI

client = OpenAI()

def summarize(text):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Summarize the following text clearly."},
            {"role": "user", "content": text[:3000]}
        ]
    )
    return response.choices[0].message.content