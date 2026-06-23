from pymilvus import MilvusClient, DataType
from typing import List, Dict

class MilvusService:
    def __init__(self):
        self.client = MilvusClient(uri="./milvus_data.db")
        print("✅ Подключено к Milvus Lite")
        
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

        # Индекс HNSW для быстрого поиска
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="embedding",
            metric_type="COSINE",
            index_type="HNSW",
            params={"M": 16, "efConstruction": 200}
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )
        print(f"✅ Коллекция '{self.collection_name}' создана с индексом HNSW")

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
            filter=filter_expr,  # ← Фильтр по статусу И типу
            output_fields=["pet_id", "status", "pet_type"],
            search_params={"metric_type": "COSINE", "params": {"ef": 64}}
        )

        matches = []
        for hits in results:
            for hit in hits:
                # ✅ УЖЕСТЧАЕМ ПОРОГ: distance < 0.20 (similarity > 0.80)
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