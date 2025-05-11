from text_preprocessing import preprocess_text

text = 'Привет! Это тестовый текст с лишними символами: 1234567890.'

result = preprocess_text(text)

print(f'Это исходный текст: {text}')
print("-" *100)
print(f'Это обработанный текст: {result}')