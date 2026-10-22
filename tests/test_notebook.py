# -*- coding: utf-8 -*-
"""Tests for the notebook: texts, segmentation round trips, the rendered page and the bridge.

  python3 -m unittest discover -s tests

Uses only the Python 3 standard library (node, when installed, checks the page's script).
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from notebook import bridge, languages, page  # noqa: E402
from notebook.product import STRINGS_DIR, TEMPLATE, Product  # noqa: E402

PLACEHOLDER_RE = re.compile(r"(?<!\{)\{(\w+)\}(?!\})")


def load(language):
    with open(os.path.join(STRINGS_DIR, f"{language}.json"), encoding="utf-8") as f:
        return json.load(f)


def product(language, **extra):
    data = {"name": "Test Product?", "slug": "notebook-test", "language": language, "patterns": {"R1": "Pattern one"}}
    data.update(extra)
    return Product(data)


class StubAudit:
    """The four functions the page needs from a skill's audit module."""

    @staticmethod
    def measure(text):
        return {"words": len(text.split())}

    @staticmethod
    def alarms(measurement):
        return [("Words", measurement["words"], "info", "")]

    @staticmethod
    def guess_profile(text):
        return {"genre": None}

    @staticmethod
    def read(source):
        return source


def accepted(segments):
    return "".join(s["x"] if s["t"] == "eq" else s["i"] for s in segments)


def reverted(segments):
    return "".join(s["x"] if s["t"] == "eq" else s["d"] for s in segments)


class Strings(unittest.TestCase):
    def test_same_keys_and_shapes(self):
        tr, en = load("tr"), load("en")
        self.assertEqual(sorted(tr), sorted(en))
        for key in tr:
            self.assertEqual(type(tr[key]), type(en[key]), key)
            if isinstance(tr[key], dict):
                self.assertEqual(sorted(tr[key]), ["one", "other"], key)
                self.assertEqual(sorted(en[key]), ["one", "other"], key)
            if isinstance(tr[key], list):
                self.assertEqual(len(tr[key]), len(en[key]), key)

    def test_same_placeholders(self):
        tr, en = load("tr"), load("en")

        def names(value):
            values = value.values() if isinstance(value, dict) else value if isinstance(value, list) else [value]
            # {name} and {Name} are the same placeholder written two ways
            return {n.lower() for v in values for n in PLACEHOLDER_RE.findall(v)}
        for key in tr:
            self.assertEqual(names(tr[key]), names(en[key]), key)

    def test_every_used_key_exists(self):
        strings = load("en")
        sources = {}
        for name in ("template.html", "page.py", "bridge.py"):
            with open(os.path.join(ROOT, "notebook", name), encoding="utf-8") as f:
                sources[name] = f.read()
        used = set()
        used |= set(re.findall(r"\{\{([a-z_]+\.[a-z_]+)\}\}", sources["template.html"]))
        used |= set(re.findall(r'msg\("([a-z_]+\.[a-z_]+)"', sources["template.html"]))
        used |= set(re.findall(r'\bt\("([a-z_]+\.[a-z_]+)"', sources["page.py"] + sources["bridge.py"]))
        used |= {f"engine.detail_{e}" for e in bridge.ENGINES}  # built from the engine's name in the page
        self.assertTrue(used)
        self.assertEqual(sorted(k for k in used if k not in strings and not k.endswith("_")), [])

    def test_every_key_formats(self):
        for language in ("tr", "en"):
            p = product(language)
            for key, value in load(language).items():
                if isinstance(value, list):
                    continue
                names = {n for v in (value.values() if isinstance(value, dict) else [value]) for n in PLACEHOLDER_RE.findall(v)}
                p.t(key, **dict({n: "x" for n in names}, n=2))

    def test_plural(self):
        p = product("en")
        self.assertEqual(p.t("meta.changes", n=1), "1 change")
        self.assertEqual(p.t("meta.changes", n=3), "3 changes")

    def test_product_overrides(self):
        p = product("en", strings={"card.keep": "Fine"})
        self.assertEqual(p.t("card.keep"), "Fine")
        self.assertEqual(p.t("feedback.header"), "[Test Product? · feedback]")
        self.assertEqual(p.page_strings()["download.file_name"], "notebook-test-result.txt")
        self.assertNotIn("bridge.prompt", p.page_strings())


class Language(unittest.TestCase):
    def test_turkish_lowercase(self):
        self.assertEqual(languages.lower("IŞIK İzmir", "tr"), "ışık izmir")
        self.assertEqual(languages.lower("LIGHT", "en"), "light")

    def test_sentences(self):
        page.LANGUAGE = "tr"
        self.assertEqual(page.sentences("Dr. Ayşe geldi. Sonra gitti."), ["Dr. Ayşe geldi. ", "Sonra gitti."])
        self.assertEqual(page.sentences("Elma, armut vb. meyveler aldık. Bitti."), ["Elma, armut vb. meyveler aldık. ", "Bitti."])
        page.LANGUAGE = "en"
        self.assertEqual(page.sentences("Ms. Patel left. Then J. Smith came."), ["Ms. Patel left. ", "Then J. Smith came."])
        self.assertEqual(page.sentences("Bring fruit, e.g. apples. Done."), ["Bring fruit, e.g. apples. ", "Done."])


CASES = {
    "tr": [
        ("Merhaba ekip,\n\nBu sadece bir araç değil, aynı zamanda bir köprü. Panel hızlı.\n\nTeşekkürler.",
         "Merhaba ekip,\n\nPanel ekipleri aynı ekranda buluşturuyor. Panel hızlı.\n\nTeşekkürler.",
         [{"before": "Bu sadece bir araç değil, aynı zamanda bir köprü.", "after": "Panel ekipleri aynı ekranda buluşturuyor."}]),
        # a deleted sentence in the middle of a paragraph
        ("Değerli ekip. Günümüzde her şey hızla değişiyor. Yeni paneli cuma günü açtık.",
         "Değerli ekip. Yeni paneli cuma günü açtık.",
         [{"before": "Günümüzde her şey hızla değişiyor.", "after": ""}]),
        # an added sentence at the end of a paragraph
        ("İlk hafta iyi geçti.\n\nSorular için yazın.",
         "İlk hafta iyi geçti. Yanıt süreleri kısaldı.\n\nSorular için yazın.",
         [{"before": "", "after": "Yanıt süreleri kısaldı."}]),
        # no notes: the similarity diff alone
        ("Kapsamlı ve yenilikçi bir çözüm sunuyoruz.\n\nIşıklar yandı.", "Bir çözüm sunuyoruz.\n\nIşıklar yandı, kapı açıldı.", []),
    ],
    "en": [
        ("Hi team,\n\nThis isn't just a tool, it's a bridge. The panel is fast.\n\nThanks.",
         "Hi team,\n\nThe panel puts every request on one screen. The panel is fast.\n\nThanks.",
         [{"before": "This isn't just a tool, it's a bridge.", "after": "The panel puts every request on one screen."}]),
        ("Dear team. In today's fast-paced world, everything changes. We launched the panel on Friday.",
         "Dear team. We launched the panel on Friday.",
         [{"before": "In today's fast-paced world, everything changes.", "after": ""}]),
        ("The first week went well.\n\nWrite to us with questions.",
         "The first week went well. Reply times are shorter.\n\nWrite to us with questions.",
         [{"before": "", "after": "Reply times are shorter."}]),
        ("We offer a comprehensive, innovative solution.\n\nMs. Patel agreed.", "We offer a solution.\n\nMs. Patel agreed, then left.", []),
    ],
}


class RoundTrip(unittest.TestCase):
    def test_keep_all_and_revert_all(self):
        for language, cases in CASES.items():
            p = product(language)
            for before, after, notes in cases:
                with self.subTest(language=language, before=before[:30]):
                    _, data = page.build_page(p, StubAudit, before, after, {"changes": [dict(n) for n in notes]})
                    self.assertEqual(accepted(data["segments"]), page.normalize(after))
                    self.assertEqual(reverted(data["segments"]), page.normalize(before))
                    self.assertTrue(any(s["t"] == "ch" for s in data["segments"]))
                    for n in data["notes"]:
                        self.assertTrue(n["parts"], n)

    def test_no_double_space_after_deletion(self):
        p = product("tr")
        before, after, notes = CASES["tr"][1]
        _, data = page.build_page(p, StubAudit, before, after, {"changes": [dict(n) for n in notes]})
        self.assertNotIn("  ", accepted(data["segments"]))


class RenderedPage(unittest.TestCase):
    def render(self, language):
        p = product(language, title_html="Test Product<b>?</b>")
        before, after, notes = CASES[language][0]
        meta = {"title": "</script><b>x</b> /*__LIVE__*/null", "changes": [dict(n) for n in notes]}
        html, _ = page.build_page(p, StubAudit, before, after, meta)
        return html

    def test_everything_filled(self):
        for language in ("tr", "en"):
            html = self.render(language)
            self.assertIsNone(re.search(r"\{\{[a-z_]+\.[a-z_]+\}\}", html), language)
            for slot in ("__LANG__", "__TITLE__", "__PRODUCT_TITLE_HTML__", "/*__STRINGS__*/null",
                         "/*__PRODUCT__*/null", "/*__DATA__*/null"):
                self.assertNotIn(slot, html, (language, slot))
            self.assertIn(f'<html lang="{language}">', html)
            self.assertIn("Test Product<b>?</b></h1>", html)
            self.assertEqual(html.count("/*__LIVE__*/null"), 1)  # only the bridge's own slot
            self.assertEqual(html.count("</script>"), 1)

    def test_template_has_no_product_text(self):
        with open(TEMPLATE, encoding="utf-8") as f:
            template = f.read()
        self.assertIsNone(re.search(r"[çğıöşüÇĞİÖŞÜ]", template))
        self.assertNotIn("insanlik", template.lower())
        self.assertNotIn("still-human", template.lower())

    @unittest.skipUnless(shutil.which("node"), "node is not installed")
    def test_script_parses(self):
        for language in ("tr", "en"):
            html = self.render(language)
            script = html[html.index("<script>") + len("<script>"):html.rindex("</script>")]
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
                f.write(script)
            try:
                r = subprocess.run(["node", "--check", f.name], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)
            finally:
                os.remove(f.name)


class Bridge(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp(prefix="notebook-test-")
        os.environ["NOTEBOOK_TEST_ROOT"] = os.path.join(self.folder, "sessions")
        # a skill's bridge.py: binds the bridge to its product and runs it
        self.script = os.path.join(self.folder, "bridge.py")
        with open(self.script, "w", encoding="utf-8") as f:
            f.write(f"""import sys
sys.path.insert(0, {ROOT!r})
from notebook import bridge
from notebook.product import Product
bridge.configure(Product({{"name": "Test Product?", "slug": "notebook-test", "language": "en", "root_env": "NOTEBOOK_TEST_ROOT"}}), __file__)
bridge.main()
""")
        bridge.configure(product("en", root_env="NOTEBOOK_TEST_ROOT"), self.script)
        self.page = os.path.join(self.folder, "review.html")
        html, _ = page.build_page(bridge.PRODUCT, StubAudit, "One. Two.", "One. Three.", {})
        with open(self.page, "w", encoding="utf-8") as f:
            f.write(html)

    def tearDown(self):
        os.environ.pop("NOTEBOOK_TEST_ROOT", None)
        shutil.rmtree(self.folder, ignore_errors=True)

    def test_start_send_close(self):
        info, address = bridge.start(self.page, agent="none")
        try:
            self.assertTrue(address.startswith("http://127.0.0.1:"))
            status = bridge.call(info, "/api/status")
            self.assertFalse(status["engines"]["agent"])
            self.assertEqual(bridge.call(info, "/api/send", {"text": "[feedback]"})["status"], "saved")
            event = bridge.call(info, "/api/agent/wait?timeout=1", timeout=10)
            self.assertEqual(event, {"type": "send", "data": {"text": "[feedback]"}})
            self.assertEqual(bridge.read_info(info["id"])["port"], info["port"])
        finally:
            bridge.call(info, "/api/close", {})
        for _ in range(50):
            if not os.path.exists(os.path.join(info["dir"], "state.json")):
                break
            time.sleep(0.1)
        self.assertFalse(os.path.exists(os.path.join(info["dir"], "state.json")))

    def test_prompt_in_product_language(self):
        prompt = bridge.suggestion_prompt({"before": "a", "after": "b", "request": ""})
        self.assertIn("Test Product?", prompt)
        self.assertIn('{"suggestions": [', prompt)
        self.assertIn(bridge.PRODUCT.t("bridge.default_request"), prompt)


if __name__ == "__main__":
    unittest.main()
