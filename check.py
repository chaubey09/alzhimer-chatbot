import google.generativeai as genai

genai.configure(api_key="AIzaSyAAndXwQ9jGyBNkfnNo70j8rQq4cqwYe-k")

for m in genai.list_models():
    print(m.name, " - ", m.supported_generation_methods)
