"""Setup Case 006: 刁钻版页面内查找 - source files + route_decision.json"""
import sys
sys.path.insert(0, '.')
from packages.common import get_project_source_dir, get_project_runtime_dir, get_knowledge_root_dir
import os, json

project_id = 'uxb-qc-006-permission-find-tricky'
repo_root = os.path.dirname(str(get_knowledge_root_dir()))
kroot = str(get_knowledge_root_dir())

src_dir = str(get_project_source_dir(project_id))
inp = os.path.join(repo_root, 'uxb_mainline_quality_test_pack', 'inputs', '需求文档_006_功能权限页面内查找.md')
open(os.path.join(src_dir, 'requirement.md'), 'w', encoding='utf-8').write(open(inp, encoding='utf-8').read())
open(os.path.join(src_dir, 'background.md'), 'w', encoding='utf-8').write('# Background\n\n本测试仅使用 requirement.md 中的信息，不额外补充背景。\n')

def find_files(subpath):
    d = os.path.join(kroot, subpath)
    if not os.path.exists(d): return []
    result = []
    for root, dirs, files in os.walk(d):
        for f in files:
            if f.endswith('.md') and f != 'README.md':
                full = os.path.join(root, f)
                rel = os.path.relpath(full, repo_root).replace('\\', '/')
                result.append(rel)
    return sorted(result)

def select_by_prefix(files, prefixes):
    selected = []
    for f in files:
        basename = os.path.basename(f)
        for prefix in prefixes:
            if basename.startswith(prefix):
                selected.append(f)
                break
    return selected

perm_files = find_files('raw/业务/权限管理')
guide_files = find_files('raw/设计准则')

# Case 006: 刁钻混淆版 - ONLY 2 permission knowledge files
# The test: can AI resist consuming more permission knowledge than needed,
# even when the document says "搜索/筛选/页面内查找" and introduces "只看已勾选"?
biz_refs = select_by_prefix(perm_files, ['00_', '10_'])

guide_refs = []
for f in guide_files:
    basename = os.path.basename(f)
    if basename.startswith('可用性') or basename.startswith('认知') or basename.startswith('信息架构'):
        guide_refs.append(f)
for f in guide_files:
    if '反馈与报错' in f and '00_' in os.path.basename(f):
        guide_refs.append(f)

reasons = []
for ref in biz_refs:
    basename = os.path.basename(ref)
    if '00_' in basename:
        r = '仅确认功能权限设置页面在权限体系中的位置。需求文档中出现的"搜索/筛选/页面内查找"混淆语言和"只看已勾选"诉求——这些都不改变权限规则。不展开权限治理知识。'
    else:
        r = '仅确认功能权限设置页面的能力地图位置。不展开权限配置流程、审批、来源模型等。'
    reasons.append({'ref': ref, 'reason': r})

for ref in guide_refs:
    basename = os.path.basename(ref)
    if '可用性' in basename:
        r = '关键知识：指导页面内查找（Ctrl+F体验）的可用性设计。需求文档混淆了"查找"和"筛选"——可用性原则要求系统状态可见(U-01)和用户可控(U-03)，查找不应改变数据范围。'
    elif '认知' in basename:
        r = '关键知识：控制认知负担。需求文档中4种矛盾说法（A/B/C/D）会让用户困惑——需要认知原则来判断哪些诉求属于"查找"，哪些属于"筛选"。C-03减少认知负荷：查找=定位，筛选=改变范围。'
    elif '信息架构' in basename:
        r = '指导查找入口和命中结果的信息组织。IA-01信息气味：高亮让用户一眼看到"匹配了什么"。如果隐藏未命中项(说法C)，用户就看不到"还有什么没匹配"——信息气味丢失。'
    elif '反馈' in ref:
        r = '指导无命中提示和状态反馈。需求中"只看已勾选"需要额外规则——如果只看已勾选后取消勾选，该项是否立刻消失？这需要反馈原则来设计。'
    else:
        r = '支撑查找体验设计'
    reasons.append({'ref': ref, 'reason': r})

decision = {
    'schema_version': 'uxb_route_decision@3.0',
    'created_by': 'uxb_ai',
    'confirmed_by_user': True,
    'can_execute_mainline': True,
    'judgment': {
        'demand_type': 'local_ux_enhancement',
        'business_depth': 'fast',
        'experience_output': 'light_blueprint',
        'reason': '本需求的核心是功能权限设置页面的页面内查找定位（Ctrl+F体验）。但需求文档故意混淆了"查找""筛选""搜索"三个概念，且引入了"只看已勾选"的筛选诉求。关键判断：页面内查找（高亮+定位，不改变数据范围）属于本次范围；"只看已勾选"和"隐藏未命中项"本质是筛选——改变了数据展示范围——应拆出去作为独立需求。不能因为需求文档把三者都叫"搜索"就混在一起做。'
    },
    'complexity_judgment': {
        'business_change': 'shallow',
        'business_change_reason': '底层权限规则零变化。仅页面内增加查找定位交互。"只看已勾选"是筛选——如果本次要做，会改变数据展示范围，需要对筛选规则做额外定义。建议本次只做查找，筛选拆出去。',
        'experience_pressure': 'low',
        'experience_pressure_reason': '查找定位交互模式接近Ctrl+F，复杂度低。但如果把"只看已勾选"和"隐藏未命中项"都加进来——交互复杂度显著上升（需要处理两种模式的切换/组合/互斥/状态保持）。',
        'uncertainties': [
            {'item': '本次到底是页面内查找还是筛选？——需求文档故意混淆', 'type': 'blocking', 'reason': '决定本次功能范围和交互模式。建议：本次只做查找。筛选（只看已勾选+隐藏未命中项）拆出去。'},
            {'item': '"只看已勾选"是否属于本次范围？', 'type': 'blocking', 'reason': '"只看已勾选"改变数据展示范围——本质是筛选，不是查找。如果不拆出去，需要额外定义：未保存勾选是否算已勾选/取消后是否立刻消失/与关键词查找的优先级。'},
            {'item': '查找是否改变页面展示范围？——说法A vs 说法C', 'type': 'blocking', 'reason': '说法A(不改变范围)是正确的查找定位；说法C(隐藏未命中项)是筛选。不能两者都做但都叫"搜索"。'},
            {'item': '折叠节点命中后是否自动展开？清空关键词后是否恢复？', 'type': 'non_blocking', 'reason': '可在方案中给建议'}
        ]
    },
    'knowledge_selection': {
        'business_refs': biz_refs,
        'guideline_refs': guide_refs,
        'complexity_refs': [],
        'selection_reasons': reasons
    },
    'execution': {
        'required_outputs': ['facts.md', 'business_note.md', 'experience_blueprint.md', 'gap_list.md', 'check_report.md'],
        'notes': [
            '核心区分：查找≠筛选≠搜索。需求文档故意混用三个词。',
            '页面内查找：高亮+定位，不改变数据范围——本次做。',
            '"只看已勾选"：改变数据展示范围——本质是筛选，拆出去。',
            '"隐藏未命中项"：改变数据展示范围——本质是筛选，拆出去。',
            '如果业务方坚持要把筛选也做了——需要明确筛选与查找的交互优先级、状态保持、编辑保护规则。'
        ]
    }
}

runtime = str(get_project_runtime_dir(project_id))
os.makedirs(runtime, exist_ok=True)
path = os.path.join(runtime, 'uxb_route_decision.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(decision, f, ensure_ascii=False, indent=2)

print(f'Done: {len(biz_refs)} biz + {len(guide_refs)} guide + {len(reasons)} reasons')
