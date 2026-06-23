from pymilvus import MilvusClient

# Подключаемся к Milvus
client = MilvusClient(uri="./milvus_data.db")

collection_name = "pet_embeddings"

print("=" * 60)
print("🔍 ДИАГНОСТИКА MILVUS")
print("=" * 60)

# 1. Проверяем, существует ли коллекция
if not client.has_collection(collection_name):
    print(f"❌ Коллекция '{collection_name}' не найдена!")
    exit()

print(f"✅ Коллекция '{collection_name}' существует")

# 2. Загружаем коллекцию
client.load_collection(collection_name)
print("✅ Коллекция загружена в память")

# 3. Получаем статистику
stats = client.get_collection_stats(collection_name)
print(f"📊 Статистика коллекции: {stats}")

# 4. Получаем все записи
results = client.query(
    collection_name=collection_name,
    filter="",  # Без фильтра
    output_fields=["pet_id", "status", "pet_type"],
    limit=100
)

print(f"\n📋 Записей в коллекции: {len(results)}")
for i, record in enumerate(results):
    print(f"   {i+1}. pet_id={record['pet_id']}, status={record['status']}, type={record['pet_type']}")

# 5. Тестовый поиск с первым эмбеддингом
if len(results) > 0:
    print("\n🧪 Тестовый поиск...")
    
    # Берём первый эмбеддинг из базы
    first_record = results[0]
    
    # Получаем сам вектор (нужен отдельный запрос)
    vector_result = client.query(
        collection_name=collection_name,
        filter=f"pet_id == {first_record['pet_id']}",
        output_fields=["embedding"],
        limit=1
    )
    
    if vector_result:
        test_embedding = vector_result[0]['embedding']
        print(f"✅ Взяли эмбеддинг pet_id={first_record['pet_id']}, размерность: {len(test_embedding)}")
        
        # Ищем похожие
        search_results = client.search(
            collection_name=collection_name,
            data=[test_embedding],
            limit=5,
            output_fields=["pet_id", "status", "pet_type"]
        )
        
        print(f"\n🔎 Результаты поиска (топ-5):")
        for hits in search_results:
            for hit in hits:
                print(f"   - pet_id={hit['entity']['pet_id']}, status={hit['entity']['status']}, type={hit['entity']['pet_type']}, distance={hit['distance']:.4f}")

print("\n" + "=" * 60)