from pymilvus import MilvusClient, DataType
from typing import List, Dict
import os

class MilvusService:
    def __init__(self):
        # ✅ Читаем URI и токен из переменных окружения
        uri = os.getenv("MILVUS_URI", "./milvus_data.db")
        token = os.getenv("MILVUS_TOKEN", "")
        
        if token:
            # ☁️ Подключение к Zilliz Cloud (production)
            self.client = MilvusClient(uri=uri, token=token)
            print(f"✅ Подключено к Zilliz Cloud: {uri}")
        else:
            # 💻 Локальный Milvus Lite (разработка)
            self.client = MilvusClient(uri=uri)
            print("✅ Подключено к Milvus Lite (локально)")
        
        self.collection_name = "pet_embeddings"
        self._create_collection()

    def _create_collection(self):
        if self.client.has_collection(self.collection_name):
            print(f"✅ Коллекция '{self.collection_name}' уже существует")
            return

        # Схема: ID (авто), ID питомца из PG, статус, тип, эмбеддинг (512)
        schema = self.client.create_schema(auto_id=True, enable_dynamic_field=False)
        schema.add_field("id", DataType.INT64, is_primary=True)
        schema.add_field("pet_id", DataType.INT64)
        schema.add_field("status", DataType.VARCHAR, max_length=20)
        schema.add_field("pet_type", DataType.VARCHAR, max_length=20)
        schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=512)

        # ✅ Индекс: AUTOINDEX для облака, HNSW для локальной версии
        index_params = self.client.prepare_index_params()
        
        if os.getenv("MILVUS_TOKEN"):
            # Zilliz Cloud — используем AUTOINDEX (оптимален для облака)
            index_params.add_index(
                field_name="embedding",
                metric_type="COSINE",
                index_type="AUTOINDEX",
                params={}
            )
            print("📊 Используется индекс AUTOINDEX (Zilliz Cloud)")
        else:
            # Локально — HNSW для быстрого поиска
            index_params.add_index(
                field_name="embedding",
                metric_type="COSINE",
                index_type="HNSW",
                params={"M": 16, "efConstruction": 200}
            )
            print(" Используется индекс HNSW (локально)")

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )
        print(f"✅ Коллекция '{self.collection_name}' создана")

    def insert_embedding(self, pet_id: int, embedding: List[float], status: str, pet_type: str):
        """Добавляет эмбеддинг в базу"""
        self.client.insert(
            collection_name=self.collection_name,
            data=[{
                "pet_id": pet_id,
                "status": status,
                "pet_type": pet_type,
                "embedding": embedding
            }]
        )

    def search_similar(self, query_embedding: List[float], status: str = None, pet_type: str = None, limit: int = 3) -> List[Dict]:
        """Ищет похожие объявления"""
        self.client.load_collection(self.collection_name)
    
        # Формируем фильтр
        filter_parts = []
        if status:
            filter_parts.append(f'status == "{status}"')
        if pet_type:
            filter_parts.append(f'pet_type == "{pet_type}"')
    
        filter_expr = " and ".join(filter_parts) if filter_parts else None
    
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_embedding],
            limit=limit,
            filter=filter_expr,
            output_fields=["pet_id", "status", "pet_type"],
            search_params={"metric_type": "COSINE"}
        )

        matches = []
        for hits in results:
            for hit in hits:
                # ✅ Строгий порог: distance < 0.10 (similarity > 0.90)
                if hit['distance'] < 0.10:
                    similarity = 1 - hit['distance']
                    matches.append({
                        "pet_id": hit['entity']['pet_id'],
                        "status": hit['entity'].get('status', 'unknown'),
                        "similarity": similarity
                    })
    
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return matches

# Глобальный экземпляр
milvus_service = MilvusService()