"""Setup Case 003: source files + route_decision.json"""
import sys
sys.path.insert(0, '.')
from packages.common import get_project_source_dir, get_project_runtime_dir, get_knowledge_root_dir
import os, json

project_id = 'uxb-qc-003-permission-search-in-page'
repo_root = os.path.dirname(str(get_knowledge_root_dir()))
kroot = str(get_knowledge_root_dir())

# Write source files
src_dir = str(get_project_source_dir(project_id))
inp = os.path.join(repo_root, 'uxb_mainline_quality_test_pack', 'inputs', '功能权限设置支持筛选已勾选权限_需求文档.md')
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

# Case 003: Local UX enhancement - MINIMAL permission knowledge, focus on UX
# The key test: does AI avoid over-consuming permission knowledge?
biz_refs = select_by_prefix(perm_files, ['00_', '10_'])  # Only domain overview + capability map

guide_refs = []
for f in guide_files:
    basename = os.path.basename(f)
    if basename.startswith('可用性') or basename.startswith('认知') or basename.startswith('信息架构'):
        guide_refs.append(f)
for f in guide_files:
    if '反馈与报错' in f and ('00_' in os.path.basename(f) or '02_' in os.path.basename(f)):
        guide_refs.append(f)

reasons = []
for ref in biz_refs:
    basename = os.path.basename(ref)
    if '00_' in basename:
        r = '仅确认功能权限设置页面在权限体系中的位置——不展开权限规则、审批、治理模式'
    else:
        r = '仅确认功能权限设置页面的能力地图位置——不展开权限配置流程'
    reasons.append({'ref': ref, 'reason': r})

for ref in guide_refs:
    basename = os.path.basename(ref)
    if '可用性' in basename:
        r = '指导页面内查找（Ctrl+F体验）的可用性设计——这是本需求的核心：查找定位而非筛选'
    elif '认知' in basename:
        r = '控制查找功能的认知负担——区分"查找"与"筛选"，用户需要明确知道查找不改变数据范围'
    elif '信息架构' in basename:
        r = '指导查找入口和命中结果的信息组织——查找输入框位置、高亮标记方式、命中计数展示'
    elif '反馈' in ref:
        r = '指导无命中提示、命中计数、清空恢复等状态反馈文案'
    else:
        r = '支撑查找定位的体验设计'
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
        'reason': '本需求是在功能权限设置页面（1100+节点，约35屏）增加页面内查找定位能力。本质是页面内交互增强（类似Ctrl+F），不改变权限规则、不改变数据范围、不改变勾选状态。不应过度消费权限治理知识——只需确认功能权限设置页在权限体系中的位置。重点在可用性设计：查找入口、焦点跳转、折叠节点展开、编辑状态保护、大量命中性能。'
    },
    'complexity_judgment': {
        'business_change': 'shallow',
        'business_change_reason': '底层权限规则无变化，仅页面内增加查找定位交互。不涉及权限来源、审批、状态、治理模式等。',
        'experience_pressure': 'low',
        'experience_pressure_reason': '交互模式接近Ctrl+F，用户已有心智模型。需要特别处理的场景：折叠节点内命中（自动展开）、大量命中性能（1100+节点）、编辑状态保护（查找不触发保存）。',
        'uncertainties': [
            {'item': '查看模式和编辑模式是否都支持查找', 'type': 'non_blocking', 'reason': '可在方案中建议都支持'},
            {'item': '是否适用于所有授权对象还是仅限功能权限页面', 'type': 'non_blocking', 'reason': '初期可只支持功能权限设置页'},
            {'item': '查找输入框是常驻展示还是快捷键/按钮呼出', 'type': 'non_blocking', 'reason': '可在方案中建议常驻展示'}
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
            '查找≠筛选——这是本用例最核心的测试点。查找不改变数据范围，不改变勾选状态',
            '本次是局部体验优化，business_note足够——不需要展开完整业务蓝图',
            '重点处理：折叠节点内命中自动展开、编辑状态保护、大量命中性能和用户提示'
        ]
    }
}

runtime = str(get_project_runtime_dir(project_id))
os.makedirs(runtime, exist_ok=True)
path = os.path.join(runtime, 'uxb_route_decision.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(decision, f, ensure_ascii=False, indent=2)

print(f'Done: {len(biz_refs)} biz + {len(guide_refs)} guide + {len(reasons)} reasons')
for r in biz_refs:
    print(f'  BIZ: {os.path.basename(r)}')
for r in guide_refs:
    print(f'  GUIDE: {os.path.basename(r)}')
