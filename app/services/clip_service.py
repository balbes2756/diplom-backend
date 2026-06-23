from sentence_transformers import SentenceTransformer
from PIL import Image
import io
from typing import List, Optional

class CLIPService:
    def __init__(self):
        print("⏳ Загрузка CLIP модели через sentence-transformers...")
        # Используем CLIP через sentence-transformers (проще и надёжнее)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ CLIP модель загружена")

    def get_text_embedding(self, text: str) -> List[float]:
        """Генерирует эмбеддинг для текста"""
        # encode() автоматически нормализует вектор
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def get_image_embedding(self, image_bytes: bytes) -> List[float]:
        """Генерирует эмбеддинг для изображения"""
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # encode() принимает PIL Image напрямую
        embedding = self.model.encode(image, normalize_embeddings=True)
        return embedding.tolist()

    def get_combined_embedding(self, text: str, image_bytes: Optional[bytes] = None) -> List[float]:
        """Комбинирует текст и изображение (если есть)"""
        text_emb = self.get_text_embedding(text)
        
        if image_bytes:
            image_emb = self.get_image_embedding(image_bytes)
            # Усредняем векторы
            combined = [0.45 * t + 0.55 * i for t, i in zip(text_emb, image_emb)]
            # Нормализуем после усреднения
            norm = sum(x**2 for x in combined) ** 0.5
            if norm > 0:
                return [x / norm for x in combined]
        
        return text_emb

# Глобальный экземпляр
clip_service = CLIPService()