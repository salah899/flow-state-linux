from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QSplitter, QVBoxLayout, QWidget

from flow_state.i18n import tr, translate_tree
from flow_state.ui.formatting import WEEKDAYS, format_minutes
from flow_state.ui.theme import ACCENTS
from flow_state.ui.widgets.charts import DonutChart, StatCard, WeeklyChart


class AnalyticsPage(QWidget):
    def __init__(self, services):
        super().__init__()
        self.analytics = services.analytics
        self.weekly_mode = "tasks"
        self.donut_mode = "tasks"
        lay = QVBoxLayout(self)
        title = QLabel("الإحصائيات والتحليلات")
        title.setObjectName("brand")
        lay.addWidget(title)

        self.total = StatCard("إجمالي المهام", ACCENTS["blue"])
        self.done = StatCard("المهام المنجزة", ACCENTS["green"])
        self.overdue = StatCard("المهام المتأخرة", ACCENTS["red"])
        self.rate = StatCard("معدل الإنجاز", ACCENTS["orange"])
        lay.addLayout(self._row(self.total, self.done, self.overdue, self.rate))
        self.total_time = StatCard("إجمالي الوقت", ACCENTS["blue"])
        self.elapsed_time = StatCard("الوقت المنقضي", ACCENTS["green"])
        self.remaining_time = StatCard("الوقت المتبقي", ACCENTS["orange"])
        self.time_rate = StatCard("معدل الوقت", ACCENTS["primary"])
        lay.addLayout(self._row(self.total_time, self.elapsed_time, self.remaining_time, self.time_rate))

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        weekly_card, self.weekly_toggle, self.weekly = self._chart_card(WeeklyChart(), self.toggle_weekly)
        donut_card, self.donut_toggle, self.donut = self._chart_card(DonutChart(), self.toggle_donut)
        self.splitter.addWidget(weekly_card)
        self.splitter.addWidget(donut_card)
        self.splitter.setSizes([700, 350])
        lay.addWidget(self.splitter, 1)
        self.refresh()

    @staticmethod
    def _row(*cards):
        grid = QGridLayout()
        for i, card in enumerate(cards):
            grid.addWidget(card, 0, i)
        return grid

    @staticmethod
    def _chart_card(chart, on_toggle):
        card = QFrame()
        card.setObjectName("card")
        lay = QVBoxLayout(card)
        toggle = QPushButton()
        toggle.setObjectName("nav")
        toggle.clicked.connect(on_toggle)
        lay.addWidget(toggle)
        lay.addWidget(chart)
        return card, toggle, chart

    def toggle_weekly(self):
        self.weekly_mode = "time" if self.weekly_mode == "tasks" else "tasks"
        self.refresh()

    def toggle_donut(self):
        self.donut_mode = "time" if self.donut_mode == "tasks" else "tasks"
        self.refresh()

    def refresh(self):
        s = self.analytics.summary()
        counts = self.analytics.counts()
        self.total.value.setText(str(s["total_tasks"]))
        self.done.value.setText(str(s["done_tasks"]))
        self.overdue.value.setText(str(counts["overdue"]))
        self.rate.value.setText(f"{s['task_rate']}%")
        self.total_time.value.setText(format_minutes(s["total_minutes"], short=True))
        self.elapsed_time.value.setText(format_minutes(s["elapsed_minutes"], short=True))
        self.remaining_time.value.setText(format_minutes(s["remaining_minutes"], short=True))
        self.time_rate.value.setText(f"{s['time_rate']}%")

        days = self.analytics.weekly()
        labels = [tr(WEEKDAYS[d["weekday"]]) for d in days]
        if self.weekly_mode == "tasks":
            self.weekly_toggle.setText("▼ المهام المكتملة")
            self.weekly.set_data([d["completed_tasks"] for d in days], labels, "", ACCENTS["primary"])
        else:
            self.weekly_toggle.setText("▲ وقت التركيز")
            self.weekly.set_data([d["focus_minutes"] for d in days], labels, tr("د"), ACCENTS["green"])
        if self.donut_mode == "tasks":
            self.donut_toggle.setText("▼ إنجاز المهام")
            self.donut.set_data(s["task_rate"], tr("إنجاز المهام"), ACCENTS["green"])
        else:
            self.donut_toggle.setText("▲ الوقت المنقضي")
            self.donut.set_data(s["time_rate"], tr("الوقت المنقضي"), ACCENTS["primary"])
        translate_tree(self)

    # layout persistence
    def set_layout_editing(self, enabled):
        self.splitter.setHandleWidth(9 if enabled else 2)

    def layout_sizes(self):
        return self.splitter.sizes()

    def apply_layout_sizes(self, sizes):
        if sizes and len(sizes) == 2:
            self.splitter.setSizes(sizes)
