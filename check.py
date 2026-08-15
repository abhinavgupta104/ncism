import re
from html.parser import HTMLParser
src=open('src/page.html',encoding='utf-8').read()
body=re.sub(r'<(script|style)\b.*?</\1>','',src,flags=re.S|re.I)
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class P(HTMLParser):
    def __init__(s):super().__init__();s.st=[];s.er=[]
    def handle_starttag(s,t,a):
        if t not in VOID:s.st.append((t,s.getpos()))
    def handle_endtag(s,t):
        if t in VOID:return
        if not s.st:s.er.append(f'stray </{t}> {s.getpos()}');return
        if s.st[-1][0]!=t:
            s.er.append(f'</{t}> at {s.getpos()} but open <{s.st[-1][0]}> from {s.st[-1][1]}')
            for i in range(len(s.st)-1,-1,-1):
                if s.st[i][0]==t:del s.st[i:];return
        else:s.st.pop()
p=P();p.feed(body)
print('tag errors:',p.er or 'none')
print('unclosed:',p.st or 'none')

css='\n'.join(re.findall(r'<style>(.*?)</style>',src,re.S))
used=set(re.findall(r'var\(\s*(--[\w-]+)',css));dec=set(re.findall(r'(--[\w-]+)\s*:',css))
print('undeclared vars:',sorted(used-dec) or 'none')
root=re.search(r':root\{(.*?)\n\}',css,re.S).group(1)
rv={v for v in re.findall(r'(--[\w-]+)\s*:',root)}
med=re.search(r'@media \(prefers-color-scheme:dark\)\{\s*:root:not\(\[data-theme="light"\]\)\{(.*?)\n  \}',css,re.S)
stm=re.search(r':root\[data-theme="dark"\]\{(.*?)\n\}',css,re.S)
mv=set(re.findall(r'(--[\w-]+)\s*:',med.group(1))) if med else set()
sv=set(re.findall(r'(--[\w-]+)\s*:',stm.group(1))) if stm else set()
print('dark-media overrides:',len(mv),'| dark-stamp overrides:',len(sv))
print('media vs stamp mismatch:',sorted(mv^sv) or 'none')
print('defined ONLY in dark (bug):',sorted((mv|sv)-rv) or 'none')
print('root vars NOT themed:',sorted(rv-sv))
ids=['progress','noticeList','ftbody','fq','fsys','fstate','fstatus','fcount','navbar','navToggle','navList','tickerTrack','tickerPause','themeBtn','themeIcon','themeTxt','langBtn']
print('all JS ids present:',all(f'id="{i}"' in src for i in ids))
