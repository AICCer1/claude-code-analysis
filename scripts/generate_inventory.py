from pathlib import Path
import re
root = Path('/root/.openclaw/workspace/claude-code-sourcemap/restored-src/src')
out = Path('/root/.openclaw/workspace/claude-code-analysis/docs/generated')
out.mkdir(parents=True, exist_ok=True)

# 1) top-level directory counts
lines = ['# 目录文件计数（自动生成）', '', '| 目录 | 文件数 | 说明建议 |', '|---|---:|---|']
notes = {
'assistant':'Assistant/KAIROS 相关入口与会话辅助',
'bootstrap':'全局 bootstrap / 进程级状态',
'bridge':'桥接与远程控制能力',
'buddy':'伴侣/观察者 UI',
'cli':'CLI handler/命令辅助',
'commands':'slash/本地命令系统',
'components':'Ink/React 组件层',
'constants':'常量定义',
'context':'React Context/上下文',
'coordinator':'协调器/多代理模式',
'entrypoints':'SDK/入口类型与初始化',
'hooks':'React hooks/UI hooks',
'ink':'终端 UI 框架适配',
'keybindings':'按键绑定',
'memdir':'memory/CLAUDE.md 读取机制',
'migrations':'配置迁移',
'moreright':'小型附加模块',
'native-ts':'原生扩展包装',
'outputStyles':'输出样式',
'plugins':'插件引导',
'query':'查询主循环辅助模块',
'remote':'远程会话/传送',
'schemas':'共享 schema',
'screens':'UI screen',
'server':'本地服务/直连',
'services':'服务层（API/MCP/LSP/analytics 等）',
'skills':'技能系统',
'state':'应用状态容器',
'tasks':'任务系统',
'tools':'工具系统',
'types':'共享类型',
'upstreamproxy':'上游代理',
'utils':'最大公共工具箱',
'vim':'Vim 模式',
'voice':'语音模式',
}
for p in sorted([x for x in root.iterdir() if x.is_dir()]):
    count = sum(1 for f in p.rglob('*') if f.is_file())
    lines.append(f'| `{p.name}` | {count} | {notes.get(p.name, "-")} |')
(out / 'directory-counts.md').write_text('\n'.join(lines))

# 2) key files and exported symbols
candidate_files = [
    root / 'main.tsx',
    root / 'query.ts',
    root / 'QueryEngine.ts',
    root / 'commands.ts',
    root / 'tools.ts',
    root / 'Tool.ts',
    root / 'state' / 'AppStateStore.ts',
    root / 'utils' / 'hooks.ts',
    root / 'utils' / 'hooks' / 'hooksConfigManager.ts',
    root / 'services' / 'tools' / 'toolOrchestration.ts',
    root / 'services' / 'tools' / 'StreamingToolExecutor.ts',
    root / 'services' / 'tools' / 'toolHooks.ts',
    root / 'services' / 'mcp' / 'client.ts',
    root / 'skills' / 'loadSkillsDir.ts',
    root / 'tools' / 'AgentTool' / 'AgentTool.tsx',
    root / 'tools' / 'AgentTool' / 'agentToolUtils.ts',
    root / 'query' / 'stopHooks.ts',
]
pat = re.compile(r'^(export\s+)?(async\s+)?(function|class)\s+([A-Za-z0-9_]+)|^(export\s+)?const\s+([A-Za-z0-9_]+)\s*=')
lines = ['# 关键文件导出/符号索引（自动生成）', '']
for f in candidate_files:
    if not f.exists():
        continue
    rel = f.relative_to(root)
    lines.append(f'## `{rel}`')
    lines.append('')
    lines.append('| 行号 | 符号 |')
    lines.append('|---:|---|')
    found = 0
    for i, line in enumerate(f.read_text(errors='ignore').splitlines(), 1):
        m = pat.match(line.strip())
        if m:
            name = m.group(4) or m.group(6)
            lines.append(f'| {i} | `{name}` |')
            found += 1
    if found == 0:
        lines.append('| - | *(无简单匹配结果)* |')
    lines.append('')
(out / 'key-file-symbols.md').write_text('\n'.join(lines))

# 3) root file index
lines = ['# 根层关键文件（自动生成）', '', '| 文件 | 作用猜测 |', '|---|---|']
for f in sorted(root.glob('*')):
    if f.is_file():
        note = {
            'main.tsx':'CLI 主入口与启动编排',
            'query.ts':'单轮/多轮 query 主循环',
            'QueryEngine.ts':'SDK/无 UI 会话引擎',
            'commands.ts':'命令注册总表',
            'tools.ts':'工具注册与合并工厂',
            'Tool.ts':'工具抽象接口与 buildTool',
            'Task.ts':'任务抽象',
            'tasks.ts':'任务入口/导出',
            'replLauncher.tsx':'REPL 启动',
            'interactiveHelpers.tsx':'交互模式辅助',
        }.get(f.name, '-')
        lines.append(f'| `{f.name}` | {note} |')
(out / 'root-files.md').write_text('\n'.join(lines))
