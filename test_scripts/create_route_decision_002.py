"""Create route_decision.json for Case 002: Permission Query."""
import sys
sys.path.insert(0, '.')
from packages.common import get_project_runtime_dir, get_knowledge_root_dir
import os, json

project_id = 'uxb-qc-002-permission-query'
repo_root = os.path.dirname(str(get_knowledge_root_dir()))
kroot = str(get_knowledge_root_dir())

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

biz_refs = select_by_prefix(perm_files, ['00_', '01_', '04_', '10_', '12_', '14_'])

guide_refs = []
for f in guide_files:
    basename = os.path.basename(f)
    if basename.startswith('信息架构') or basename.startswith('可用性') or basename.startswith('认知'):
        guide_refs.append(f)
for f in guide_files:
    if '反馈与报错' in f and '00_' in os.path.basename(f):
        guide_refs.append(f)

reasons = []
for ref in biz_refs:
    basename = os.path.basename(ref)
    prefix = basename[:3]
    if prefix == '00_':
        r = '理解权限管理整体定位——确认查询能力在权限体系中的位置，而非授权配置'
    elif prefix == '01_':
        r = '确认查询能力的边界：查询是只读操作，不改变权限数据，查询≠配置'
    elif prefix == '04_':
        r = '理解人-角色-权限的实体关系——这是设计多维度查询视角（按人查/按角色查/按权限查）的基础'
    elif prefix == '10_':
        r = '确认权限查询在能力地图中的位置——应该放在查询与排障域，而非授权配置域'
    elif prefix == '12_':
        r = '关键知识：理解查询与配置路径的关系——确保查询结果不变成配置入口，跳转需受控'
    elif prefix == '14_':
        r = '确认不同角色（权限管理员/超管/审计人员）使用查询能力的边界'
    else:
        r = '支撑查询能力的业务推理'
    reasons.append({'ref': ref, 'reason': r})

for ref in guide_refs:
    basename = os.path.basename(ref)
    if '信息架构' in basename:
        r = '指导多维度查询视角的信息组织和切换方式——影响experience查询入口和结果展示'
    elif '可用性' in basename:
        r = '指导查询条件输入、结果浏览的可用性设计——影响experience查询交互'
    elif '认知' in basename:
        r = '控制查询页面的认知负担——区分查询与配置，避免用户混淆'
    elif '反馈' in ref:
        r = '指导无结果、查询超时、权限不足等状态反馈——影响experience异常流程'
    else:
        r = '支撑查询体验设计'
    reasons.append({'ref': ref, 'reason': r})

decision = {
    'schema_version': 'uxb_route_decision@3.0',
    'created_by': 'uxb_ai',
    'confirmed_by_user': True,
    'can_execute_mainline': True,
    'judgment': {
        'demand_type': 'strategy_inquiry',
        'business_depth': 'standard',
        'experience_output': 'standard_blueprint',
        'reason': '本需求是补齐统一权限查询视角的策略类需求，不是新增授权配置能力。核心是从多维度查看权限归属关系，服务于核对、审计、排障场景。需求完整度低——未给出完整字段、页面结构、规则细节。不应按复杂新业务全量展开，适合先做精简业务判断（business_blueprint_lite），讲清查询维度设计和查询≠配置的核心边界。'
    },
    'complexity_judgment': {
        'business_change': 'moderate',
        'business_change_reason': '查询能力不改变权限规则，但需要明确查询维度（按人/按角色/按权限项）和查询≠配置的边界——参考12_查询与配置路径的知识',
        'experience_pressure': 'moderate',
        'experience_pressure_reason': '需要设计多维度查询视角切换、查询结果的信息层级、无结果/权限不足等状态处理——避免写成标准筛选+表格+详情抽屉的套路',
        'uncertainties': [
            {'item': '查询维度具体包含哪些（按人/按角色/按权限项）及是否覆盖数据权限', 'type': 'blocking', 'reason': '决定查询入口和页面结构'},
            {'item': '查询结果是否允许跳转到配置页及跳转后的权限控制', 'type': 'blocking', 'reason': '影响查询与配置的边界设计——这是本需求的核心区分点'},
            {'item': '不同角色（权限管理员/超管/审计人员）的查询范围是否不同', 'type': 'non_blocking', 'reason': '可在方案中建议，不阻断整体方向'}
        ]
    },
    'knowledge_selection': {
        'business_refs': biz_refs,
        'guideline_refs': guide_refs,
        'complexity_refs': [],
        'selection_reasons': reasons
    },
    'execution': {
        'required_outputs': ['facts.md', 'business_blueprint_lite.md', 'experience_blueprint.md', 'gap_list.md', 'check_report.md'],
        'notes': [
            '查询≠配置——这是本需求最核心的区分，贯穿所有产物',
            '三种查询视角（按人/按角色/按权限项）的信息展示结构可能不同——不是同一套列表模板',
            '查询是只读操作，不改变任何权限数据'
        ]
    }
}

runtime = str(get_project_runtime_dir(project_id))
os.makedirs(runtime, exist_ok=True)
path = os.path.join(runtime, 'uxb_route_decision.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(decision, f, ensure_ascii=False, indent=2)

print(f'Done: {len(biz_refs)} biz + {len(guide_refs)} guide + {len(reasons)} reasons')
