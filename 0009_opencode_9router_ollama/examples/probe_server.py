#!/usr/bin/env python3
"""Serve deterministic OpenAI-compatible responses for the routing exercise."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROUTES = {
    "/router/v1": ("pathbit-code", "PATHBIT_ROUTER_OK"),
    "/local/v1": ("qwen2.5-coder:7b", "PATHBIT_LOCAL_OK"),
}


class ProbeHandler(BaseHTTPRequestHandler):
    def route(self, suffix):
        return next(((model, result) for path, (model, result) in ROUTES.items()
                     if self.path == path + suffix), None)

    def reply_json(self, body, status=200):
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        expected = self.route("/models")
        if expected is None:
            self.reply_json({"error": "Unknown catalogue"}, 404)
            return
        self.reply_json({"object": "list", "data": [{"id": expected[0], "object": "model"}]})

    def do_POST(self):
        expected = self.route("/chat/completions")
        if expected is None:
            self.reply_json({"error": "Unknown route"}, 404)
            return
        try:
            request = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
        except (ValueError, TypeError):
            self.reply_json({"error": "Invalid JSON body"}, 400)
            return
        model, message = expected
        if not isinstance(request, dict) or request.get("model") != model:
            self.reply_json({"error": {"message": f"Expected model {model}"}}, 400)
            return
        base = {"id": "chatcmpl-pathbit-probe", "created": 1795770000, "model": model}
        if not request.get("stream"):
            self.reply_json({**base, "object": "chat.completion", "choices": [{
                "index": 0, "message": {"role": "assistant", "content": message}, "finish_reason": "stop",
            }], "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}})
            return
        events = [
            {"index": 0, "delta": {"role": "assistant", "content": message}, "finish_reason": None},
            {"index": 0, "delta": {}, "finish_reason": "stop"},
        ]
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        for event in events:
            chunk = {**base, "object": "chat.completion.chunk", "choices": [event]}
            self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode("utf-8"))
        self.wfile.write(b"data: [DONE]\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=19809)
    with ThreadingHTTPServer(("127.0.0.1", parser.parse_args().port), ProbeHandler) as server:
        print(f"Probe on 127.0.0.1:{server.server_port}", flush=True)
        server.serve_forever()
