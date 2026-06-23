from pymilvus import MilvusClient, DataType
import os
import shutil

# Если база уже существует — удаляем её вручную
if os.path.exists("./milvus_data.db"):
    shutil.rmtree("./milvus_data.db")
    print("🗑️ Старая база удалена")

print(" Подключение к Milvus Lite...")

client = MilvusClient(uri="./milvus_data.db")

# Создаём схему с правильными типами данных
schema = client.create_schema(auto_id=True)
schema.add_field("id", DataType.INT64, is_primary=True)  # ← DataType.INT64, не строка
schema.add_field("vector", DataType.FLOAT_VECTOR, dim=3)

client.create_collection("test_collection", schema=schema)
print("✅ Коллекция создана")

# Вставляем данные
client.insert("test_collection", [
    {"vector": [0.1, 0.2, 0.3]},
    {"vector": [0.9, 0.8, 0.7]}
])
print("✅ Данные вставлены")

# Ищем
results = client.search("test_collection", data=[[0.15, 0.25, 0.35]], limit=2)
print(f"✅ Результаты поиска: {results}")

print("\n🎉 Milvus Lite работает!")