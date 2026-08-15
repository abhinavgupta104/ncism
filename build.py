import re, base64, os, mimetypes

src = open('src/page.html', encoding='utf-8').read()
fonts = open('assets/fonts/fonts.css', encoding='utf-8').read()

# 1. inline fonts
html = src.replace('/*__FONTS__*/', fonts)

# 2. inline local images as data URIs
def inline(m):
    attr, path = m.group(1), m.group(2)
    if path.startswith(('data:', 'http')):
        return m.group(0)
    if not os.path.exists(path):
        print('  !! missing:', path)
        return m.group(0)
    mime = mimetypes.guess_type(path)[0] or 'image/jpeg'
    b64 = base64.b64encode(open(path, 'rb').read()).decode()
    print(f'  inlined {path} ({os.path.getsize(path)/1024:.0f} KB)')
    return f'{attr}="data:{mime};base64,{b64}"'

html = re.sub(r'(src)="([^"]+\.(?:png|jpg|jpeg|gif|svg|webp))"', inline, html)

open('index.html', 'w', encoding='utf-8').write(html)
print(f'\nindex.html: {os.path.getsize("index.html")/1024:.0f} KB')
