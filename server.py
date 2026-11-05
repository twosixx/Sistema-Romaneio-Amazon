import json, os, socket, sqlite3, uuid, webbrowser
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent
DB = ROOT / "data" / "romaneio.db"
DB.parent.mkdir(exist_ok=True)

def connection():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def initialize():
    with connection() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS orders (
          id TEXT PRIMARY KEY, order_id TEXT NOT NULL, sku TEXT, asin TEXT, title TEXT,
          quantity TEXT, tracking_id TEXT, ship_method TEXT, history_date TEXT NOT NULL,
          source_name TEXT, imported_at TEXT NOT NULL,
          UNIQUE(order_id, sku, tracking_id, history_date)
        )""")

def network_urls():
    addresses = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127."):
                addresses.add(f"http://{ip}:8765")
    except OSError: pass
    return sorted(addresses)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(ROOT), **kwargs)
    def reply(self, data, status=200):
        raw=json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def body(self):
        return json.loads(self.rfile.read(int(self.headers.get("Content-Length",0))).decode("utf-8"))
    def do_GET(self):
        if self.path == "/api/status": return self.reply({"urls":network_urls()})
        if self.path == "/api/history":
            with connection() as db:
                rows=[{"id":r["id"],"Order ID":r["order_id"],"SKU":r["sku"],"ASIN":r["asin"],"Item Title":r["title"],"Item Quantity":r["quantity"],"Tracking ID":r["tracking_id"],"Ship Method":r["ship_method"],"historyDate":r["history_date"],"importedAt":r["imported_at"]} for r in db.execute("SELECT * FROM orders ORDER BY history_date DESC, imported_at DESC")]
            return self.reply(rows)
        return super().do_GET()
    def do_POST(self):
        if self.path != "/api/history": return self.reply({"error":"not found"},404)
        try:
            payload=self.body(); day=payload["date"]; source=payload.get("source",""); orders=payload["orders"]; added=0
            with connection() as db:
                for row in orders:
                    result=db.execute("""INSERT OR IGNORE INTO orders
                    (id,order_id,sku,asin,title,quantity,tracking_id,ship_method,history_date,source_name,imported_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (str(uuid.uuid4()),row.get("Order ID",""),row.get("SKU",""),row.get("ASIN",""),row.get("Item Title",""),row.get("Item Quantity",""),row.get("Tracking ID",""),row.get("Ship Method",""),day,source,datetime.now().isoformat()))
                    added += result.rowcount
            return self.reply({"added":added})
        except Exception as error: return self.reply({"error":str(error)},400)
    def do_DELETE(self):
        parts=self.path.split("/")
        with connection() as db:
            if len(parts)==4 and parts[2]=="day": count=db.execute("DELETE FROM orders WHERE history_date=?",(parts[3],)).rowcount
            elif len(parts)==3 and parts[1]=="history": count=db.execute("DELETE FROM orders WHERE id=?",(parts[2],)).rowcount
            else: return self.reply({"error":"not found"},404)
        return self.reply({"deleted":count})

if __name__ == "__main__":
    initialize(); print("Romaneio: http://localhost:8765"); print("Equipe: " + ", ".join(network_urls()))
    webbrowser.open("http://localhost:8765")
    ThreadingHTTPServer(("0.0.0.0",8765),Handler).serve_forever()
