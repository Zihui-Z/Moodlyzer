import google.generativeai as genai

genai.configure(api_key="AIzaSyAav00BY2N0plqBqz05CW9sWijhEuPMSo8")

models = genai.list_models()

for m in models:
    print(m.name)