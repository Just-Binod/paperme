from groq import Groq

client = Groq(api_key="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")

try:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Say hello"}],
        model="llama-3.3-70b-versatile",
    )
    print("SUCCESS! Response:", response.choices[0].message.content)
except Exception as e:
    print("ERROR:", str(e))