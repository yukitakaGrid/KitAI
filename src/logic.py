"""bot の判断部分。Discord に依存しない（試験できる）。返すのは「やること」のリスト。"""
import approval
import rules

def handle(msg, state, cfg, store, maker):
    """msg: dict(author_id, role_ids, channel_id, content, mentioned, is_bot)
    戻り: [("send", text) | ("delete",)]"""
    if msg["is_bot"]:
        return []
    out = []
    content = msg["content"]
    # 1) 保留中の承認
    verdict, rule = state["pending"].decide(msg["channel_id"], content,
                                            msg["author_id"], msg["role_ids"], cfg)
    if verdict == "approved":
        try:
            store.add(rule)
        except rules.RuleError as e:
            return [("send", f"登録できません: {e}")]
        return [("send", f"登録しました: {rule['name']}")]
    if verdict == "rejected":
        return [("send", "破棄しました。")]
    if verdict == "denied":
        return [("send", "承認できるのは決められた承認者だけです。")]
    # 2) モード切替・一覧・依頼（メンション必須。承認者のみ）
    if msg["mentioned"]:
        is_ok = approval.is_approver(msg["author_id"], msg["role_ids"], cfg)
        if "!edit" in content or "!command" in content or "!display" in content:
            if not is_ok:
                return [("send", "それは承認者だけの操作です。")]
            if "!display" in content:
                names = "\n".join(r["name"] for r in store.rules) or "(なし)"
                return [("send", f"登録済みルール:\n{names}")]
            state["edit"] = "!edit" in content
            return [("send", "edit mode" if state["edit"] else "command mode")]
        if state["edit"]:
            if not is_ok:
                return [("send", "ルールの追加は承認者だけです。")]
            ai_limit = state.get("ai_limiter")
            if ai_limit and not ai_limit.allow(msg["author_id"]):
                return [("send", "AI への依頼が多すぎます。少し待ってください。")]
            try:
                rule = maker.make(content)
            except Exception as e:  # AI・検査どちらの失敗も、詳細は出さず知らせる
                kind = str(e) if isinstance(e, rules.RuleError) else "AI への依頼に失敗しました"
                return [("send", f"作れませんでした: {kind}")]
            state["pending"].put(msg["channel_id"], msg["author_id"], rule)
            return [("send", "次のルールを登録していい？ Yes / No（5分有効）\n```\n"
                             + rules.describe(rule) + "\n```")]
    # 3) 登録済みルールの実行（bot 自身の発言は上で除外済み）
    matched = rules.match(store.rules, content)
    rule_limit = state.get("rule_limiter")
    if matched and rule_limit and not rule_limit.allow(msg["channel_id"]):
        return []  # 連発防止：制限中は黙って何もしない（案内の返信も連発になるため）
    for r in matched:
        for a in r["actions"]:
            out.append(("send", a["text"]) if a["type"] == "reply" else ("delete",))
    return out
