"""Parcours d'interface de Brèche : titre → partie → joystick → niveau → pause → export → effacement → import → reprise → hors ligne.
Mesure aussi les cibles tactiles et la taille du texte sur chaque écran. Usage : python3 outils/qa/breche_flow.py [dossier_captures]"""
import sys, os, subprocess, time, json
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PORT = 8767; URL = f"http://localhost:{PORT}/petits-jeux/breche/"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/breche_flow"; os.makedirs(OUT, exist_ok=True)
srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)], cwd=os.path.dirname(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
MEASURE = """() => { const vis = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden' && el.closest('.screen, .hud, #app') && (!el.closest('.screen') || el.closest('.screen').classList.contains('show')); };
  const small = [...document.querySelectorAll('button, a, [data-act]')].filter(vis).map(el => { const r = el.getBoundingClientRect(); return { t: el.textContent.trim().slice(0, 20), w: Math.round(r.width), h: Math.round(r.height) }; }).filter(o => o.w < 44 || o.h < 44);
  const txt = [...document.querySelectorAll('.screen.show *, .hud *')].filter(el => el.childNodes.length && [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) && vis(el)).map(el => ({ t: el.textContent.trim().slice(0, 25), fs: parseFloat(getComputedStyle(el).fontSize) })).filter(o => o.fs < 16);
  return { small, txt, hscroll: document.documentElement.scrollWidth > innerWidth }; }"""
log = {}; errs = []
try:
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True)
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(URL); pg.wait_for_timeout(1200)
        log["titre"] = pg.evaluate(MEASURE); pg.screenshot(path=f"{OUT}/a_titre.png")
        pg.click("text=Règles"); pg.wait_for_timeout(200); log["regles"] = pg.evaluate(MEASURE); pg.screenshot(path=f"{OUT}/b_regles.png"); pg.click("text=Retour")
        pg.click("text=Nouvelle partie"); pg.wait_for_timeout(300)
        # joystick : glisser vers la droite pendant 1 s
        x0 = pg.evaluate("__game.state.player.x")
        cdp = ctx.new_cdp_session(pg)
        cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": 200, "y": 650}]})
        for i in range(1, 11):
            cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": 200 + i * 6, "y": 650}]}); pg.wait_for_timeout(30)
        pg.wait_for_timeout(800); pg.screenshot(path=f"{OUT}/c_jeu_joystick.png")
        cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        log["joystick_dx"] = round(pg.evaluate("__game.state.player.x") - x0, 1)
        log["jeu"] = pg.evaluate(MEASURE)
        # niveau supérieur : donner de l'XP
        pg.evaluate("__game.state.gems.push({x: __game.state.player.x, y: __game.state.player.y, v: 5, m: 1})"); pg.wait_for_timeout(700)
        log["mode_apres_xp"] = pg.evaluate("__game.mode()")
        log["niveau"] = pg.evaluate(MEASURE); pg.screenshot(path=f"{OUT}/d_niveau.png")
        nb_armes = pg.evaluate("__game.state.weapons.length + Object.keys(__game.state.passives).length")
        pg.locator("#cards .card").first.click(); pg.wait_for_timeout(300)
        log["choix_applique"] = pg.evaluate("__game.state.weapons.length + Object.keys(__game.state.passives).length") > nb_armes or pg.evaluate("__game.state.weapons[0].lvl") > 1
        pg.wait_for_timeout(2000)
        t_before = pg.evaluate("__game.state.t")
        pg.click("#pauseBtn"); pg.wait_for_timeout(300); log["pause"] = pg.evaluate(MEASURE); pg.screenshot(path=f"{OUT}/e_pause.png")
        pg.click("#sPause [data-act=save]"); pg.click("text=Obtenir le code de sauvegarde"); pg.wait_for_timeout(600)
        code = pg.input_value("#saveCode"); log["code_longueur"] = len(code); log["code_prefixe"] = code[:8]
        log["sauvegarde"] = pg.evaluate(MEASURE); pg.screenshot(path=f"{OUT}/f_sauvegarde.png")
        pg.close()  # effacement page fermée, comme une purge iOS
        cdp0 = ctx.new_cdp_session(ctx.new_page() if False else ctx.pages[0] if ctx.pages else ctx.new_page())
        cdp0.send("Storage.clearDataForOrigin", {"origin": f"http://localhost:{PORT}", "storageTypes": "local_storage"})
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(URL); pg.wait_for_timeout(800)
        log["reprise_visible_apres_effacement"] = pg.is_visible("#resumeBtn")
        pg.click("#sTitle [data-act=save]"); pg.fill("#saveCode", code); pg.click("text=Charger ce code"); pg.wait_for_timeout(1500)
        log["reprise_visible_apres_import"] = pg.is_visible("#resumeBtn")
        pg.click("#resumeBtn"); pg.wait_for_timeout(300)
        log["temps_avant_apres"] = [round(t_before, 1), round(pg.evaluate("__game.state.t"), 1)]
        pg.click("#sPause [data-act=unpause]"); pg.wait_for_timeout(500); log["mode_reprise"] = pg.evaluate("__game.mode()")
        # interruption
        pg.evaluate("Object.defineProperty(document, 'hidden', {value: true, configurable: true}); document.dispatchEvent(new Event('visibilitychange'))")
        log["mode_apres_arriere_plan"] = pg.evaluate("__game.mode()")
        # hors ligne
        ctx.set_offline(True); pg.reload(); pg.wait_for_timeout(1000)
        log["hors_ligne_titre"] = pg.is_visible("text=Nouvelle partie"); pg.screenshot(path=f"{OUT}/g_hors_ligne.png")
        ctx.set_offline(False)
        # paysage
        pg.set_viewport_size({"width": 844, "height": 390}); pg.wait_for_timeout(300)
        log["paysage_message"] = pg.is_visible("#rotate"); pg.screenshot(path=f"{OUT}/h_paysage.png")
        br.close()
finally:
    srv.terminate()
log["erreurs"] = errs
print(json.dumps(log, ensure_ascii=False, indent=1))
