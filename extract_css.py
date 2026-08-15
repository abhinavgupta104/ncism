import codecs, re

html = codecs.open('src/_layout.html', encoding='utf-8').read()

style_match = re.search(r'<style>(.*?)</style>', html, re.S)
if style_match:
    css = style_match.group(1).strip()
    with codecs.open('src/style.css', 'w', encoding='utf-8') as f:
        f.write(css)
    
    new_html = html[:style_match.start()] + '<link rel="stylesheet" href="src/style.css">\n' + html[style_match.end():]
    with codecs.open('src/_layout.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Extracted CSS to src/style.css")
else:
    print("No <style> block found.")
