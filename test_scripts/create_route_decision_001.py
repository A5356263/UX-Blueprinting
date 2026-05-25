"""Create route_decision.json for Case 001."""
import sys
sys.path.insert(0, '.')
from packages.common import get_project_runtime_dir, get_knowledge_root_dir
import os, json

project_id = 'uxb-qc-001-employee-self-service-permission'
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
approval_files = find_files('raw/业务/审批管理')
guide_files = find_files('raw/设计准则')

# Business refs for Case 001
biz_prefixes = ['00_', '01_', '02_', '03_', '04_', '14_', '21_', '24_', '30_']
biz_refs = select_by_prefix(perm_files, biz_prefixes)
biz_refs.extend(approval_files)

# Guideline refs
guide_refs = []
for f in guide_files:
    basename = os.path.basename(f)
    if basename.startswith('可用性') or basename.startswith('流程模式') or basename.startswith('信息架构') or basename.startswith('认知'):
        guide_refs.append(f)
for f in guide_files:
    if '反馈与报错' in f and '00_' in os.path.basename(f):
        guide_refs.append(f)

# Build reasons
reasons = []
for ref in biz_refs:
    basename = os.path.basename(ref)
    prefix = basename[:3] if basename[0].isdigit() else ''
    r = ''
    if prefix == '00_':
        r = '理解权限管理的整体定位与边界，确认自助申请权限在现有权限体系中的位置——影响business"能力形态"判断'
    elif prefix == '01_':
        r = '判断自助申请权限的能力边界，确认与现有权限治理模式的互斥关系——影响business"模式互斥规则"和experience中的冲突阻断提示'
    elif prefix == '02_':
        r = '统一权限来源、审批状态、授权生效等关键术语定义——确保facts/business/experience三阶段概念一致'
    elif prefix == '03_':
        r = '比对现有权限业务规则，判断自助申请引入后需要新增或修改哪些规则——影响business全部规则和边界设计'
    elif prefix == '04_':
        r = '理解员工-权限-角色-审批的实体关系——直接影响business推荐方案中的对象模型设计'
    elif prefix == '14_':
        r = '定义员工、审批人、超级管理员、权限管理员在自助申请流程中的职责边界——影响business"角色边界规则"和experience中三端角色路径'
    elif prefix == '21_':
        r = '确认"自助申请"能否作为新的权限来源类型——这是本次需求最核心的业务判断，直接影响business"能力形态"和"权限来源规则"'
    elif prefix == '24_':
        r = '定义申请中/审批中/已生效/已拒绝/已关闭等状态及其转换关系——影响business状态流转设计和experience状态反馈文案'
    elif prefix == '30_':
        r = '判断自助申请模式与现有治理模式的互斥/共存规则——影响business"模式互斥规则"和experience"模式互斥冲突"阻断流程'
    else:
        r = '理解审批流程的设计规则——影响business"审批端"和experience"审批端流程"'
    reasons.append({'ref': ref, 'reason': r})

for ref in guide_refs:
    basename = os.path.basename(ref)
    if '可用性' in basename:
        r = '指导员工端申请入口和流程的可用性设计——影响experience员工端流程设计'
    elif '流程模式' in basename:
        r = '指导管理端多步骤配置流程和员工端申请流程的模式选择——影响experience管理端配置和员工申请流程'
    elif '信息架构' in basename:
        r = '指导员工端权限查看、申请记录的信息组织方式——影响experience页面设计'
    elif '反馈' in ref:
        r = '指导申请提交、审批结果、异常状态等场景的用户反馈和文案设计——影响experience全部状态反馈文案'
    elif '认知' in basename:
        r = '指导首次使用自助申请的员工认知负担设计——影响experience中的引导和帮助提示'
    else:
        r = '支撑体验设计中的交互和反馈规则'
    reasons.append({'ref': ref, 'reason': r})

decision = {
    'schema_version': 'uxb_route_decision@3.0',
    'created_by': 'uxb_ai',
    'confirmed_by_user': True,
    'can_execute_mainline': True,
    'judgment': {
        'demand_type': 'complex_business_capability',
        'business_depth': 'full',
        'experience_output': 'full_blueprint',
        'reason': '本需求不是局部页面优化，而是新增一条"员工自助申请→审批→自动授权"的业务通道。涉及：权限来源模型（新增"自助申请"来源）、权限状态模型（新增申请中/审批中状态）、角色边界（员工获得主动发起权限变更的能力）、与已有权限治理模式的互斥关系。需求文档完整度低（15个不明确事项），需在business阶段区分阻断型和非阻断型不确定项。'
    },
    'complexity_judgment': {
        'business_change': 'deep',
        'business_change_reason': '引入新的权限来源路径，影响权限对象模型（来源字段）、权限状态模型（6种状态）、角色边界（4类角色）、治理模式（互斥检测）',
        'experience_pressure': 'high',
        'experience_pressure_reason': '涉及管理端（配置+关闭）、员工端（查看+申请+记录）、审批端（审批处理）三个端侧，需覆盖多步骤流程、状态反馈、8种异常场景、安全保护',
        'uncertainties': [
            {'item': '自助申请权限模式与现有权限治理模式是否互斥及互斥范围', 'type': 'blocking', 'reason': '互斥关系影响能力开关设计和用户提示文案'},
            {'item': '员工可申请角色、功能权限还是两者都支持', 'type': 'blocking', 'reason': '决定可申请范围的配置方式和申请表单结构'},
            {'item': '审批人不存在或审批流程异常时的兜底规则', 'type': 'blocking', 'reason': '影响审批异常处理设计和用户反馈'},
            {'item': '管理员关闭能力后已获权限是否保留', 'type': 'blocking', 'reason': '影响关闭逻辑和员工体验'},
            {'item': '管理员关闭能力时审批中申请如何处理', 'type': 'blocking', 'reason': '影响关闭流程和员工通知'},
            {'item': '审批通过后权限生效方式（实时/异步）', 'type': 'blocking', 'reason': '影响授权回写逻辑和员工端状态展示'},
            {'item': '敏感角色或权限是否需要自动排除', 'type': 'non_blocking', 'reason': '可在方案中建议默认排除'},
            {'item': '审批人默认是谁（组织负责人/管理员/自定义）', 'type': 'non_blocking', 'reason': '可在方案中给建议默认值'},
            {'item': '服务人员是否支持该能力', 'type': 'non_blocking', 'reason': '当前倾向不开放，可在business中明确'},
            {'item': '是否需要支持上传附件', 'type': 'non_blocking', 'reason': '可在方案中建议支持'},
            {'item': '审批中申请是否可以撤销', 'type': 'non_blocking', 'reason': '可在方案中建议支持'},
            {'item': '员工端入口位置', 'type': 'non_blocking', 'reason': '可在experience中给建议'},
            {'item': '是否给员工展示权限来源', 'type': 'non_blocking', 'reason': '可在experience中给建议'},
            {'item': '是否给管理员提供申请统计', 'type': 'non_blocking', 'reason': '可在business中建议'},
            {'item': '申请权限时是否可选择数据权限范围', 'type': 'non_blocking', 'reason': '初期可不支持，后续迭代'}
        ]
    },
    'knowledge_selection': {
        'business_refs': biz_refs,
        'guideline_refs': guide_refs,
        'complexity_refs': [],
        'selection_reasons': reasons
    },
    'execution': {
        'required_outputs': ['facts.md', 'business_blueprint.md', 'experience_blueprint.md', 'gap_list.md', 'check_report.md'],
        'notes': [
            '需求完整度低，需在facts中充分暴露15个GAP',
            'business需区分需求事实、知识依据、AI推导三个层次',
            'experience需承接business中的所有角色、规则、状态、异常和文案要求',
            '不确定事项不能脑补为确定方案——GAP必须标记'
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
