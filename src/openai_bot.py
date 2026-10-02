import openai
import rules

SYSTEM_PROMPT = """あなたはDiscord botのルール作成係です。コードは書かないでください。
依頼を、次のJSONオブジェクト1つだけで返してください（説明文なし）。
{"name": "短い名前", "trigger": {"type": "contains", "text": "含む言葉", "ignore_case": true},
 "actions": [{"type": "reply", "text": "返信文"}, {"type": "delete_message"}]}
使えるtriggerはcontainsのみ。使えるactionはreply（text必須）とdelete_message（textなし）のみ。
actionは最大3個。これで表せない依頼には {"error": "理由"} を返してください。"""

class RuleMaker:
    def __init__(self, cfg, client=None):
        self.model = cfg.openai_model
        self.client = client or openai.OpenAI(api_key=cfg.openai_api_key,
                                              organization=cfg.openai_org)

    def make(self, request_text):
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": request_text[:1000]}],
        )
        text = resp.choices[0].message.content or ""
        if '"error"' in text and '"trigger"' not in text:
            raise rules.RuleError("AI がこの依頼は部品で表せないと返しました")
        return rules.parse_ai_output(text)
