"""Setup Case 004: source files + route_decision.json"""
import sys
sys.path.insert(0, '.')
from packages.common import get_project_source_dir, get_project_runtime_dir, get_knowledge_root_dir
import os, json

project_id = 'uxb-qc-004-sub-admin-copy'
repo_root = os.path.dirname(str(get_knowledge_root_dir()))
kroot = str(get_knowledge_root_dir())

src_dir = str(get_project_source_dir(project_id))
inp = os.path.join(repo_root, 'uxb_mainline_quality_test_pack', 'inputs', '子管理员支持复制_需求文档.md')
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

# Case 004: Rule-based enhancement, medium-high completeness
# Select knowledge for: sub-admin mode, overlay logic, dual admin audit, validation rules
biz_refs = select_by_prefix(perm_files, ['00_', '01_', '02_', '03_', '04_', '10_', '14_', '24_', '30_', '31_'])

guide_refs = []
for f in guide_files:
    basename = os.path.basename(f)
    if basename.startswith('可用性') or basename.startswith('流程模式'):
        guide_refs.append(f)
for f in guide_files:
    if '反馈与报错' in f and '00_' in os.path.basename(f):
        guide_refs.append(f)

reasons = []
reason_map = {
    '00_': '理解子管理员模式在权限体系中的定位——确认复制能力在子管理员管理中的位置',
    '01_': '确认复制能力的边界：仅在子管理员模式内，不扩展到其他权限配置——对应需求约束第1条',
    '02_': '统一"子管理员""可授权组织""可授权功能""叠加"等术语——确保校验文案和操作记录文案术语一致',
    '03_': '比对复制能力与现有子管理员业务规则的兼容性——确保叠加不覆盖逻辑与现有规则不冲突',
    '04_': '理解子管理员-可授权组织-可授权功能-用户的实体关系——支撑复制来源和复制对象的对象模型',
    '10_': '确认复制能力在能力地图中的位置——子管理员管理域的批量操作增强',
    '14_': '确认权限管理员和子管理员的角色边界——复制操作需要权限管理员/超管权限',
    '24_': '确认复制后权限的生效状态和双管理员互审的审批状态流转——影响business规则6和互审GAP处理',
    '30_': '判断复制能力与双管理员互审模式的互动关系——复制完成时需要生成审批，这是本需求最关键的GAP来源',
    '31_': '参考翻牌叠加等已有模式设计复制逻辑——翻牌叠加是已有的叠加不覆盖先例，直接用于推理叠加规则',
}
for ref in biz_refs:
    basename = os.path.basename(ref)
    prefix = basename[:3]
    r = reason_map.get(prefix, '支撑业务推理')
    reasons.append({'ref': ref, 'reason': r})

for ref in guide_refs:
    basename = os.path.basename(ref)
    if '可用性' in basename:
        r = '指导复制弹窗的可用性设计——选择器交互、默认全选、至少选一项的校验提示'
    elif '流程模式' in basename:
        r = '指导复制弹窗的分步结构（复制信息→复制对象）——BFM-02分步引导适用于校验顺序强制的场景'
    elif '反馈' in ref:
        r = '指导校验顺序的错误提示文案——按顺序阻断、展示具体失败用户名单'
    else:
        r = '支撑复制弹窗体验设计'
    reasons.append({'ref': ref, 'reason': r})

decision = {
    'schema_version': 'uxb_route_decision@3.0',
    'created_by': 'uxb_ai',
    'confirmed_by_user': True,
    'can_execute_mainline': True,
    'judgment': {
        'demand_type': 'rule_based_enhancement',
        'business_depth': 'full',
        'experience_output': 'full_blueprint',
        'reason': '本需求是在子管理员模式中新增复制能力，需求信息相对完整——入口、弹窗结构、复制内容、复制对象、校验顺序（4步）、复制规则（叠加不覆盖+普通用户变子管理员+200人限制）、操作记录文案、双管理员互审触发均有明确描述。核心工作是严格承接这些明确规则，逐条转译到business和experience，同时对双管理员互审审批规则不完整的GAP保持诚实标记，不脑补。'
    },
    'complexity_judgment': {
        'business_change': 'moderate',
        'business_change_reason': '复制不改变底层权限模型，但影响子管理员配置流程（操作列新增入口）、批量授权效率（1→N）、操作记录格式（两种记录类型）、双管理员互审审批（时机待确认）',
        'experience_pressure': 'moderate',
        'experience_pressure_reason': '涉及：复制弹窗的完整结构、选择员工弹窗（复用添加子管理员弹窗样式）、4步校验顺序和阻断文案、200人限制提示、叠加不覆盖的视觉表达、双管理员互审审批提示',
        'uncertainties': [
            {'item': '双管理员互审模式下审批规则不完整（审批时机/生效方式/拒绝回滚/分别审批）', 'type': 'blocking', 'reason': '影响审批流程设计和体验——不能脑补'},
            {'item': '加入状态口径统一（已启用/已加入）', 'type': 'non_blocking', 'reason': '仅影响选择员工弹窗的过滤文案'},
            {'item': '部分用户校验失败时的处理策略（全部阻断/跳过失败继续）', 'type': 'blocking', 'reason': '影响批量复制失败的用户体验'},
            {'item': '重复组织/功能是否自动去重', 'type': 'non_blocking', 'reason': '影响叠加逻辑的细节'},
            {'item': '操作记录中多对象是否折叠展示', 'type': 'non_blocking', 'reason': '影响操作记录展示'}
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
            '严格承接需求中的明确规则：叠加不覆盖、普通用户变子管理员、200人限制、校验顺序(4步)',
            '双管理员互审审批规则GAP不可脑补——必须在business和experience中标记为待确认',
            '加入状态口径冲突（已启用/已加入）需在facts中暴露',
            '复制信息至少选一项、复制对象至少选一名——两个必选校验'
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
