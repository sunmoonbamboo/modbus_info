"""简单的HTTP文件服务器，用于为MinerU官方API提供PDF文件访问"""

import http.server
import socketserver
import os
from pathlib import Path
import argparse


class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """支持CORS的HTTP请求处理器"""
    
    def end_headers(self):
        # 添加CORS头，允许跨域访问
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()


def start_server(directory: str = "data/src", port: int = 8080, host: str = "0.0.0.0"):
    """
    启动HTTP文件服务器
    
    Args:
        directory: 要共享的目录
        port: 端口号
        host: 主机地址
    """
    # 切换到指定目录
    os.chdir(directory)
    
    # 创建服务器
    with socketserver.TCPServer((host, port), CORSHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("HTTP文件服务器已启动")
        print("=" * 60)
        print(f"目录: {Path(directory).absolute()}")
        print(f"地址: http://{host}:{port}")
        print()
        print("可用的PDF文件:")
        pdf_files = list(Path(".").glob("*.pdf"))
        if pdf_files:
            for pdf_file in pdf_files:
                print(f"  - {pdf_file.name}")
                print(f"    URL: http://{host}:{port}/{pdf_file.name}")
        else:
            print("  (未找到PDF文件)")
        print()
        print("提示:")
        print("1. 将此URL配置到Gradio界面的'文件服务器URL'中")
        print(f"   例如: http://{host}:{port}")
        print()
        print("2. 如果需要从外网访问，请确保:")
        print("   - 防火墙已开放端口")
        print("   - 使用公网IP或域名替换localhost")
        print()
        print("按 Ctrl+C 停止服务器")
        print("=" * 60)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="启动HTTP文件服务器")
    parser.add_argument(
        "--directory", "-d",
        default="data/src",
        help="要共享的目录（默认: data/src）"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8080,
        help="端口号（默认: 8080）"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="主机地址（默认: 0.0.0.0，监听所有网卡）"
    )
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    directory = Path(args.directory)
    if not directory.exists():
        print(f"错误: 目录不存在: {directory}")
        print(f"正在创建目录...")
        directory.mkdir(parents=True, exist_ok=True)
    
    start_server(
        directory=str(directory),
        port=args.port,
        host=args.host
    )

