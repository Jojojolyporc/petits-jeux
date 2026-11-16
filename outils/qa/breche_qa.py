"""QA de Brèche : erreurs console, simulations en masse, fps, captures.
Usage : python3 outils/qa/breche_qa.py [nb_parties] [dossier_captures]
Sert le dépôt depuis son dossier parent (même chemin que GitHub Pages)."""
import sys, json, os, subprocess, time, statistics
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARENT = os.path.dirname(ROOT)
PORT = 8765
URL = f"http://localhost:{PORT}/petits-jeux/breche/"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20  # 0 = pas de simulation
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/breche_qa"
os.makedirs(OUT, exist_ok=True)

srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)], cwd=PARENT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
errors, failed, foreign = [], [], []
try:
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True)
        pg = ctx.new_page()
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("requestfailed", lambda r: failed.append(r.url))
        pg.on("response", lambda r: failed.append(f"{r.status} {r.url}") if r.status >= 400 else None)
        pg.on("request", lambda r: foreign.append(r.url) if not r.url.startswith(f"http://localhost:{PORT}") and not r.url.startswith("data:") else None)
        pg.goto(URL); pg.wait_for_timeout(1500)
        pg.screenshot(path=f"{OUT}/01_titre.png")
        sw = pg.evaluate("navigator.serviceWorker.getRegistration().then(r => !!(r && r.active))")

        # --- simulations ---
        runs = []
        t0 = time.time()
        for s in range(1, N + 1):
            runs.append(pg.evaluate(f"__game.simulate({{seed:{s}}})"))
        simtime = time.time() - t0
        json.dump(runs, open(f"{OUT}/runs.json", "w"), indent=1)

        # --- fps en scène chargée : partie robot avancée à 3:30 ---
        pg.evaluate("__game.newRun(42); __game.setBot(true); __game.fastForward(210, true); __game.state.weapons.forEach(w => w.lvl = 1); __game.spawnAround('imp', 420); __game.spawnAround('brute', 60)")
        enemies_at = pg.evaluate("__game.state.enemies.length")
        fps = pg.evaluate("""() => new Promise(res => { const ticks = []; let last = performance.now(); const fr = []; const end = last + 10000;
            function f(now) { fr.push(now - last); last = now; if (now < end) requestAnimationFrame(f); else res(fr); } requestAnimationFrame(f); })""")
        secs = []; acc = 0; cnt = 0
        for d in fps:
            acc += d; cnt += 1
            if acc >= 1000: secs.append(cnt * 1000 / acc); acc = 0; cnt = 0
        pg.screenshot(path=f"{OUT}/02_horde.png")
        enemies_after = pg.evaluate("__game.state.enemies.length")
        # avance jusqu'au boss éveillé
        pg.evaluate("__game.fastForward(252, true)")
        pg.wait_for_timeout(800)
        pg.screenshot(path=f"{OUT}/03_boss.png")
        pg.evaluate("__game.setBot(false)")

        # --- CPU ralenti x4 ---
        cdp = ctx.new_cdp_session(pg)
        pg.evaluate("__game.newRun(43); __game.setBot(true); __game.fastForward(210, true); __game.state.weapons.forEach(w => w.lvl = 1); __game.spawnAround('imp', 420); __game.spawnAround('brute', 60)")
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
        fps4 = pg.evaluate("""() => new Promise(res => { let n = 0; const t0 = performance.now(); function f(now) { n++; if (now - t0 < 5000) requestAnimationFrame(f); else res(n / ((now - t0) / 1000)); } requestAnimationFrame(f); })""")
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": 1})
        pg.evaluate("__game.setBot(false)")
        br.close()
finally:
    srv.terminate()

if not runs: runs = [{"result":"none","t":0,"lvlAt240":0,"peak":0,"bossHp":0,"bossFight":0}]
wins = [r for r in runs if r["result"] == "win"]
loses = [r for r in runs if r["result"] == "lose"]
early = [r for r in loses if r["t"] < 240]
print(json.dumps({
    "parties": len(runs), "simulation_s": round(simtime, 1),
    "victoires": len(wins), "defaites": len(loses), "morts_avant_4min": len(early), "timeouts": len([r for r in runs if r["result"] == "timeout"]),
    "duree_victoire_mediane": statistics.median([r["t"] for r in wins]) if wins else None,
    "duree_victoire_min_max": [min(r["t"] for r in wins), max(r["t"] for r in wins)] if wins else None,
    "combat_boss_median": statistics.median([r["bossFight"] for r in wins]) if wins else None,
    "niveau_a_4min_median": statistics.median([r["lvlAt240"] for r in runs if r["lvlAt240"]]) if any(r["lvlAt240"] for r in runs) else None,
    "pic_ennemis_median": statistics.median([r["peak"] for r in runs]),
    "pv_boss_restants_defaites": [r["bossHp"] for r in loses],
    "morts_t": sorted(r["t"] for r in loses),
    "ennemis_scene_fps": [enemies_at, enemies_after],
    "fps_median": round(statistics.median(secs), 1) if secs else None, "fps_pire_seconde": round(min(secs), 1) if secs else None,
    "fps_cpu_x4": round(fps4, 1),
    "service_worker_actif": sw,
    "erreurs_console": errors[:10], "echecs_reseau": failed[:10], "requetes_externes": foreign[:10],
}, indent=1, ensure_ascii=False))
