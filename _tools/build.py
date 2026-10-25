
# -*- coding: utf-8 -*-
import json, os, re, html

D = r'C:\Users\22084\Desktop\腾讯云FDE'
blocks = json.load(open(os.path.join(D,'_raw','blocks.json'), encoding='utf-8'))
SVGDIR = os.path.join(D, '配图', 'svg')
CH_ORDER = sorted(blocks.keys())

BT = chr(96)

def esc(s): return html.escape(s, quote=False)

def inline(text):
    t = esc(text)
    t = re.sub(BT + '([^' + BT + ']+)' + BT, r'<code class="ic">\1</code>', t)
    t = re.sub(r'\*\*([^*\n]+)\*\*', r'<strong>\1</strong>', t)
    def rep(m):
        n = int(m.group(1))
        if 1 <= n <= 12:
            return '<a class="xref" href="#ch%02d">%s</a>' % (n, m.group(0))
        return m.group(0)
    return re.sub(r'第\s?(\d{1,2})\s?章', rep, t)

def chapter_no(title):
    m = re.match(r'^(\d{1,2})\s+(.*)$', title)
    return (int(m.group(1)), m.group(2)) if m else (0, title)

def svg_inline(path):
    raw = open(path, encoding='utf-8').read()
    raw = re.sub(r'<\?xml[^>]*\?>', '', raw)
    raw = re.sub(r'<!DOCTYPE[^>]*>', '', raw).strip()
    m = re.search(r'<svg\b[^>]*>', raw)
    if m:
        tag = m.group(0)
        tag2 = re.sub(r'\s(?:width|height|style)="[^"]*"', '', tag)
        raw = raw[:m.start()] + tag2 + raw[m.end():]
    return raw

def render_table(rows):
    if not rows: return ''
    head, body = rows[0], rows[1:]
    out = ['<div class="table-wrap"><table>',
           '<thead><tr>' + ''.join('<th>%s</th>' % inline(c) for c in head) + '</tr></thead>', '<tbody>']
    for r in body:
        cells = r + [''] * (len(head) - len(r))
        out.append('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in cells[:len(head)]) + '</tr>')
    out.append('</tbody></table></div>')
    return '\n'.join(out)

def render_list(b):
    cls = b.get('cls', ''); items = b.get('items', [])
    if not items: return ''
    if len(items) == 1 and not cls and not (items[0].get('sub')):
        return '<p>%s</p>' % inline(items[0].get('text',''))
    out = ['<ul class="doc-list %s">' % cls]
    for it in items:
        t = it.get('text', '')
        m = re.match(r'^([^：:]{1,14})[：:]\s*(.+)$', t)
        if cls == 'term' and m:
            out.append('<li><strong>%s</strong><span class="sep">：</span>%s</li>' % (inline(m.group(1)), inline(m.group(2))))
        else:
            out.append('<li>%s' % inline(t))
            sub = it.get('sub') or []
            if sub:
                out.append('<ul class="sub">' + ''.join('<li>%s</li>' % inline(x) for x in sub) + '</ul>')
            out.append('</li>')
    out.append('</ul>')
    return '\n'.join(out)

def render_figure(b):
    f = b.get('file')
    if not f: return ''
    caption = b.get('caption', '')
    stem = os.path.splitext(f)[0]
    target = os.path.join(SVGDIR, stem + '.svg')
    if not os.path.exists(target):
        alt = os.path.join(D, '配图', stem + '.svg')
        if os.path.exists(alt):
            target = alt
    if os.path.exists(target):
        media = '<div class="fig-svg">%s</div>' % svg_inline(target)
        kind = '矢量重绘'
    else:
        w = h = 0
        try:
            from PIL import Image
            with Image.open(os.path.join(D, '配图', f)) as im:
                w, h = im.size
        except Exception:
            pass
        attr = (' width="%d" height="%d" style="aspect-ratio:%d/%d"' % (w, h, w, h)) if w and h else ''
        media = '<img src="配图/%s" alt="%s" loading="lazy"%s>' % (f, esc(caption), attr)
        kind = '原图'
    title = b.get('title', '')
    if title and caption.startswith(title) and len(caption) > len(title) + 3:
        rest = caption[len(title):].lstrip('：: ')
        cap = '<figcaption><span class="fig-title">%s</span>%s</figcaption>' % (inline(title), inline(rest))
    else:
        cap = '<figcaption><span class="fig-title">%s</span></figcaption>' % inline(caption)
    return '<figure class="doc-fig" data-kind="%s">%s%s</figure>' % (kind, media, cap)

TAGS = ['概念','用法','示例','注意','注意事项','陷阱','为什么','风险提示','提示','背景','原理','误区','小结','总结','案例','练习','补充','延伸','对比','关键','一句话','常见问题','问题处理','提醒','要点','结论','怎么用','最硬判据','自检']

def tagclass(label):
    if label in ('概念','背景','原理'): return 'concept'
    if label in ('用法','怎么用'): return 'usage'
    if label in ('示例','案例','练习'): return 'example'
    if label in ('注意','注意事项','风险提示','陷阱','误区','提醒'): return 'warn'
    return 'plain'

LABELS_ONLY = ('概念','用法','示例','注意','注意事项','小结','总结','案例','练习','补充','延伸','对比')

def render_h3(b):
    t = b['text']
    if t.strip() in LABELS_ONLY:
        return '<h3 class="sec-sub"><span class="tag tag-%s">%s</span></h3>' % (tagclass(t.strip()), esc(t.strip()))
    if b.get('cls') == 'q':
        mq = re.match(r'^(Q\d+)[：:]\s*(.*)$', t)
        if mq: return '<h3 class="faq-q"><span class="qno">%s</span>%s</h3>' % (esc(mq.group(1)), inline(mq.group(2)))
    m = re.match(r'^(' + '|'.join(TAGS) + r')[：:]\s*(.*)$', t)
    if m:
        return '<h3 class="sec-sub"><span class="tag tag-%s">%s</span><span class="h3-text">%s</span></h3>' % (tagclass(m.group(1)), esc(m.group(1)), inline(m.group(2)))
    m2 = re.match(r'^(陷阱[一二三四五]|模式[一二三四五]|第[一二三四五]步)[：:]\s*(.*)$', t)
    if m2:
        return '<h3 class="sec-sub"><span class="tag tag-plain">%s</span><span class="h3-text">%s</span></h3>' % (esc(m2.group(1)), inline(m2.group(2)))
    return '<h3 class="sec-sub"><span class="h3-text">%s</span></h3>' % inline(t)

chapters = []
stats = {'sections':0,'summaries':0,'figures':0,'tables':0,'code':0,'chars':0,'callouts':0,'defs':0}
for f in CH_ORDER:
    bl = blocks[f]
    no, ctitle = chapter_no(bl[0]['text'])
    parts = []; n_sec = 0; secs = []
    for b in bl[1:]:
        t = b['t']
        if t == 'lead':
            parts.append('<p class="lead">%s</p>' % inline(b['text'])); stats['chars'] += len(b['text'])
        elif t == 'objectives':
            items = ''.join('<li>%s</li>' % inline(x) for x in b['items'])
            parts.append('<div class="objectives"><div class="obj-head">本节目标</div><ul>%s</ul></div>' % items)
            stats['chars'] += sum(len(x) for x in b['items'])
        elif t == 'h2':
            n_sec += 1
            sid = 's%s' % b['num'].replace('.', '-')
            is_sum = '本章小结' in b['text']
            cls = 'h2 summary' if is_sum else 'h2'
            if is_sum: stats['summaries'] += 1
            parts.append('<h2 id="%s" class="%s"><span class="h2-num">%s</span><span class="h2-text">%s</span></h2>' % (sid, cls, esc(b['num']), inline(b['text'])))
            secs.append((b['num'], b['text'], sid, is_sum))
        elif t == 'h3':
            parts.append(render_h3(b)); stats['chars'] += len(b['text'])
        elif t == 'h4':
            parts.append('<h4 class="sec-h4">%s</h4>' % inline(b['text'])); stats['chars'] += len(b['text'])
        elif t == 'p':
            parts.append('<p>%s</p>' % inline(b['text'])); stats['chars'] += len(b['text'])
        elif t == 'defs':
            rows = ''.join('<div class="def"><div class="def-t">%s</div><p>%s</p></div>' % (inline(x['term']), inline(x['desc'])) for x in b['items'])
            parts.append('<div class="defs">%s</div>' % rows)
            stats['chars'] += sum(len(x['term']) + len(x['desc']) for x in b['items'])
            stats['defs'] += 1
        elif t == 'table':
            parts.append(render_table(b['rows'])); stats['tables'] += 1
            stats['chars'] += sum(len(c) for r in b['rows'] for c in r)
        elif t == 'list':
            parts.append(render_list(b)); stats['chars'] += sum(len(i.get('text','')) for i in b['items'])
        elif t == 'callout':
            rest = b['text']; m = re.match(r'^(风险提示|提示|注意)[：:]\s*(.*)$', rest)
            body = m.group(2) if m else rest
            label = m.group(1) if m else ('风险提示' if b['kind']=='warn' else '要点')
            parts.append('<div class="callout %s"><div class="callout-head">%s</div><p>%s</p></div>' % (b['kind'], label, inline(body)))
            stats['callouts'] += 1; stats['chars'] += len(body)
        elif t == 'figure':
            parts.append(render_figure(b)); stats['figures'] += 1
        elif t == 'code':
            box = any(ch in b['text'] for ch in '│├└┌┐┘┗┴┬┼─▼')
            cls = 'code ascii' if box else 'code'
            parts.append('<pre class="%s"><code>%s</code></pre>' % (cls, esc(b['text'])))
            stats['code'] += 1; stats['chars'] += len(b['text'])
    stats['sections'] += sum(1 for s in secs if not s[3])
    chapters.append({'no':no,'title':ctitle,'html':'\n'.join(parts),'secs':secs})

CSS = open(os.path.join(D,'_tools','style.css'), encoding='utf-8').read()
JS  = open(os.path.join(D,'_tools','app.js'), encoding='utf-8').read()

nav = ['<nav class="toc" id="toc">']
for c in chapters:
    nav.append('<div class="toc-group" data-ch="%02d">' % c['no'])
    nav.append('<a class="toc-ch" href="#ch%02d"><span class="toc-no">%02d</span><span class="toc-t">%s</span></a>' % (c['no'], c['no'], inline(c['title'])))
    nav.append('<div class="toc-secs">')
    for (num, txt, sid, is_sum) in c['secs']:
        cls = 'toc-sec summary' if is_sum else 'toc-sec'
        nav.append('<a class="%s" href="#%s" data-txt="%s"><span class="s-no">%s</span><span class="s-t">%s</span></a>' % (cls, sid, esc(txt), esc(num), inline(txt)))
    nav.append('</div></div>')
nav.append('</nav>')
nav = '\n'.join(nav)

body_chapters = []
for c in chapters:
    body_chapters.append(
      '<section class="chapter" id="ch%02d" data-ch="%02d">\n'
      '  <header class="chapter-head">\n'
      '    <div class="ch-eyebrow">第 %02d 章</div>\n'
      '    <h1>%s</h1>\n'
      '  </header>\n%s\n</section>' % (c['no'], c['no'], c['no'], inline(c['title']), c['html']))
chapters_html = '\n'.join(body_chapters)

HTML = f'''<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>腾讯云 FDE 培训 · 全章文字与配图</title>
<meta name="description" content="腾讯云人工智能前沿部署工程师（FDE）培训课程全 {stats['sections']} 节文字与 {stats['figures']} 张配图的离线阅读版">
<style>{CSS}</style>
</head>
<body>
<div class="progress"><div class="progress-bar" id="progressBar"></div></div>

<header class="topbar">
  <button class="icon-btn only-mobile" id="menuBtn" aria-label="目录">☰</button>
  <a class="brand" href="#top">
    <span class="brand-dot"></span>
    <span class="brand-name">腾讯云 FDE 培训</span>
    <span class="brand-sub">全章文字与配图</span>
  </a>
  <div class="search">
    <span class="search-ico">⌕</span>
    <input id="searchInput" type="search" placeholder="搜索章节标题、问题或关键词…" autocomplete="off">
    <span class="search-count" id="searchCount"></span>
  </div>
  <button class="icon-btn" id="themeBtn" aria-label="切换主题">◐</button>
</header>

<div class="layout">
  <aside class="sidebar" id="sidebar">
    <div class="side-head">
      <div class="side-title">课程目录</div>
      <div class="side-meta">{len(chapters)} 章 · {stats['sections']} 节 · {stats['figures']} 图</div>
    </div>
    {nav}
  </aside>
  <div class="scrim" id="scrim"></div>

  <main class="content" id="top">
    <section class="hero">
      <div class="hero-eyebrow">腾讯云培训认证 · 学习路径</div>
      <h1 class="hero-title">腾讯云人工智能<br>前沿部署工程师（FDE）</h1>
      <p class="hero-desc">从角色认知到 WorkBuddy 实操，从进场挖需求到交付验收与组织沉淀，再到安全治理与 CFO 财务结算审核实战。本页把整门课的文字、表格、代码与配图整理成可离线查阅的一本电子书。</p>
      <div class="hero-stats">
        <div class="stat"><b>{len(chapters)}</b><span>章</span></div>
        <div class="stat"><b>{stats['sections']}</b><span>节正文</span></div>
        <div class="stat"><b>{stats['figures']}</b><span>张配图</span></div>
        <div class="stat"><b>{stats['tables']}</b><span>张表格</span></div>
        <div class="stat"><b>{stats['callouts']}</b><span>处风险提示</span></div>
      </div>
      <div class="hero-hint">按 <kbd>Ctrl</kbd> + <kbd>F</kbd> 全文搜索，或用右上角搜索框按章节定位。</div>
    </section>

    {chapters_html}

    <footer class="foot">
      <div>共 {len(chapters)} 章 {stats['sections']} 节 · {stats['figures']} 张配图 · 内容整理自腾讯云培训认证课程</div>
      <div class="foot-dim">离线阅读版 · 生成于 {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}</div>
    </footer>
  </main>
</div>

<button class="to-top" id="toTop" aria-label="回到顶部">↑</button>
<script>{JS}</script>
</body>
</html>
'''
open(os.path.join(D,'index.html'),'w',encoding='utf-8').write(HTML)
print('index.html', os.path.getsize(os.path.join(D,'index.html')))
print(json.dumps(stats, ensure_ascii=False))
