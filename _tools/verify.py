
import json, os, re, difflib
D = r'C:\Users\22084\Desktop\腾讯云FDE'
b = json.load(open(os.path.join(D,'_raw','blocks.json'), encoding='utf-8'))
def norm(s): return re.sub(r'\s+', '', s)
for f in sorted(b):
    src = norm(open(os.path.join(D,f), encoding='utf-8').read())
    out = []
    for x in b[f]:
        t = x['t']
        if t in ('h1','lead','p','callout','code'): out.append(x['text'])
        elif t == 'h2': out.append(x['num'] + x['text'])
        elif t == 'h3': out.append(x['text'])
        elif t == 'objectives': out.extend(x['items'])
        elif t == 'table': out.extend(''.join(r) for r in x['rows'])
        elif t == 'list':
            for i in x['items']:
                out.append(i.get('text',''))
                out.extend(i.get('sub') or [])
        elif t == 'defs':
            for i in x['items']: out.append(i['term'] + i['desc'])
        elif t == 'figure':
            out.append(x.get('title','')); out.append(x.get('caption',''))
    got = norm(''.join(out))
    sm = difflib.SequenceMatcher(None, src, got, autojunk=False)
    r = sm.ratio()
    print(f, 'ratio %.4f' % r, 'src', len(src), 'out', len(got))
    if r < 0.999:
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != 'equal':
                print('   ', tag, 'SRC[', src[i1:i2][:60], '] OUT[', got[j1:j2][:60], ']')
