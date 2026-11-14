from flow_state import i18n


def test_all_languages_load():
    assert len(i18n.LANGUAGES) >= 12
    assert "ar" in i18n.RTL and "en" not in i18n.RTL


def test_repeated_switching_never_stacks():
    for code in ("en", "fr", "de", "ja", "ar", "ko"):
        i18n.set_language(code)
        text = i18n.translate_text("▶ " + i18n.tr("ابدأ"))
        assert text == "▶ " + i18n.tr("ابدأ")
    i18n.set_language("ar")


def test_every_language_pack_is_well_formed():
    for code, pack in i18n.PACKS.items():
        assert pack.CODE == code
        assert isinstance(pack.MESSAGES, dict)
        assert pack.QT_LOCALE


def test_report_missing_translations(capsys):
    """Not a failure: prints which English keys each language still lacks."""
    english = set(i18n.PACKS["en"].MESSAGES.values())
    for code, pack in i18n.PACKS.items():
        if code in ("ar", "en"):
            continue
        missing = english - set(pack.MESSAGES)
        print(f"{code}: {len(missing)} missing (fall back to English)")
