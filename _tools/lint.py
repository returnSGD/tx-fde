
import re, html
h = open(r'C:\Users\22084\Desktop\腾讯云FDE\index.html', encoding='utf-8').read()
body = h.split('<main', 1)[1]
body = re.sub(r'<script[\s\S]*?</script>', '', body)
body = re.sub(r'<pre class="code[\s\S]*?</pre>', '\n[CODE]\n', body)
text = re.sub(r'<[^>]+>', '\n', body)
text = html.unescape(text)
lines = [l.strip() for l in text.split('\n')]
lines = [l for l in lines if l]
BT = chr(96)
bad = []
for l in lines:
    if re.match(r'^#{1,6}\s', l): bad.append(('md-h', l[:80]))
    elif l.count('|') >= 2 and '｜' not in l: bad.append(('pipe', l[:80]))
    elif '**' in l: bad.append(('bold', l[:80]))
    elif re.match(r'^\s*>\s', l): bad.append(('quote', l[:80]))
    elif BT in l: bad.append(('backtick', l[:80]))
print('suspect:', len(bad))
for b in bad[:30]: print(b)
