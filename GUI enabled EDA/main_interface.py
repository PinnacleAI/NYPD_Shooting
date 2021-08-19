
import sys
from PyQt5.QtWidgets import (
        QVBoxLayout, QFormLayout, QComboBox, QCheckBox, QSpacerItem, QGroupBox,
        QMainWindow, QSizePolicy, QLineEdit, QApplication, QWidget, QDockWidget,
        QRadioButton, QHBoxLayout, QMessageBox, QSlider, QScrollArea,
        QSplashScreen
)

from PyQt5.QtCore import Qt, QDateTime, QDate
from PyQt5.QtGui import QPainter, QFont, QColor, QPixmap, QIcon
from PyQt5.QtChart import (
    QChart, QChartView, QDateTimeAxis, QCategoryAxis, QBarCategoryAxis, QLineSeries, QValueAxis
)

import matplotlib as mpl


class MainInterface(QMainWindow):
    def __init__(self, parent=None):
        super(MainInterface, self).__init__(parent)

        appearance_groupBox = QGroupBox("Appearance:")

        self.theme_comboBox = QComboBox()
        spacer = QSpacerItem(15, 10, QSizePolicy.Fixed, QSizePolicy.Fixed)

        form_layout = QFormLayout()
        form_layout.addRow("Theme:", self.theme_comboBox)
        form_layout.addItem(spacer)

        form_layout.setVerticalSpacing(18)
        appearance_groupBox.setLayout(form_layout)

        plot_setting_groupBox = QGroupBox("Plot Settings:")

        self.plot_type_comboBox = QComboBox()
        items = ["None", "Bar plot", "Scatter plot", "Line plot", "Density plot"]
        self.plot_type_comboBox.addItems(items)

        self.xaxis_comboBox = QComboBox()
        self.yaxis_comboBox = QComboBox()

        self.horizontal_orientation_radioButton = QRadioButton("Horizontal Bar")
        self.vertical_orientation_radioButton = QRadioButton("Vertical Bar")

        # set vertical bar orientation as the default option
        self.vertical_orientation_radioButton.setChecked(True)

        self.radio_group = QGroupBox("Bar orientation")
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.horizontal_orientation_radioButton)
        radio_layout.addWidget(self.vertical_orientation_radioButton)

        self.radio_group.setLayout(radio_layout)
        self.radio_group.setHidden(True)

        self.set_scatter_transparency = QSlider(Qt.Horizontal)
        self.set_scatter_transparency.setRange(0, 10)
        self.set_scatter_transparency.setSingleStep(1)
        self.set_scatter_transparency.setPageStep(1)
        self.set_scatter_transparency.setValue(10)

        self.shade_plot = QCheckBox("")

        self.slider_group = QGroupBox("Scatter plot setting")
        slider_layout = QFormLayout()
        slider_layout.addRow("alpha:", self.set_scatter_transparency)
        slider_layout.addRow("shade:", self.shade_plot)

        self.slider_group.setLayout(slider_layout)
        self.slider_group.setHidden(True)

        self.group_by_comboBox = QComboBox()

        self.xaxis_date_settings_group = QGroupBox("Date Settings (x axis):")
        self.xaxis_date_settings_group.setHidden(True)

        self.xaxis_daily_setting = QRadioButton('Daily')
        self.xaxis_monthly_setting = QRadioButton("Monthly")
        self.xaxis_yearly_setting = QRadioButton("Yearly")

        self.xaxis_yearly_setting.setChecked(True)

        v_box_layout = QVBoxLayout()
        v_box_layout.addWidget(self.xaxis_daily_setting)
        v_box_layout.addWidget(self.xaxis_monthly_setting)
        v_box_layout.addWidget(self.xaxis_yearly_setting)

        self.xaxis_date_settings_group.setLayout(v_box_layout)

        self.yaxis_date_settings_group = QGroupBox("Date Settings (y axis):")
        self.yaxis_date_settings_group.setHidden(True)

        self.yaxis_daily_setting = QRadioButton('Daily')
        self.yaxis_monthly_setting = QRadioButton("Monthly")
        self.yaxis_yearly_setting = QRadioButton("Yearly")

        self.yaxis_yearly_setting.setChecked(True)

        v_box_layout = QVBoxLayout()
        v_box_layout.addWidget(self.yaxis_daily_setting)
        v_box_layout.addWidget(self.yaxis_monthly_setting)
        v_box_layout.addWidget(self.yaxis_yearly_setting)

        self.yaxis_date_settings_group.setLayout(v_box_layout)

        self.group_by_date_settings_group = QGroupBox("Date Settings")
        self.group_by_date_settings_group.setHidden(True)

        self.group_by_daily_setting = QRadioButton("Daily")
        self.group_by_monthly_setting = QRadioButton("Monthly")
        self.group_by_yearly_setting = QRadioButton("Yearly")

        self.group_by_yearly_setting.setChecked(True)

        v_box_layout = QVBoxLayout()
        v_box_layout.addWidget(self.group_by_daily_setting)
        v_box_layout.addWidget(self.group_by_monthly_setting)
        v_box_layout.addWidget(self.group_by_yearly_setting)

        self.group_by_date_settings_group.setLayout(v_box_layout)

        form_layout = QFormLayout()
        form_layout.addRow("Plot type:", self.plot_type_comboBox)
        form_layout.addWidget(self.radio_group)
        form_layout.addWidget(self.slider_group)
        form_layout.addRow("X axis:", self.xaxis_comboBox)
        form_layout.addWidget(self.xaxis_date_settings_group)
        form_layout.addRow("Y axis:", self.yaxis_comboBox)
        form_layout.addWidget(self.yaxis_date_settings_group)
        form_layout.addRow("Group by:", self.group_by_comboBox)
        form_layout.addWidget(self.group_by_date_settings_group)

        form_layout.setVerticalSpacing(18)
        plot_setting_groupBox.setLayout(form_layout)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(appearance_groupBox)

        spacer = QSpacerItem(15, 14, QSizePolicy.Fixed, QSizePolicy.Fixed)
        vertical_layout.addItem(spacer)

        vertical_layout.addWidget(plot_setting_groupBox)

        spacer = QSpacerItem(15, 10, QSizePolicy.Fixed, QSizePolicy.Expanding)
        vertical_layout.addItem(spacer)

        scroll_widget_contents = QWidget()
        scroll_widget_contents.setLayout(vertical_layout)

        widget = QScrollArea()
        widget.setWidgetResizable(True)
        widget.setWidget(scroll_widget_contents)

        dock_widget = QDockWidget("Settings")
        dock_widget.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

        dock_widget.setWidget(widget)

        dock_widget.setFixedWidth(300)

        menu_bar = self.menuBar()
        view_menu = menu_bar.addMenu("View")
        toggle_dock_action = dock_widget.toggleViewAction()
        view_menu.addAction(toggle_dock_action)

        self.setup_chart()
        self.initialize_ui()

    def set_chart_customization(self):
        font = QFont("Tahoma", 20)
        self.chart.setTitleFont(font)

        self.red_color = QColor("red")
        self.chart.setTitleBrush(self.red_color)

    def setup_chart(self):
        """Set up the GUI's chart instances"""
        self.chart = QChart()

        self.chart.setTitle("NYPD Shooting Data 2006 - 2020")

        min_ = QDateTime(QDate(2006, 1, 1))
        max_ = QDateTime(QDate(2020, 12, 31))
        self.axis_x = QDateTimeAxis()
        self.axis_x.setLabelsEditable(False)
        self.axis_x.setFormat("yyyy")

        self.axis_x.setRange(min_, max_)
        self.axis_x.setTickCount(15)
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)

        self.axis_y = QValueAxis()
        self.axis_y.setLabelFormat("%i")
        self.axis_y.setTickCount(10)
        self.axis_y.setRange(0, 10)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)

        self.set_chart_customization()

        # create QChartView object for displaying the chart
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.HighQualityAntialiasing)
        self.chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.connect_slots()
        self.setCentralWidget(self.chart_view)

        self.auto_change_style_comboBox()

    def connect_slots(self):
        """Connect the slots to their appropriate signals"""
        self.theme_comboBox.currentIndexChanged.connect(self.change_chart_theme)

    def initialize_ui(self):
        """Initialize the window and display its contents."""
        self.setMinimumSize(900, 700)
        self.showMaximized()
        self.setWindowTitle("NYPD Shootings")

    def setup_menu(self):
        """Create a simple menu to manage the dock widget."""
        pass

    def change_chart_animation(self):
        """Slot for changing the animation of the chart."""
        animation = self.animation_dict[self.animation_comboBox.currentText()]
        animation_options = self.chart.AnimationOptions(animation)
        self.chart.setAnimationOptions(animation_options)

    def change_chart_legend(self):
        """Slot for changing the position of the chart legend."""
        legend_alignment = self.legend_comboBox.currentText()
        if legend_alignment == "No Legend":
            self.chart.legend().hide()
        else:
            self.chart.legend().setAlignment(self.legend_dict[legend_alignment])
            self.chart.legend().show()

    def toggle_antialiasing(self, state):
        """if toggle the chart anti aliasing feature"""
        if state:
            self.chart_view.setRenderHint(QPainter.Antialiasing, on=True)
        else:
            self.chart_view.setRenderHint(QPainter.Antialiasing, on=False)

    def change_chart_label_title(self, label: str):
        if label == "title":
            title = self.title_lineEdit.text()
            try:
                self.chart.setTitle(title)
            except RuntimeError:
                self.chart = QChart()
                self.chart.setTitle(title)
        elif label == "x_label":
            x_label = self.xlabel_lineEdit.text()
            self.axis_x.setTitleText(x_label)
        elif label == "y_label":
            y_label = self.ylabel_lineEdit.text()
            self.axis_y.setTitleText(y_label)

    def setup_mpl_theme(self):
        style_list = [style for style in mpl.style.available if "_" not in style]
        self.theme_comboBox.clear()
        self.theme_comboBox.addItems(style_list)

    def setup_qchart_theme(self):
        # set the values for the theme combobox
        self.themes_dict = {
            "Qt": self.chart.ChartThemeQt, "Dark": self.chart.ChartThemeDark,
            "Light": self.chart.ChartThemeLight, "NCS Blue": self.chart.ChartThemeBlueNcs,
            "Cerulean Blue": self.chart.ChartThemeBlueCerulean,
            "Icy Blue": self.chart.ChartThemeBlueIcy,
            "Brown Sand": self.chart.ChartThemeBrownSand,
            "Hight Contrast": self.chart.ChartThemeHighContrast
        }
        self.theme_comboBox.clear()
        self.theme_comboBox.addItems(self.themes_dict.keys())

    def auto_change_style_comboBox(self, style_class="QChart"):
        if style_class == "mpl":
            self.setup_mpl_theme()
        elif style_class == "QChart":
            self.setup_qchart_theme()
