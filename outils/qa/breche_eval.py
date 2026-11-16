"""Évalue une expression JS dans Brèche (viewport iPhone) et affiche le résultat JSON.
Usage : python3 outils/qa/breche_eval.py "<expression JS>" [fichier_de_reglages_js]"""
import sys, json, os, subprocess, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PORT = 8766
srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)], cwd=os.path.dirname(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
try:
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = br.new_page(viewport={"width": 390, "height": 844})
        pg.goto(f"http://localhost:{PORT}/petits-jeux/breche/"); pg.wait_for_timeout(800)
        if len(sys.argv) > 2: pg.evaluate(open(sys.argv[2]).read())
        print(json.dumps(pg.evaluate(sys.argv[1]), ensure_ascii=False))
        br.close()
finally:
    srv.terminate()
