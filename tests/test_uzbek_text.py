import unittest
from unittest.mock import patch

from libs.uztext import langdetect, normalize
from libs.uztext import profanity as uz
from services.profanity import (
    check_for_profanity,
    check_for_profanity_all,
    check_name_for_violations,
    find_profanity,
    languages_for,
)


class NormalizeTestCase(unittest.TestCase):
    def test_both_scripts_and_apostrophes_meet(self):
        latin = normalize.to_latin("Ўзбекистон ғалаба")
        self.assertEqual(latin, "o'zbekiston g'alaba")
        for variant in ("O‘zbekiston", "Oʻzbekiston", "O`zbekiston", "O’zbekiston"):
            self.assertEqual(normalize.to_latin(variant), "o'zbekiston")

    def test_ye_rule(self):
        self.assertEqual(normalize.to_latin("ер сен"), "yer sen")

    def test_fold_removes_evasions(self):
        self.assertEqual(normalize.fold("s1kay"), "sikay")
        self.assertEqual(normalize.fold("jalaaaab"), "jalab")
        # real double letters survive
        self.assertEqual(normalize.fold("sikka jallab"), "sikka jallab")

    def test_numbers_are_not_leet(self):
        self.assertEqual(normalize.fold("23-bandiga 5ta 100"), "23-bandiga 5ta 100")

    def test_fold_keeps_source_offsets(self):
        text = "Ўғил"
        mapped = normalize.fold_mapped(text)
        self.assertEqual(mapped.text, "ogil")
        self.assertEqual(mapped.source_span(0, len(mapped.text)), (0, 4))

    def test_spelled_out_words_are_rebuilt(self):
        words = {c.word for c in normalize.candidates(normalize.fold("va s i k a y"))}
        self.assertIn("sikay", words)
        words = {c.word for c in normalize.candidates(normalize.fold("j.a.l.a.b"))}
        self.assertIn("jalab", words)


class UzbekProfanityTestCase(unittest.TestCase):
    OBSCENE = (
        "onangni sikay", "сикаман", "s1kay", "s i k a y", "j.a.l.a.b",
        "jalaaaab", "qo'toq", "кўтоқ", "ko'tingga", "қанжиқ", "далбаёб",
        "dalbayob", "qahba", "siktir", "ja la b",
        # Russian mat in both scripts
        "nahuy", "блядь", "pizdec", "zaebal", "сука",
    )
    CLEAN = (
        "Assalomu alaykum", "Нонни еб қўйдим", "yeb qo'ydim", "sikl", "sikka",
        "siqildim", "сикилдим", "Sikandar", "ko'taring", "кўтаринг", "muddat",
        "муддати", "hujjat", "hujum", "qotib qoldi", "kotlet", "skidka", "skype",
        "Amin aka", "amaki", "jalb qilish", "huquq", "jalapeno", "debat",
        "pedagog", "fuqaro", "фукаро", "23-bandiga asosan", "skeyt",
    )

    def test_obscene_words_are_found(self):
        for text in self.OBSCENE:
            with self.subTest(text=text):
                self.assertIsNotNone(uz.find(text))

    def test_everyday_words_are_clean(self):
        for text in self.CLEAN:
            with self.subTest(text=text):
                self.assertIsNone(uz.find(text))

    def test_match_points_at_original_text(self):
        text = "bu ja.la.b ekan"
        match = uz.find(text)
        self.assertEqual(text[match.start:match.end], "ja.la.b")

    def test_allowlist_and_blocklist(self):
        self.assertIsNone(uz.find("jalab", allowlist=["жалаб"]))
        self.assertIsNotNone(uz.find("сўкинишлар", blocklist=["so'kinish"]))


class RoutingTestCase(unittest.TestCase):
    def test_language_detection(self):
        self.assertTrue(langdetect.is_uzbek("Salom, qayerdasan? Bugun kelasanmi?"))
        self.assertTrue(langdetect.is_uzbek("Бугун кечқурун кўришамизми?"))
        self.assertFalse(langdetect.is_uzbek("Привет, как дела?"))
        self.assertFalse(langdetect.is_uzbek("what the hell is this"))

    def test_uzbek_text_skips_ru_en_regexes(self):
        self.assertEqual(languages_for("Jizzaxda yangi universitet ochildi, bu juda yaxshi"), ("uz",))
        self.assertEqual(set(languages_for("Привет всем")), {"uz", "ru", "en"})

    def test_uzbek_words_no_longer_trip_ru_en(self):
        for text in (
            "Jizzax viloyati", "Dildora opa", "Бўлгандан кейин гаплашамиз",
            "Мудофаа вазирлиги", "Kuzgacha ishni tugatish kerak.",
        ):
            with self.subTest(text=text):
                self.assertEqual(check_for_profanity_all(text), (False, None))

    def test_mixed_chat_still_catches_mat(self):
        self.assertTrue(check_for_profanity_all("Сен нима деяпсан, нахуй")[0])
        self.assertTrue(check_for_profanity_all("иди нахуй")[0])
        self.assertTrue(check_for_profanity_all("бляяя че ты несешь")[0])
        self.assertTrue(check_for_profanity_all("fuck you")[0])

    def test_uz_language_in_service_api(self):
        result = check_for_profanity("bu dalbayob", "uz")
        self.assertTrue(result.detected)
        self.assertEqual(result.word, "dalbayob")

        match = find_profanity("Salom, s1kay")[0]
        self.assertEqual(match.language, "uz")
        self.assertEqual(match.text, "s1kay")

    def test_routing_can_be_disabled(self):
        with patch("services.profanity.config.profanity.uzbek_routing", False):
            self.assertEqual(set(languages_for("Bugun juda yaxshi kun")), {"uz", "ru", "en"})


class UzbekNamesTestCase(unittest.TestCase):
    def test_common_names_are_clean(self):
        for name in ("Dildora", "Sikandar", "Shohruh", "Muyassar", "Шоҳруҳ", "Ҳусан"):
            with self.subTest(name=name):
                self.assertTrue(check_name_for_violations(name))

    def test_uzbek_bait_names(self):
        for name in ("Интим 18+", "Lichkaga yoz", "Yalang'och qizlar", "Profilimga kir"):
            with self.subTest(name=name):
                self.assertFalse(check_name_for_violations(name))


if __name__ == "__main__":
    unittest.main()
