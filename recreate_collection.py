from pymilvus import MilvusClient, DataType
import os
import shutil

# Удаляем старую базу
if os.path.exists("./milvus_data.db"):
    shutil.rmtree("./milvus_data.db")
    print("🗑️ Старая база Milvus удалена")

# Подключаемся
client = MilvusClient(uri="./milvus_data.db")
print("✅ Подключено к новой базе Milvus")

collection_name = "pet_embeddings"

# Создаём схему
schema = client.create_schema(auto_id=True, enable_dynamic_field=False)
schema.add_field("id", DataType.INT64, is_primary=True)
schema.add_field("pet_id", DataType.INT64)
schema.add_field("status", DataType.VARCHAR, max_length=20)
schema.add_field("pet_type", DataType.VARCHAR, max_length=20)
schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=512)

# ✅ КРИТИЧНО: явно указываем COSINE
index_params = client.prepare_index_params()
index_params.add_index(
    field_name="embedding",
    metric_type="COSINE",  # ← ЯВНО УКАЗЫВАЕМ COSINE
    index_type="HNSW",
    params={"M": 16, "efConstruction": 200}
)

# Создаём коллекцию
client.create_collection(
    collection_name=collection_name,
    schema=schema,
    index_params=index_params
)

print(f"✅ Коллекция '{collection_name}' создана с метрикой COSINE")

# Проверяем метрику
info = client.describe_collection(collection_name)
print(f"📊 Информация о коллекции: {info}")

# Проверяем индекс
index_info = client.describe_index(collection_name, "embedding")
print(f"📊 Информация об индексе: {index_info}")

print("\n🎉 Коллекция пересоздана! Теперь нужно заново создать объявления.")