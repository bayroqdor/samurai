import unittest
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from aiogram.types import Chat, Message, User

from handlers import group_events
from libs.uztext.features import prepare
from services import cache, spam, uzspam
from services.spam import SpamVerdict, classify

UZ_SPAM = "Kredit kerakmi? Pasport bilan 15 daqiqada kartangizga pul, lichkaga yozing"
UZ_NORMAL = "Ertaga futbol bor, kim boradi? Soat oltida maktab stadionida"
RU_TEXT = "Привет всем, кто знает где починить телефон?"


class FeaturesTestCase(unittest.TestCase):
    def test_contacts_become_placeholders(self):
        text = prepare("Yozing @ishbor_admin yoki +998 90 123-45-67, t.me/kanal, 500 000 so'm")
        for token in ("mention", "phonenum", "tglink", "moneysum"):
            self.assertIn(token, text)

    def test_scripts_are_unified(self):
        self.assertEqual(prepare("Кредит керакми?"), prepare("Kredit kerakmi?"))


class ClassifyRoutingTestCase(unittest.TestCase):
    def test_uzbek_text_uses_uzbek_model_in_shadow_mode(self):
        with patch.object(spam, "predict") as ruspam:
            verdict = classify(UZ_SPAM)
        ruspam.assert_not_called()
        self.assertEqual(verdict.model, "uzspam")
        self.assertTrue(verdict.is_spam)
        self.assertTrue(verdict.shadow)

    def test_uzbek_normal_text_passes(self):
        verdict = classify(UZ_NORMAL)
        self.assertFalse(verdict.is_spam)
        self.assertLess(verdict.score, 0.5)

    def test_other_text_keeps_russian_model(self):
        with patch.object(spam, "predict", return_value=True) as ruspam:
            verdict = classify(RU_TEXT)
        ruspam.assert_called_once_with(RU_TEXT)
        self.assertEqual(verdict, SpamVerdict(True, "ruspam"))

    def test_russian_model_never_sees_uzbek_text_when_uz_model_is_off(self):
        with patch.object(spam.config.spam, "uz_model_mode", "off"), \
             patch.object(spam, "predict") as ruspam:
            verdict = classify(UZ_SPAM)
        ruspam.assert_not_called()
        self.assertFalse(verdict.is_spam)

    def test_enforce_mode_and_threshold_override(self):
        with patch.object(spam.config.spam, "uz_model_mode", "enforce"), \
             patch.object(spam.config.spam, "uz_model_threshold", 0.999):
            verdict = classify(UZ_SPAM)
        self.assertFalse(verdict.shadow)
        self.assertFalse(verdict.is_spam)

    def test_known_substrings_still_win(self):
        self.assertEqual(classify("Salom, bepul vpnbot bor").model, "substring")

    def test_model_artifact_is_loadable(self):
        self.assertIsNotNone(uzspam.spam_probability("salom"))
        self.assertGreaterEqual(uzspam.default_threshold(), 0.5)


class SpamHandlerTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        cache.clear_all_caches()
        self.addCleanup(cache.clear_all_caches)
        self.bot = AsyncMock()
        self.member = SimpleNamespace(id=1, user_id=123, reputation_points=0, messages_count=0)

    def message(self, text):
        return Message(
            message_id=10, date=datetime.now(UTC),
            chat=Chat(id=-100123, type="supergroup", title="Group"),
            from_user=User(id=123, is_bot=False, first_name="Alex"),
            text=text,
        ).as_(self.bot)

    async def run_with_verdict(self, verdict):
        role = SimpleNamespace(status="member")
        with patch.object(group_events, "retrieve_or_create_member", new=AsyncMock(return_value=self.member)), \
             patch.object(group_events, "retrieve_tgmember", new=AsyncMock(return_value=role)), \
             patch.object(group_events, "spam_classify", return_value=verdict), \
             patch.object(group_events, "_send_spam_review", new_callable=AsyncMock) as review, \
             patch.object(group_events, "_maybe_autoban", new_callable=AsyncMock), \
             patch.object(group_events, "check_for_unwanted", new=AsyncMock(return_value=False)), \
             patch.object(group_events, "queue_member_update", new_callable=AsyncMock) as updates, \
             patch.object(group_events.config.spam, "burst_enabled", False), \
             patch.object(Message, "delete", new_callable=AsyncMock) as delete:
            await group_events._process_user_message(self.message(UZ_SPAM), count_clean_message=True)
        return review, updates, delete

    async def test_shadow_verdict_is_reported_but_not_deleted(self):
        review, updates, delete = await self.run_with_verdict(SpamVerdict(True, "uzspam", 0.9, shadow=True))
        delete.assert_not_awaited()
        review.assert_awaited_once()
        self.assertFalse(review.await_args.kwargs["deleted"])
        # the user is not penalized while the model is on probation
        for call in updates.await_args_list:
            self.assertNotIn("violations_count_spam", call.kwargs)

    async def test_enforced_verdict_deletes_and_reports(self):
        review, updates, delete = await self.run_with_verdict(SpamVerdict(True, "uzspam", 0.9))
        delete.assert_awaited_once()
        review.assert_awaited_once()
        self.assertTrue(review.await_args.kwargs["deleted"])
        updates.assert_any_await(123, violations_count_spam=1, reputation_points=-5)

    async def test_clean_verdict_does_nothing(self):
        review, _, delete = await self.run_with_verdict(SpamVerdict(False, "uzspam", 0.1, shadow=True))
        delete.assert_not_awaited()
        review.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
