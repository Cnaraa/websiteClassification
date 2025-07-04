from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import warnings
import os

warnings.filterwarnings("ignore", category=UserWarning)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

model_path = r"D:\models\rut5-base-absum"

try:
    tokenizer = AutoTokenizer.from_pretrained(model_path, legacy=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True)
    print("Модель успешно загружена")
except Exception as e:
    print(f"Ошибка при загрузке модели: {e}")
    exit()


def summarize(text, max_length=96):
    if not text or len(text.strip()) < 50:
        print("Текст слишком короткий")
        return None

    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="longest", max_length=512)
        with torch.no_grad():
            summary_ids = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=max_length,       
                min_length=60,
                length_penalty=1.5,
                num_beams=8,
                no_repeat_ngram_size=2,
                repetition_penalty=1.2,
                early_stopping=True,
                do_sample=True,
                top_k=50,
                top_p=0.95)

        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        return summary

    except Exception as e:
        print(f"Ошибка при суммаризации: {e}")
        return None