import requests
from bs4 import BeautifulSoup as bs

response = requests.get('https://www.hell-let-loose-calculator.com/foy')
soup = bs(response.content, 'html.parser')

print('Status:', response.status_code)
print('Content length:', len(response.content))
print('\nFirst 2000 chars:')
print(response.text[:2000])

print('\n\n=== Looking for gun elements ===')
gun_elements = soup.find_all('div', class_='v-list-item-title text-h6')
print(f'Found {len(gun_elements)} elements with class "v-list-item-title text-h6"')

# Try other methods
print('\n=== Looking for v-list-item-title class ===')
gun_elements2 = soup.find_all('div', class_='v-list-item-title')
print(f'Found {len(gun_elements2)} elements with class "v-list-item-title"')

print('\n=== Looking for text-h6 class ===')
gun_elements3 = soup.find_all('div', class_='text-h6')
print(f'Found {len(gun_elements3)} elements with class "text-h6"')

