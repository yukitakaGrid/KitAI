import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import approval
import logic
import rules
from config import Config

CFG = Config({"APPROVER_USER_IDS": "1, 2", "APPROVER_ROLE_IDS": "900"})
GOOD = {"name": "neko", "trigger": {"type": "contains", "text": "にゃ"},
        "actions": [{"type": "reply", "text": "にゃーん"}]}

class FakeMaker:
    def __init__(self, rule=None, exc=None):
        self.rule, self.exc = rule, exc
    def make(self, text):
        if self.exc:
            raise self.exc
        return rules.validate_rule(self.rule)

def msg(content, uid=1, roles=(), ch=10, mentioned=True, bot=False):
    return {"author_id": uid, "role_ids": list(roles), "channel_id": ch,
            "content": content, "mentioned": mentioned, "is_bot": bot}

class RuleValidation(unittest.TestCase):
    def test_good(self):
        self.assertEqual(rules.validate_rule(GOOD)["name"], "neko")

    def test_rejects_code_like_and_unknown(self):
        bad = [
            {**GOOD, "code": "import os"},
            {**GOOD, "actions": [{"type": "exec", "text": "x"}]},
            {**GOOD, "actions": [{"type": "reply", "text": "x", "eval": "1"}]},
            {**GOOD, "actions": []},
            {**GOOD, "actions": [{"type": "reply", "text": "a"}] * 4},
            {**GOOD, "trigger": {"type": "regex", "text": "(a+)+"}},
            {**GOOD, "actions": [{"type": "reply", "text": "x" * 301}]},
            {**GOOD, "actions": [{"type": "delete_message", "text": "x"}]},
            {**GOOD, "name": ""},
            "not a dict",
        ]
        for b in bad:
            with self.assertRaises(rules.RuleError, msg=str(b)):
                rules.validate_rule(b)

    def test_ai_output_fenced_and_garbage(self):
        self.assertEqual(rules.parse_ai_output("```json\n" + json.dumps(GOOD) + "\n```")["name"], "neko")
        with self.assertRaises(rules.RuleError):
            rules.parse_ai_output("import os; os.system('x')")

    def test_match_case(self):
        r = rules.validate_rule({**GOOD, "trigger": {"type": "contains", "text": "Abc"}})
        self.assertTrue(rules.match([r], "xxabcxx"))
        r2 = rules.validate_rule({**GOOD, "trigger": {"type": "contains", "text": "Abc", "ignore_case": False}})
        self.assertFalse(rules.match([r2], "xxabcxx"))

    def test_store_roundtrip_and_tampered_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.json")
            s = rules.RuleStore(p)
            s.add(GOOD)
            self.assertEqual(len(rules.RuleStore(p).rules), 1)
            with open(p, "w") as f:
                json.dump([{"name": "x", "trigger": {"type": "contains", "text": "a"},
                            "actions": [{"type": "shell", "text": "rm"}]}], f)
            with self.assertRaises(rules.RuleError):
                rules.RuleStore(p)

class Approval(unittest.TestCase):
    def test_partial_match_no_longer_approves(self):
        p = approval.Pending()
        p.put(10, 1, GOOD)
        for t in ("Yesterday", "No problem yes", "Yes!"):
            self.assertEqual(p.decide(10, t, 1, [], CFG)[0], "ignored")
        self.assertTrue(p.has(10))

    def test_non_approver_denied_and_pending_kept(self):
        p = approval.Pending()
        p.put(10, 1, GOOD)
        self.assertEqual(p.decide(10, "Yes", 99, [], CFG)[0], "denied")
        self.assertTrue(p.has(10))
        self.assertEqual(p.decide(10, "yes", 99, [900], CFG)[0], "approved")

    def test_expiry_and_channel_binding(self):
        t = [0]
        p = approval.Pending(clock=lambda: t[0])
        p.put(10, 1, GOOD)
        self.assertEqual(p.decide(11, "Yes", 1, [], CFG)[0], "ignored")
        t[0] = 301
        self.assertEqual(p.decide(10, "Yes", 1, [], CFG)[0], "ignored")

class Logic(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.store = rules.RuleStore(os.path.join(self.d.name, "r.json"))
        self.state = {"edit": False, "pending": approval.Pending()}
    def tearDown(self):
        self.d.cleanup()

    def run_(self, m, maker=None):
        return logic.handle(m, self.state, CFG, self.store, maker or FakeMaker(GOOD))

    def test_full_flow(self):
        self.run_(msg("@bot !edit"))
        out = self.run_(msg("@bot 猫語で"))
        self.assertIn("Yes", out[0][1])
        self.assertEqual(self.store.rules, [])
        self.run_(msg("Yes", mentioned=False))
        self.assertEqual(len(self.store.rules), 1)
        self.assertEqual(self.run_(msg("にゃ", uid=50, mentioned=False)), [("send", "にゃーん")])

    def test_non_approver_cannot_switch_or_request(self):
        self.assertIn("承認者", self.run_(msg("!edit", uid=99))[0][1])
        self.assertFalse(self.state["edit"])
        self.state["edit"] = True
        self.assertIn("承認者", self.run_(msg("作って", uid=99))[0][1])

    def test_ai_failure_does_not_leak(self):
        self.state["edit"] = True
        out = self.run_(msg("x"), FakeMaker(exc=RuntimeError("key sk-SECRET")))
        self.assertNotIn("SECRET", out[0][1])

    def test_bot_messages_ignored_and_delete_needs_rule(self):
        self.assertEqual(self.run_(msg("お前", mentioned=False)), [])  # 既定の「お前」削除は無い
        self.store.add({"name": "d", "trigger": {"type": "contains", "text": "お前"},
                        "actions": [{"type": "delete_message"}]})
        self.assertEqual(self.run_(msg("お前", bot=True, mentioned=False)), [])
        self.assertEqual(self.run_(msg("お前", mentioned=False)), [("delete",)])

class ConfigTest(unittest.TestCase):
    def test_missing(self):
        self.assertEqual(len(Config({}).missing()), 3)
        c = Config({"DISCORD_TOKEN": "a", "OPENAI_API_KEY": "b", "APPROVER_USER_IDS": "5"})
        self.assertEqual(c.missing(), [])

if __name__ == "__main__":
    unittest.main()
