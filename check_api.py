import requests

# Get all motorcycles with pagination
all_motos = []
page = 1
while True:
    r = requests.get(f'http://localhost:8000/api/v1/bikes/motorcycles?per_page=50&page={page}')
    data = r.json()
    items = data.get('items', [])
    all_motos.extend(items)
    meta = data.get('meta', {})
    if page >= meta.get('total_pages', 1):
        break
    page += 1

print(f"Total models fetched: {len(all_motos)}")

# Find Benelli and Bajaj
benelli_models = [m for m in all_motos if 'benelli' in m.get('brand_id','').lower() or 'Benelli' in m.get('brand_name','')]
bajaj_models = [m for m in all_motos if 'bajaj' in m.get('brand_id','').lower() or 'Bajaj' in m.get('brand_name','')]

print(f"\nBenelli models: {len(benelli_models)}")
print(f"Bajaj models: {len(bajaj_models)}")

# Show a sample item
if all_motos:
    print("\n--- Sample model keys ---")
    print(list(all_motos[0].keys()))
    print("\n--- Sample model ---")
    print(all_motos[0])
    
# Show models with thumbnail
with_thumb = [m for m in all_motos if m.get('thumbnail_url')]
print(f"\nModels with thumbnail_url: {len(with_thumb)}")
for m in with_thumb:
    print(m.get('name'), '|', m.get('thumbnail_url'))
