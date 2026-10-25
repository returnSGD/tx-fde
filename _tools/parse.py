
# -*- coding: utf-8 -*-
import os, re, json
D = r'C:\Users\22084\Desktop\腾讯云FDE'

FENCE = {
    '03.txt': [(43, 64), (89, 94)],
    '04.txt': [(51, 58), (66, 84), (106, 114)],
    '05.txt': [(173, 178), (273, 279)],
    '08.txt': [(271, 280), (283, 289), (292, 295)],
    '10.txt': [(109, 121), (241, 274)],
}

def norm(s):
    return re.sub(r'\s+', '', s).lower()

FIG = {
 'fde三步闭环':'fde_three_step_loop.svg',
 'echo/delta能力模型':'echo_delta_model.svg',
 '腾讯云几款主要的ai产品定位':'tool_matrix_position_map.svg',
 '客户落地四层门槛':'four_layer_gates.svg',
 'harness五件套：模型是发动机，五件套是整辆车':'harness_five_components.svg',
 '权限判断优先级流程：黑名单>白名单>默认允许':'permission_priority_flow.svg',
 '三层下挖法':'requirement_three_layers.png',
 '显性sop与真实流程对比':'hidden_process_comparison.png',
 '破解一线抵触的三步法':'resistance_three_steps.png',
 '三个候选场景的六维打分':'scenario_scoring_card.png',
 'pev交付闭环':'pev_loop.png',
 '四维验收框架':'acceptance_four_dimensions.png',
 'l0–l4成熟度框架':'l0_l4_maturity.svg',
 'landandexpand四阶段':'land_expand_stages.png',
 '双向蒸馏的两个方向':'distillation_two_directions.svg',
 'skill封装的两层结构':'skill_two_layers.png',
 '三态溯源':'evidence_three_states.png',
 '成本曲线对比：项目制vs本体化':'cost_curve_comparison.png',
 '沉淀载体三件套':'asset_carriers_three.png',
 '12周节奏：四阶段+四道gate':'twelve_week_timeline.png',
 '约束三层模型':'constraint_three_layers.png',
 '动作分级：可逆性×影响面':'approval_risk_matrix.png',
 '三类护栏':'guardrails_three_types.png',
 '四类能力资产':'four_capability_assets.png',
 'prompt五要素':'prompt_five_components.png',
 'agentloop四环节循环':'agent_loop_cycle.png',
 'workbuddy客户端界面五区域':'workbuddy_ui_five_areas.png',
 'workbuddy三端架构':'workbuddy_three_tier.svg',
 '能力下发四步链路':'capability_delivery_chain.png',
 'agent/runtime/session关系':'agent_runtime_session.svg',
 'fde×workbuddy实战全景图':'fde-workbuddy-method.jpg',
}

H3LAB = ['概念','用法','示例','注意','为什么','风险提示','提示','背景','原理','误区','小结','总结','案例','练习','补充','延伸','对比','关键','一句话','常见问题','问题处理','提醒','要点','结论','怎么用','最硬判据','自检']
TERM_RE = re.compile(r'^[^：:。，\t]{1,24}[：:]\s*\S')
LIST_RE = re.compile(r'^([-*+•·]|\d+[.、)]|\(\d+\)|[①②③④⑤⑥⑦⑧⑨⑩])\s*')

def ends_sentence(s):
    return bool(re.search(r'[。！？…]\s*$', s))

def is_fig_head(lines, i):
    s = lines[i].strip()
    if i+1 >= len(lines): return None
    nxt = lines[i+1].strip()
    if nxt == s and len(s) <= 40:
        return (s, s)
    if len(s) <= 30 and nxt.startswith(s) and len(nxt) > len(s) + 3:
        return (s, nxt)
    return None

def classify(lines, fname):
    blocks = []
    n = len(lines)
    if n == 0: return blocks
    fences = FENCE.get(fname, [])
    fenced = set()
    for (fa, fb) in fences:
        fenced.update(range(fa, fb + 1))
    blocks.append({'t':'h1','text':lines[0].strip()})
    i = 1
    while i < n and not lines[i].strip(): i += 1
    if i < n:
        blocks.append({'t':'lead','text':lines[i].strip()}); i += 1
    in_summary = False
    while i < n:
        ln = i + 1
        hit = None
        for (a,b) in fences:
            if a <= ln <= b: hit = (a,b); break
        if hit:
            body = lines[hit[0]-1:hit[1]]
            blocks.append({'t':'code','text':'\n'.join(x.rstrip() for x in body)})
            i = hit[1]
            continue
        line = lines[i]; s = line.strip()
        if not s: i += 1; continue
        if re.fullmatch(r'本\s*[节章]\s*目\s*标|目\s*标', s):
            i += 1; items = []
            while i < n and lines[i].strip() and len(items) < 8:
                items.append(lines[i].strip()); i += 1
            if len(items) > 1 and items[-1] and ends_sentence(items[-1]) and not ends_sentence(items[0]):
                i -= 1; items = items[:-1]
            if items and re.match(r'^(能|会|掌握|理解|了解|知道|识别|区分|用|说出|判断|设计|搭建|配置|接入|完成|把)', items[0]):
                keep = 0
                for x in items:
                    if re.match(r'^(能|会|掌握|理解|了解|知道|识别|区分|用|说出|判断|设计|搭建|配置|接入|完成|把)', x): keep += 1
                    else: break
                if 0 < keep < len(items):
                    i -= (len(items) - keep); items = items[:keep]
            blocks.append({'t':'objectives','items':items}); continue
        m = re.match(r'^(\d+\.\d+)\s*(.*)$', s)
        if m and len(m.group(2)) < 40:
            num, rest = m.group(1), m.group(2).strip()
            if not rest and i+1 < n and lines[i+1].strip():
                rest = lines[i+1].strip(); i += 1
            blocks.append({'t':'h2','num':num,'text':rest}); in_summary = '本章小结' in rest; i += 1; continue
        if '\t' in line:
            rows = []
            while i < n and '\t' in lines[i]:
                rows.append([c.strip() for c in lines[i].split('\t')]); i += 1
            blocks.append({'t':'table','rows':rows}); continue
        if s.startswith('|'):
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-{2,}:?', c) for c in cells if c):
                    rows.append(cells)
                i += 1
            if rows: blocks.append({'t':'table','rows':rows})
            continue
        mh = re.match(r'^(#{2,6})\s+(\S.*)$', s)
        if mh and '\t' not in s:
            lvl = 3 if len(mh.group(1)) == 2 else 4
            blocks.append({'t':'h%d' % lvl, 'text':mh.group(2).strip()}); i += 1; continue
        if s == '{':
            j = i; depth = 0; body = []
            while j < n:
                body.append(lines[j]); depth += lines[j].count('{') + lines[j].count('[') - lines[j].count('}') - lines[j].count(']'); j += 1
                if depth <= 0 and j > i: break
            blocks.append({'t':'code','text':'\n'.join(body)}); i = j; continue
        cm = re.match(r'^(⚠️|💡|📝|✅|❌|❗️|🔴|📌)\s*', s)
        if cm:
            blocks.append({'t':'callout','kind':'warn' if cm.group(1)=='⚠️' else 'tip','text':s[cm.end():]}); i += 1; continue
        fg = is_fig_head(lines, i)
        if fg:
            f = FIG.get(norm(fg[0]))
            if f:
                blocks.append({'t':'figure','caption':fg[1],'title':fg[0],'file':f}); i += 2; continue
        if re.match(r'^(' + '|'.join(H3LAB) + r')[：:]', s) and len(s) <= 40:
            blocks.append({'t':'h3','text':s}); i += 1; continue
        if re.match(r'^(陷阱[一二三四五]|模式[一二三四五]|场景\s?[A-Za-z一二三四五]|第[一二三四五]步)[：:]', s) and len(s) <= 40:
            blocks.append({'t':'h3','text':s}); i += 1; continue
        if re.match(r'^Q\d+[：:]', s):
            blocks.append({'t':'h3','cls':'q','text':s}); i += 1; continue
        if LIST_RE.match(s):
            items = []; base_indent = len(line) - len(line.lstrip())
            while i < n and lines[i].strip():
                cur = lines[i]; cs = cur.strip(); ind = len(cur) - len(cur.lstrip()); mm = LIST_RE.match(cs)
                if ind > base_indent and mm:
                    sub = []
                    while i < n and lines[i].strip() and (len(lines[i]) - len(lines[i].lstrip())) > base_indent:
                        ss = lines[i].strip(); m2 = LIST_RE.match(ss)
                        sub.append(ss[m2.end():] if m2 else ss); i += 1
                    if items: items[-1]['sub'] = sub
                    else: items.append({'text':'','sub':sub})
                    continue
                if mm and ind <= base_indent:
                    items.append({'text':cs[mm.end():]}); i += 1; continue
                break
            blocks.append({'t':'list','items':items}); continue
        if in_summary:
            items = []
            while i < n and lines[i].strip():
                items.append(lines[i].strip()); i += 1
            blocks.append({'t':'list','cls':'summary','items':[{'text':x} for x in items]}); continue
        if len(s) <= 24 and not ends_sentence(s) and not re.search(r'[：:]', s) and i+2 < n:
            pairs = []; k = i
            while k+1 < n:
                a = lines[k].strip(); b = lines[k+1].strip()
                if not a or not b: break
                if len(a) > 24 or ends_sentence(a) or re.search(r'[：:]|\t', a): break
                if not ends_sentence(b) or len(b) < 12 or '\t' in lines[k+1]: break
                if re.match(r'^\d+\.\d+', a) or re.match(r'^\d+\.\d+', b): break
                pairs.append({'term':a,'desc':b}); k += 2
                while k < n and not lines[k].strip(): k += 1
            if len(pairs) >= 2:
                blocks.append({'t':'defs','items':pairs}); i = k; continue
        if TERM_RE.match(s) and len(s) <= 60:
            run = 0; k = i
            while k < n and lines[k].strip() and TERM_RE.match(lines[k].strip()) and len(lines[k].strip()) <= 60 and (k + 1) not in fenced and not lines[k].strip().startswith(('|','#')) and '\t' not in lines[k]:
                if is_fig_head(lines, k) and k > i: break
                run += 1; k += 1
            if run >= 2:
                items = []
                while i < n and lines[i].strip() and TERM_RE.match(lines[i].strip()) and len(lines[i].strip()) <= 60 and (i + 1) not in fenced and not lines[i].strip().startswith(('|','#')) and '\t' not in lines[i]:
                    if is_fig_head(lines, i) and items: break
                    items.append({'text':lines[i].strip()}); i += 1
                blocks.append({'t':'list','cls':'term','items':items}); continue
        def run_ok(k):
            if (k + 1) in fenced: return False
            if lines[k].strip().startswith(('|','#')): return False
            t = lines[k].strip()
            if not t or '\t' in lines[k]: return False
            if is_fig_head(lines, k): return False
            if ends_sentence(t) or len(t) > 60: return False
            return True
        if run_ok(i):
            run = 0; k = i
            while k < n and run_ok(k): run += 1; k += 1
            prev = lines[i-1].strip() if i > 0 else ''
            if run >= 3 or (run >= 2 and prev.endswith(('：',':'))):
                items = []
                while i < n and run_ok(i):
                    items.append({'text':lines[i].strip()}); i += 1
                blocks.append({'t':'list','items':items}); continue
        if len(s) <= 34 and not ends_sentence(s) and i+1 < n and lines[i+1].strip():
            prev_blank = (i == 0) or (lines[i-1].strip() == '')
            if prev_blank or re.match(r'^(' + '|'.join(H3LAB) + r')', s):
                blocks.append({'t':'h3','text':s}); i += 1; continue
        blocks.append({'t':'p','text':s}); i += 1
    return blocks

all_blocks = {}
for f in sorted(x for x in os.listdir(D) if x.endswith('.txt')):
    txt = open(os.path.join(D,f), encoding='utf-8').read().replace('\r\n','\n')
    all_blocks[f] = classify(txt.split('\n'), f)
json.dump(all_blocks, open(os.path.join(D,'_raw','blocks.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
for f, bl in all_blocks.items():
    types = {}
    for b in bl: types[b['t']] = types.get(b['t'],0)+1
    print(f, types)
