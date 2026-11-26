"""Tests for Domain-Specific-Chatbot (MediAssist AI Pro).

The app is a Streamlit script, so `streamlit` and `groq` are stubbed with tiny
fakes before importing app.py. Only pure helpers + rendering escaping are
tested — no API key and no network needed.

Run from the repo root:

    python3 -m unittest discover -s tests -v
"""

import io
import os
import sys
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
sys.path.insert(0, REPO_ROOT)

# ---- Fake streamlit -------------------------------------------------------
# Import-time app.py only calls st.set_page_config() and st.markdown() (the
# CSS block). Everything else is called inside main(), which tests never run.


class _FakeStreamlit(types.ModuleType):
    def __init__(self):
        super().__init__("streamlit")
        self.secrets = {}
        self.session_state = {}
        self.markdown_calls = []

    def set_page_config(self, **kwargs):
        pass

    def markdown(self, *args, **kwargs):
        self.markdown_calls.append((args, kwargs))

    def __getattr__(self, name):
        def _dummy(*args, **kwargs):
            return None

        return _dummy


_fake_st = _FakeStreamlit()
sys.modules["streamlit"] = _fake_st

# ---- Fake groq ------------------------------------------------------------

_fake_groq = types.ModuleType("groq")


class _FakeGroq:
    def __init__(self, api_key=None):
        self.api_key = api_key


_fake_groq.Groq = _FakeGroq
sys.modules["groq"] = _fake_groq

import app  # noqa: E402  (imported after the stubs above)


# ---- Fake Groq client for groq_text() -------------------------------------


class _FakeResponse:
    def __init__(self, text):
        self.choices = [
            types.SimpleNamespace(message=types.SimpleNamespace(content=text))
        ]


class _NotFoundError(Exception):
    """Stands in for groq.NotFoundError (HTTP 404, model retired)."""

    def __init__(self, message="model_not_found"):
        super().__init__(message)
        self.status_code = 404


class _FakeCompletions:
    def __init__(self, behaviour):
        # behaviour: list of ("raise", error) or ("ok", text)
        self.behaviour = list(behaviour)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        kind, payload = self.behaviour.pop(0)
        if kind == "raise":
            raise payload
        return _FakeResponse(payload)


class _FakeClient:
    def __init__(self, behaviour):
        self.chat = types.SimpleNamespace(completions=_FakeCompletions(behaviour))


class TestModels(unittest.TestCase):
    def test_text_default_is_a_live_groq_model(self):
        # Groq retired llama-3.3-70b-versatile for free/dev tiers on
        # 2026-08-16; its recommended replacement is openai/gpt-oss-120b.
        text_model, _ = app.get_models()
        self.assertEqual(text_model, "openai/gpt-oss-120b")
        self.assertNotEqual(text_model, "llama-3.3-70b-versatile")

    def test_vision_default_is_maverick_not_scout(self):
        # Llama 4 Scout was shut down 2026-07-17; Maverick is the live
        # vision model on Groq.
        _, vision_model = app.get_models()
        self.assertEqual(
            vision_model, "meta-llama/llama-4-maverick-17b-128e-instruct"
        )
        self.assertNotIn("scout", vision_model)

    def test_no_retired_model_id_is_a_default(self):
        self.assertNotIn("llama-3.3-70b-versatile", app.TEXT_MODEL_DEFAULT)
        self.assertNotIn("llama-4-scout", app.VISION_MODEL_DEFAULT)


class TestGroqTextFallback(unittest.TestCase):
    def test_falls_back_when_primary_model_is_retired(self):
        client = _FakeClient(
            [
                ("raise", _NotFoundError("404 The model `openai/gpt-oss-120b` does not exist")),
                ("ok", "fallback answer"),
            ]
        )
        reply = app.groq_text(
            client, app.TEXT_MODEL_DEFAULT, [{"role": "user", "content": "hi"}]
        )
        self.assertEqual(reply, "fallback answer")
        self.assertEqual(len(client.chat.completions.calls), 2)
        self.assertEqual(
            client.chat.completions.calls[1]["model"], app.TEXT_MODEL_FALLBACK
        )

    def test_other_errors_are_not_swallowed(self):
        client = _FakeClient([("raise", RuntimeError("rate limit"))])
        with self.assertRaises(RuntimeError):
            app.groq_text(
                client, app.TEXT_MODEL_DEFAULT, [{"role": "user", "content": "hi"}]
            )
        self.assertEqual(len(client.chat.completions.calls), 1)

    def test_model_not_found_detection(self):
        self.assertTrue(app._is_model_not_found(_NotFoundError()))
        self.assertTrue(
            app._is_model_not_found(Exception("model_not_found: no such model"))
        )
        self.assertTrue(
            app._is_model_not_found(
                Exception("The model `x` does not exist or you do not have access")
            )
        )
        self.assertFalse(app._is_model_not_found(Exception("rate limit exceeded")))
        self.assertFalse(app._is_model_not_found(RuntimeError("boom")))


class TestEscaping(unittest.TestCase):
    def test_safe_html_escapes_tags(self):
        out = app.safe_html('<script>alert("xss")</script>')
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)

    def test_safe_html_escapes_event_handlers(self):
        out = app.safe_html('<img src=x onerror=alert(1)>')
        self.assertNotIn("<img", out)
        self.assertIn("&lt;img", out)

    def test_safe_html_keeps_newlines_as_breaks(self):
        out = app.safe_html("line one\nline two")
        self.assertIn("line one<br>line two", out)

    def test_render_bubble_escapes_user_input(self):
        _fake_st.markdown_calls.clear()
        app.render_bubble("user", '<img src=x onerror=alert(document.cookie)>')
        rendered = " ".join(str(a) for args, _ in _fake_st.markdown_calls for a in args)
        # No live tag may survive: the "<" must be escaped, so the browser
        # shows the text instead of creating an <img> element.
        self.assertNotIn("<img", rendered)
        self.assertIn("&lt;img", rendered)

    def test_render_bubble_escapes_ai_reply(self):
        _fake_st.markdown_calls.clear()
        app.render_bubble("assistant", "Hello <b>world</b>\nSecond line")
        rendered = " ".join(str(a) for args, _ in _fake_st.markdown_calls for a in args)
        self.assertNotIn("<b>world</b>", rendered)
        self.assertIn("&lt;b&gt;world&lt;/b&gt;", rendered)
        self.assertIn("<br>", rendered)


class TestHelpers(unittest.TestCase):
    def test_is_urgent(self):
        self.assertTrue(app.is_urgent("I have chest pain"))
        self.assertTrue(app.is_urgent("I CAN'T BREATHE"))
        self.assertTrue(app.is_urgent("severe bleeding from my leg"))
        self.assertFalse(app.is_urgent("mild headache since morning"))
        self.assertFalse(app.is_urgent("what is a healthy diet?"))

    def test_classify_vital(self):
        self.assertEqual(app.classify_vital("heart_rate", "72"), "normal")
        self.assertEqual(app.classify_vital("heart_rate", "105"), "warn")
        self.assertEqual(app.classify_vital("heart_rate", "45"), "danger")
        self.assertEqual(app.classify_vital("spo2", "98"), "normal")
        self.assertEqual(app.classify_vital("spo2", "92"), "warn")
        self.assertEqual(app.classify_vital("spo2", "85"), "danger")
        # Non-numeric input must not crash — it is treated as normal.
        self.assertEqual(app.classify_vital("heart_rate", "abc"), "normal")
        self.assertEqual(app.classify_vital("heart_rate", ""), "normal")
        self.assertEqual(app.classify_vital("weight", "70"), "normal")

    def test_resize_valid_image(self):
        from PIL import Image

        img = Image.new("RGB", (2000, 1500), color="red")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        out = app.resize_image_bytes(buf.getvalue())
        result = Image.open(io.BytesIO(out))
        self.assertEqual(result.format, "JPEG")
        self.assertLessEqual(result.width, 1200)
        self.assertLessEqual(result.height, 1200)

    def test_resize_rejects_corrupt_file(self):
        with self.assertRaises(ValueError):
            app.resize_image_bytes(b"this is not an image at all")

    def test_resize_rejects_oversized_upload(self):
        with self.assertRaises(ValueError):
            app.resize_image_bytes(b"\x00" * (app.MAX_UPLOAD_BYTES + 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
