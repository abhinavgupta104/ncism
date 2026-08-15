from html.parser import HTMLParser
import re

html_data = open('scrape/index.php.html', encoding='utf-8').read()
m = re.search(r'<ul class="navbar-nav[^>]*>(.*?)</ul>\s*(?:<div class="others-options|<\/div>)', html_data, re.IGNORECASE | re.DOTALL)
if not m:
    # Just try to grab anything between <ul class="navbar-nav and the next </ul> that closes it
    # We can do this with basic string finding
    start = html_data.find('<ul class="navbar-nav')
    if start == -1:
        print("Could not find <ul class='navbar-nav'")
        exit(1)
    
    # naive extraction of the block
    count = 0
    end = -1
    for i in range(start, len(html_data) - 4):
        if html_data[i:i+3] == '<ul': count += 1
        elif html_data[i:i+4] == '</ul':
            count -= 1
            if count == 0:
                end = i + 5
                break
    
    if end != -1:
        nav_html = html_data[start:end]
    else:
        print("Could not parse ul properly")
        exit(1)
else:
    nav_html = m.group(0)

class NavParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tree = []
        self.stack = [{'tag': 'root', 'children': [], 'text': ''}]

    def handle_starttag(self, tag, attrs):
        node = {'tag': tag, 'attrs': dict(attrs), 'children': [], 'text': ''}
        self.stack[-1]['children'].append(node)
        self.stack.append(node)

    def handle_endtag(self, tag):
        if len(self.stack) > 1:
            self.stack.pop()

    def handle_data(self, data):
        if data.strip():
            self.stack[-1]['text'] += data.strip() + ' '

parser = NavParser()
parser.feed(nav_html)
root = parser.stack[0]

def convert_to_new_format(node, depth=0):
    if node['tag'] == 'li' and 'nav-item' in node['attrs'].get('class', ''):
        a_tag = next((c for c in node['children'] if c['tag'] == 'a'), None)
        if not a_tag: return ""
        
        link_text = a_tag['text'].strip().replace('▼', '').replace('down', '')
        link_text = re.sub(r'bx bx-chevron-down', '', link_text)
        link_text = link_text.strip()
        
        ul_tag = next((c for c in node['children'] if c['tag'] == 'ul'), None)
        if ul_tag:
            html = f'<li><button class="nav-btn">{link_text} <i>▼</i></button>\n  <div class="drop">\n'
            for child in ul_tag['children']:
                html += convert_to_new_format(child, depth+1)
            html += '  </div>\n</li>\n'
            return html
        else:
            href = a_tag['attrs'].get('href', '#')
            if depth == 0:
                return f'<li><a href="{href}" class="nav-btn">{link_text}</a></li>\n'
            else:
                return f'<a href="{href}">{link_text}</a>\n'
    
    html = ""
    for child in node['children']:
        html += convert_to_new_format(child, depth)
    return html

output = "<ul>\n"
for child in root['children']:
    output += convert_to_new_format(child)
output += "</ul>\n"

open('new_nav.html', 'w', encoding='utf-8').write(output)
print("Saved to new_nav.html")
