import duckduckgo

for r in duckduckgo.query('Sausages').results:
    print(r.url + ' - ' + r.text)
