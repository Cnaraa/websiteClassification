import os
import pickle
import numpy as np
import tensorflow as tf
from custom_layers import AttentionLayer
from custom_losses import FocalLoss
from text_preprocessing import preprocess_text

model = None
tokenizer = None
label_encoder = None
MAX_SEQUENCE_LENGTH = 128

def load_components():
    global model, tokenizer, label_encoder
    model_path = os.path.join(os.path.dirname(__file__), 'text_classification_model.keras')
    tokenizer_path = os.path.join(os.path.dirname(__file__), 'tokenizer.pkl')
    label_encoder_path = os.path.join(os.path.dirname(__file__), 'label_encoder.pkl')
    
    try:
        model = tf.keras.models.load_model(
            model_path,
            custom_objects={
                'AttentionLayer': AttentionLayer,
                'FocalLoss': FocalLoss 
            }
        )
        print("Модель успешно загружена.")
        
        with open(tokenizer_path, 'rb') as f:
            tokenizer = pickle.load(f)
        print("Токенизатор успешно загружен.")
        
        # Загрузка кодировщика меток
        with open(label_encoder_path, 'rb') as f:
            label_encoder = pickle.load(f)
        print("Кодировщик меток успешно загружен.")
    
    except FileNotFoundError as ex:
        print(f"Ошибка: Файл не найден - {ex}")
        raise RuntimeError("Не удалось загрузить компоненты.")
    except Exception as ex:
        print(f"Ошибка при загрузке компонентов: {ex}")
        raise RuntimeError("Не удалось загрузить компоненты.")

def classify_text(title, description):
    if not title or not description:
        raise ValueError("Заголовок и описание не должны быть пустыми.")
    
    text = f"{title} {description}"
    print(f"Исходный текст: {text}")
    
    preprocessed_text = preprocess_text(text)
    print(f"Предобработанный текст: {preprocessed_text}")
    
    sequence = tokenizer.texts_to_sequences([preprocessed_text])
    
    if not sequence or not sequence[0]:
        raise ValueError("Текст не содержит известных токенов. Убедитесь, что токенизатор был обучен на аналогичных данных.")
    
    padded_sequence = tf.keras.preprocessing.sequence.pad_sequences(
        sequence, maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post'
    )
    
    predictions = model.predict(padded_sequence)
    predicted_label = np.argmax(predictions, axis=1)
    
    return label_encoder.inverse_transform(predicted_label)[0]

load_components()