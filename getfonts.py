import re, urllib.request, base64, os, io
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options

UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
url=("https://fonts.googleapis.com/css2?family=Spectral:wght@600;700"
     "&family=Public+Sans:wght@400;500;600&family=Tiro+Devanagari+Sanskrit&display=swap")
css=urllib.request.urlopen(urllib.request.Request(url,headers=UA)).read().decode()
blocks=re.findall(r'/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})', css, re.S)

# Devanagari text actually used on the page
DEVA = ("।।आयुषेसर्वलोकानाम् "
        "राष्ट्रीयभारतीयचिकित्सापद्धतिआयोग"
        "आयुर्वेदयूनानीसिद्धसोवारिग्पा"
        "मंत्रालयआयुषसरकारहिन्दीअंग्रेज़ी"
        "-–—.,()० १२३४५६७८९")

cache={}
def fetch(u):
    if u not in cache:
        cache[u]=urllib.request.urlopen(urllib.request.Request(u,headers=UA)).read()
    return cache[u]

# group: src url -> (family, subset, [weights])
groups={}
order=[]
for subset, blk in blocks:
    if subset not in ('latin','devanagari'): continue
    fam=re.search(r"font-family: '([^']+)'", blk).group(1)
    if fam.startswith('Tiro') and subset!='devanagari': continue
    wt=int(re.search(r'font-weight: (\d+)', blk).group(1))
    src=re.search(r'url\((https://[^)]+\.woff2)\)', blk).group(1)
    key=(fam,src)
    if key not in groups:
        groups[key]={'fam':fam,'src':src,'subset':subset,'wts':[]}
        order.append(key)
    groups[key]['wts'].append(wt)

out=[]
total=0
for key in order:
    g=groups[key]
    data=fetch(g['src'])
    label='full'
    if g['subset']=='devanagari':
        f=TTFont(io.BytesIO(data)); f.flavor=None
        opts=Options(); opts.layout_features='*'; opts.notdef_outline=True
        s=Subsetter(options=opts); s.populate(text=DEVA); s.subset(f)
        f.flavor='woff2'
        buf=io.BytesIO(); f.save(buf); data=buf.getvalue(); label='subset'
    wts=sorted(set(g['wts']))
    wcss = str(wts[0]) if len(wts)==1 else f'{wts[0]} {wts[-1]}'
    b64=base64.b64encode(data).decode()
    out.append("@font-face{font-family:'%s';font-style:normal;font-weight:%s;font-display:swap;"
               "src:url(data:font/woff2;base64,%s) format('woff2');}"%(g['fam'],wcss,b64))
    total+=len(data)
    print(f"{g['fam']:<26} w{wcss:<9} {g['subset']:<11} {label:<7} {len(data)/1024:6.1f} KB")

open('assets/fonts/fonts.css','w',encoding='utf-8').write('\n'.join(out))
print(f"\nfont binaries: {total/1024:.0f} KB -> fonts.css {os.path.getsize('assets/fonts/fonts.css')/1024:.0f} KB (base64)")
