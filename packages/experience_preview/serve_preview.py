from __future__ import annotations

import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from packages.common import get_project_preview_dir
from packages.experience_preview.build_preview_model import build_preview_model
from packages.experience_preview.render_html import write_preview_site
from packages.experience_preview.write_preview_runtime import write_preview_runtime
from packages.provenance import append_command_if_provenance_exists


class PreviewHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def run_experience_preview(project_id: str, host: str = "127.0.0.1", port: int = 0, serve: bool = True) -> int:
    preview_dir = get_project_preview_dir(project_id)
    preview_dir.mkdir(parents=True, exist_ok=True)

    model = build_preview_model(project_id)
    write_preview_site(preview_dir, model)

    if not serve:
        write_preview_runtime(
            project_id=project_id,
            model=model,
            host=host,
            port=port,
            ready_state="built",
            preview_url="",
        )
        append_command_if_provenance_exists(project_id, "preview")
        print("蓝图预览已生成。")
        print(f"预览输出目录：{preview_dir}")
        return 0

    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(preview_dir))
    with PreviewHTTPServer((host, port), handler) as httpd:
        actual_host, actual_port = httpd.server_address
        preview_url = f"http://{actual_host}:{actual_port}/"
        write_preview_runtime(
            project_id=project_id,
            model=model,
            host=str(actual_host),
            port=int(actual_port),
            ready_state="ready",
            preview_url=preview_url,
        )
        append_command_if_provenance_exists(project_id, "preview")
        print("蓝图预览已生成。", flush=True)
        print(f"本地预览地址：{preview_url}", flush=True)
        print("可在浏览器中直接打开查看 Business / Experience / 承接对照。", flush=True)
        httpd.serve_forever()
    return 0
