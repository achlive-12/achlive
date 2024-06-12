import requests
addr = 'bc1qy34z9zcfurachshrsflzwgshp9jn5qn0kpjtcd'
qr_code = requests.get(f'https://www.bitcoinqrcodemaker.com/api/?style=bitcoin&address={addr}&amount=30&color=1')
print(qr_code.text)