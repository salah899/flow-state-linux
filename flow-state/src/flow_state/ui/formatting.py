"""Display helpers shared by all pages (dates, durations, sessions, priority)."""
from PySide6.QtCore import QDateTime, QLocale, Qt

from flow_state.i18n import qt_locale_name, tr

PRIORITY_LABELS = {2: "عالية", 1: "متوسطة", 0: "منخفضة", -1: "غير محددة"}
PRIORITY_CHOICES = [("غير محددة", -1), ("منخفضة", 0), ("متوسطة", 1), ("عالية", 2)]
WEEKDAYS = ["أحد", "اثنين", "ثلاثاء", "أربعاء", "خميس", "جمعة", "سبت"]  # Sunday = 0


def current_locale():
    return QLocale(qt_locale_name())


def locale_date_pattern():
    return current_locale().dateFormat(QLocale.ShortFormat)


def priority_label(value):
    return PRIORITY_LABELS.get(value, "غير محددة")


def format_minutes(value, short=False):
    value = max(0, round(float(value or 0)))
    hours, minutes = divmod(value, 60)
    if short:
        if hours and minutes:
            return f"{hours} س {minutes} د"
        return f"{hours} ساعة" if hours else f"{minutes} دقيقة"
    if hours and minutes:
        return f"{hours} ساعة و{minutes} دقيقة"
    return f"{hours} ساعة" if hours else f"{minutes} دقيقة"


def format_hms(seconds):
    hours, rest = divmod(max(0, int(seconds)), 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_sessions(task):
    done = float(task["completed_sessions"] or 0)
    done_text = f"{done:.2f}" if done % 1 else str(int(done))
    estimated = task["estimated_sessions"]
    return f"{done_text} / {int(estimated)} 🍅" if estimated is not None else f"{done_text} 🍅"


def format_range(task):
    start = task["start_at"] or task["due_at"]
    end = task["end_at"] or task["due_at"]
    if not end:
        return tr("بدون مدة")
    sd = QDateTime.fromString(start, Qt.ISODate)
    ed = QDateTime.fromString(end, Qt.ISODate)
    loc = current_locale()
    return f"{loc.toString(sd.date(), QLocale.ShortFormat)} ← {loc.toString(ed.date(), QLocale.ShortFormat)}"
