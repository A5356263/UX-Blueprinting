const escapeHtml = value => String(value)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')

const inline = value => escapeHtml(value)
  .replace(/`([^`]+)`/g, '<code>$1</code>')
  .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" rel="noreferrer noopener">$1</a>')

function renderTable(rows) {
  const cells = rows.map(row => row.trim().replace(/^\||\|$/g, '').split('|').map(cell => cell.trim()))
  if (cells.length < 2) return ''
  const head = cells[0].map(cell => '<th>' + inline(cell) + '</th>').join('')
  const body = cells.slice(2).map(row => '<tr>' + row.map(cell => '<td>' + inline(cell) + '</td>').join('') + '</tr>').join('')
  return '<table><thead><tr>' + head + '</tr></thead><tbody>' + body + '</tbody></table>'
}

export function renderPreview(markdown, title = '预览') {
  const lines = String(markdown ?? '').replace(/\r\n/g, '\n').split('\n')
  const out = []
  let code = null
  let list = null
  let table = []
  const flushList = () => {
    if (!list) return
    out.push('<' + list.tag + '>' + list.items.map(item => '<li>' + item + '</li>').join('') + '</' + list.tag + '>')
    list = null
  }
  const flushTable = () => {
    if (!table.length) return
    out.push(renderTable(table))
    table = []
  }
  const flush = () => { flushList(); flushTable() }
  for (const line of lines) {
    if (line.startsWith('```')) {
      flush()
      if (code === null) code = []
      else { out.push('<pre><code>' + escapeHtml(code.join('\n')) + '</code></pre>'); code = null }
      continue
    }
    if (code !== null) { code.push(line); continue }
    if (!line.trim()) { flush(); continue }
    const heading = line.match(/^(#{1,6})\s+(.*)$/)
    if (heading) {
      flush()
      const level = heading[1].length
      out.push('<h' + level + '>' + inline(heading[2]) + '</h' + level + '>')
      continue
    }
    if (/^>\s?/.test(line)) { flush(); out.push('<blockquote>' + inline(line.replace(/^>\s?/, '')) + '</blockquote>'); continue }
    if (/^\s*([-*_])\1{2,}\s*$/.test(line)) { flush(); out.push('<hr>'); continue }
    if (/^\|.*\|$/.test(line.trim())) { flushList(); table.push(line.trim()); continue }
    const unordered = line.match(/^\s*[-*]\s+(.*)$/)
    if (unordered) {
      flushTable()
      if (!list || list.tag !== 'ul') { flushList(); list = { tag: 'ul', items: [] } }
      list.items.push(inline(unordered[1]))
      continue
    }
    const ordered = line.match(/^\s*\d+[.)]\s+(.*)$/)
    if (ordered) {
      flushTable()
      if (!list || list.tag !== 'ol') { flushList(); list = { tag: 'ol', items: [] } }
      list.items.push(inline(ordered[1]))
      continue
    }
    flush()
    out.push('<p>' + inline(line) + '</p>')
  }
  flush()
  if (code !== null) out.push('<pre><code>' + escapeHtml(code.join('\n')) + '</code></pre>')
  const body = out.join('\n')
  return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1">' +
    '<title>' + escapeHtml(title) + '</title>' +
    '<style>' +
    'body{margin:0;padding:40px 24px;background:#f6f7f9;color:#1c2430;font:15px/1.7 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif}' +
    'main{max-width:860px;margin:0 auto;background:#fff;border:1px solid #e3e7ee;border-radius:14px;padding:36px 40px;box-shadow:0 6px 24px rgba(20,30,50,.06)}' +
    'h1{font-size:26px;margin:0 0 18px}h2{font-size:19px;margin:30px 0 10px;padding-top:6px}h3{font-size:16px;margin:22px 0 8px}' +
    'p{margin:10px 0}ul,ol{padding-left:22px}li{margin:4px 0}' +
    'code{background:#f0f2f6;border-radius:4px;padding:1px 5px;font-size:13px}' +
    'pre{background:#f0f2f6;border-radius:8px;padding:14px;overflow:auto}pre code{background:none;padding:0}' +
    'table{border-collapse:collapse;width:100%;margin:14px 0;font-size:14px}th,td{border:1px solid #e3e7ee;padding:8px 10px;text-align:left}th{background:#f6f7f9}' +
    'blockquote{margin:12px 0;padding:8px 14px;border-left:3px solid #9fb4d8;background:#f6f8fb;color:#44506a}' +
    'hr{border:none;border-top:1px solid #e3e7ee;margin:24px 0}' +
    '</style></head><body><main>' + body + '</main></body></html>'
}
