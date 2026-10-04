import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import approval
import logic
import asyncio
import bot
import ratelimit
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

class RateLimit(unittest.TestCase):
    def test_window_slides(self):
        t = [0.0]
        rl = ratelimit.RateLimiter(2, 10, clock=lambda: t[0])
        self.assertTrue(rl.allow("a")); self.assertTrue(rl.allow("a"))
        self.assertFalse(rl.allow("a"))
        self.assertTrue(rl.allow("b"))  # キーごとに独立
        t[0] = 10.0
        self.assertTrue(rl.allow("a"))

    def test_rule_replies_limited_per_channel(self):
        d = tempfile.TemporaryDirectory(); self.addCleanup(d.cleanup)
        store = rules.RuleStore(os.path.join(d.name, "r.json"))
        store.add(rules.validate_rule(GOOD))
        state = {"edit": False, "pending": approval.Pending(),
                 "rule_limiter": ratelimit.RateLimiter(2, 60)}
        run = lambda ch: logic.handle(msg("にゃ", mentioned=False, ch=ch), state, CFG, store, None)
        self.assertTrue(run(10)); self.assertTrue(run(10))
        self.assertEqual(run(10), [])
        self.assertTrue(run(11))

    def test_ai_requests_limited_per_user(self):
        d = tempfile.TemporaryDirectory(); self.addCleanup(d.cleanup)
        store = rules.RuleStore(os.path.join(d.name, "r.json"))
        state = {"edit": True, "pending": approval.Pending(),
                 "ai_limiter": ratelimit.RateLimiter(1, 60)}
        h = lambda: logic.handle(msg("neko"), state, CFG, store, FakeMaker(GOOD))
        self.assertIn("登録していい", h()[0][1])
        self.assertIn("多すぎます", h()[0][1])

class PendingPersistence(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); self.addCleanup(self.d.cleanup)
        self.p = os.path.join(self.d.name, "pending.json")

    def test_survives_restart_and_still_needs_approver(self):
        t = [1000.0]
        approval.Pending(clock=lambda: t[0], path=self.p).put(10, 1, rules.validate_rule(GOOD))
        again = approval.Pending(clock=lambda: t[0], path=self.p)
        self.assertEqual(again.decide(10, "yes", 5, [], CFG)[0], "denied")
        self.assertEqual(again.decide(10, "yes", 1, [], CFG)[0], "approved")
        self.assertEqual(approval.Pending(clock=lambda: t[0], path=self.p).has(10), False)

    def test_expired_dropped_on_load(self):
        t = [1000.0]
        approval.Pending(clock=lambda: t[0], path=self.p).put(10, 1, rules.validate_rule(GOOD))
        t[0] += approval.TTL_SECONDS + 1
        self.assertFalse(approval.Pending(clock=lambda: t[0], path=self.p).has(10))

    def test_tampered_or_broken_file_ignored(self):
        t = [1000.0]
        evil = {"10": [1, {**GOOD, "code": "import os"}, 2000.0]}
        for content in (json.dumps(evil), "{broken"):
            with open(self.p, "w") as f:
                f.write(content)
            self.assertFalse(approval.Pending(clock=lambda: t[0], path=self.p).has(10))

class FakeChan:
    def __init__(self): self.sent = []
    async def send(self, text, allowed_mentions=None): self.sent.append((text, allowed_mentions))

class FakeMsg:
    def __init__(self, content, uid=1, roles=(), ch=None, bot_=False, fail_delete=False):
        self.content = content
        self.author = type("A", (), {"id": uid, "bot": bot_,
                                     "roles": [type("R", (), {"id": r}) for r in roles]})()
        self.channel = ch or type("C", (FakeChan,), {"id": 10})()
        self.deleted, self.fail = False, fail_delete
    async def delete(self):
        if self.fail: raise RuntimeError("Forbidden")
        self.deleted = True

class FakeUser:
    def mentioned_in(self, m): return "<@bot>" in m.content

class BotCase(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); self.addCleanup(self.d.cleanup)
        self.store = rules.RuleStore(os.path.join(self.d.name, "r.json"))
        cfg = Config({"APPROVER_USER_IDS": "1", "KITAI_PENDING_PATH": os.path.join(self.d.name, "p.json")})
        self.cfg, self.state = cfg, bot.build_state(cfg)
    def go(self, m):
        asyncio.run(bot.process(m, FakeUser(), self.state, self.cfg, self.store,
                                FakeMaker(GOOD), "NOMENTIONS"))

class BotBridge(BotCase):

    def test_reply_uses_no_mentions_and_roles_mapped(self):
        self.store.add(rules.validate_rule(GOOD))
        m = FakeMsg("にゃ")
        self.go(m)
        self.assertEqual(m.channel.sent, [("にゃーん", "NOMENTIONS")])
        self.assertEqual(bot.to_msg(FakeMsg("x", roles=(7,)), FakeUser())["role_ids"], [7])

    def test_delete_failure_does_not_crash(self):
        self.store.add(rules.validate_rule({**GOOD, "actions": [{"type": "delete_message"}]}))
        self.go(FakeMsg("にゃ", fail_delete=True))

    def test_edit_flow_through_bridge(self):
        self.go(FakeMsg("<@bot> !edit"))
        m = FakeMsg("<@bot> ねこ")
        self.go(m)
        self.assertIn("登録していい", m.channel.sent[0][0])
        m.channel.sent.clear()
        self.go(FakeMsg("yes", ch=m.channel))
        self.assertIn("登録しました", m.channel.sent[0][0])

class BotAbnormal(BotCase):
    """橋渡しを通した異常系。"""
    def ask(self, text, uid=1, ch=None, maker=None):
        m = FakeMsg(text, uid=uid, ch=ch)
        asyncio.run(bot.process(m, FakeUser(), self.state, self.cfg, self.store,
                                maker or FakeMaker(GOOD), "NOMENTIONS"))
        return m

    def request_rule(self):
        self.ask("<@bot> !edit")
        m = self.ask("<@bot> ねこ")
        return m.channel

    def test_non_approver_yes_is_denied_and_pending_survives(self):
        ch = self.request_rule()
        self.ask("yes", uid=99, ch=ch)
        self.assertIn("決められた承認者だけ", ch.sent[-1][0])
        self.assertEqual(self.store.rules, [])
        self.ask("yes", uid=1, ch=ch)  # 承認者なら、まだ通る
        self.assertEqual(len(self.store.rules), 1)

    def test_expired_pending_is_ignored(self):
        t = [1000.0]
        self.state["pending"] = approval.Pending(clock=lambda: t[0])
        ch = self.request_rule()
        t[0] += approval.TTL_SECONDS + 1
        n = len(ch.sent)
        self.ask("yes", uid=1, ch=ch)
        self.assertEqual(len(ch.sent), n)  # 何も返さない
        self.assertEqual(self.store.rules, [])

    def test_ai_failure_and_bad_output_reported_without_detail(self):
        self.ask("<@bot> !edit")
        for exc in (RuntimeError("secret-detail-123"), rules.RuleError("検査に通りません")):
            m = self.ask("<@bot> ねこ", maker=FakeMaker(exc=exc))
            self.assertIn("作れませんでした", m.channel.sent[-1][0])
            self.assertNotIn("secret-detail-123", m.channel.sent[-1][0])
        self.assertFalse(self.state["pending"].has(10))

    def test_broken_or_tampered_pending_file_at_startup(self):
        for content in ("{broken", json.dumps({"10": [1, {**GOOD, "code": "x"}, 9e12]})):
            with open(self.cfg.pending_path, "w") as f:
                f.write(content)
            st = bot.build_state(self.cfg)
            self.assertFalse(st["pending"].has(10))

class ConfigTest(unittest.TestCase):
    def test_missing(self):
        self.assertEqual(len(Config({}).missing()), 3)
        c = Config({"DISCORD_TOKEN": "a", "OPENAI_API_KEY": "b", "APPROVER_USER_IDS": "5"})
        self.assertEqual(c.missing(), [])

if __name__ == "__main__":
    unittest.main()
