from app.services.clip_service import clip_service

print("🧪 Тестирование CLIP-сервиса...")

# Тест 1: текстовый эмбеддинг
text = "рыжий кот, дружелюбный"
text_emb = clip_service.get_text_embedding(text)
print(f"✅ Текстовый эмбеддинг: размерность = {len(text_emb)}")
print(f"   Первые 5 значений: {text_emb[:5]}")

# Тест 2: проверка нормализации (должна быть ~1.0)
import math
norm = math.sqrt(sum(x**2 for x in text_emb))
print(f"✅ Норма вектора: {norm:.4f} (должна быть ~1.0)")

print("\n🎉 CLIP-сервис работает!")