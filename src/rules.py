"""AI が出すのはコードではなく JSON のルール。ここで厳密に検査してから使う。

ルール例:
{"name": "neko", "trigger": {"type": "contains", "text": "にゃ"},
 "actions": [{"type": "reply", "text": "にゃーん"}]}
"""
import json
import os
import tempfile

MAX_RULES = 50
MAX_ACTIONS = 3
MAX_TEXT = 300
MAX_NAME = 40
TRIGGER_TYPES = {"contains"}
ACTION_TYPES = {"reply", "delete_message"}
DANGEROUS_ACTIONS = {"delete_message"}  # 承認画面で強調する

class RuleError(ValueError):
    pass

def _only_keys(d, allowed, where):
    if not isinstance(d, dict):
        raise RuleError(f"{where} は辞書であること")
    extra = set(d) - allowed
    if extra:
        raise RuleError(f"{where} に未知のキー: {sorted(extra)}")

def _text(v, where):
    if not isinstance(v, str) or not v.strip():
        raise RuleError(f"{where} は空でない文字列")
    if len(v) > MAX_TEXT:
        raise RuleError(f"{where} は{MAX_TEXT}文字以内")
    return v

def validate_rule(rule):
    """正規化した新しい辞書を返す。不正なら RuleError。"""
    _only_keys(rule, {"name", "trigger", "actions"}, "rule")
    name = rule.get("name")
    if not isinstance(name, str) or not name.strip() or len(name) > MAX_NAME:
        raise RuleError("name は1〜40文字の文字列")
    trig = rule.get("trigger")
    _only_keys(trig, {"type", "text", "ignore_case"}, "trigger")
    if trig.get("type") not in TRIGGER_TYPES:
        raise RuleError("trigger.type は contains のみ")
    ic = trig.get("ignore_case", True)
    if not isinstance(ic, bool):
        raise RuleError("ignore_case は真偽値")
    trigger = {"type": "contains", "text": _text(trig.get("text"), "trigger.text"), "ignore_case": ic}
    acts = rule.get("actions")
    if not isinstance(acts, list) or not 1 <= len(acts) <= MAX_ACTIONS:
        raise RuleError(f"actions は1〜{MAX_ACTIONS}個の配列")
    actions = []
    for a in acts:
        _only_keys(a, {"type", "text"}, "action")
        t = a.get("type")
        if t not in ACTION_TYPES:
            raise RuleError(f"未知の action: {t!r}")
        if t == "reply":
            actions.append({"type": "reply", "text": _text(a.get("text"), "action.text")})
        else:
            if "text" in a:
                raise RuleError("delete_message に text は付けない")
            actions.append({"type": t})
    return {"name": name.strip(), "trigger": trigger, "actions": actions}

def parse_ai_output(text):
    """AI の返答（JSON 文字列。```json 囲みは許す）を検査済みルールにする。"""
    s = text.strip()
    if s.startswith("```"):
        s = s.strip("`")
        if s.lower().startswith("json"):
            s = s[4:]
    try:
        data = json.loads(s)
    except json.JSONDecodeError as e:
        raise RuleError(f"JSON として読めない: {e.msg}")
    return validate_rule(data)

def describe(rule):
    """承認者に見せる平易な説明（コードではなく意味）。"""
    t = rule["trigger"]
    lines = [f"名前: {rule['name']}", f"条件: 発言に「{t['text']}」を含む"]
    for a in rule["actions"]:
        if a["type"] == "reply":
            lines.append(f"動作: 「{a['text']}」と返信")
        else:
            lines.append("動作: その発言を【削除】（注意）")
    return "\n".join(lines)

def match(rules, content):
    """内容に合うルールを返す。"""
    out = []
    for r in rules:
        t = r["trigger"]
        a, b = (t["text"].lower(), content.lower()) if t["ignore_case"] else (t["text"], content)
        if a in b:
            out.append(r)
    return out

class RuleStore:
    def __init__(self, path):
        self.path = path
        self.rules = []
        self.load()

    def load(self):
        if not os.path.exists(self.path):
            return
        with open(self.path, encoding="utf-8") as f:
            data = json.load(f)
        self.rules = [validate_rule(r) for r in data][:MAX_RULES]  # 手で壊したファイルも再検査

    def add(self, rule):
        rule = validate_rule(rule)
        if len(self.rules) >= MAX_RULES:
            raise RuleError(f"ルールは{MAX_RULES}個まで")
        self.rules = [r for r in self.rules if r["name"] != rule["name"]] + [rule]
        self._save()

    def _save(self):
        d = os.path.dirname(os.path.abspath(self.path))
        fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(self.rules, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)
