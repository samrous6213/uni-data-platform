#!/usr/bin/env python3
"""
Proxy simple pour contourner le CORS
Permet à l'interface HTML de parler à Elasticsearch
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import json
import re

ES_URL = "http://localhost:9200"

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Nettoyer l'URL
        path = self.path
        if path == '/':
            self.serve_index()
            return
        
        # Proxy vers Elasticsearch
        if path.startswith('/es/'):
            es_path = path[3:]  # Enlever '/es/'
            url = f"{ES_URL}{es_path}"
            
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req) as resp:
                    data = resp.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(data)
            except Exception as e:
                self.send_error(500, f"Erreur: {e}")
            return
        
        self.send_error(404)

    def do_POST(self):
        if self.path.startswith('/es/'):
            es_path = self.path[3:]
            url = f"{ES_URL}{es_path}"
            
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            try:
                req = urllib.request.Request(url, data=body, method='POST')
                req.add_header('Content-Type', 'application/json')
                with urllib.request.urlopen(req) as resp:
                    data = resp.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(data)
            except Exception as e:
                self.send_error(500, f"Erreur: {e}")
            return
        
        self.send_error(404)

    def serve_index(self):
        # Servir le fichier index.html
        try:
            with open('index.html', 'r') as f:
                content = f.read()
                # Remplacer les URLs Elasticsearch par le proxy
                content = content.replace('http://localhost:9200/university_data/_search', '/es/university_data/_search')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Erreur: {e}")

if __name__ == '__main__':
    port = 8080
    print(f"🚀 Proxy démarré sur http://localhost:{port}")
    print(f"📡 Elasticsearch: {ES_URL}")
    print("✅ Ouvre http://localhost:8080 dans ton navigateur")
    server = HTTPServer(('localhost', port), ProxyHandler)
    server.serve_forever()