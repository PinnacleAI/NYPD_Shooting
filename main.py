
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

from main_interface import *
from utilities import change_axis, change_cursor


class CreateCanvas(FigureCanvasQTAgg):
    def __init__(self, nrow=1, ncol=1):
        # create Matplotlib Figure object
        figure = Figure(dpi=100, tight_layout=True)
        
        # reserve width and height space for subplots
        figure.subplots_adjust(wspace=.3, hspace=.4)
        
        # create the axes and set the number of rows/ columns for the subplots(s)
        self.axes = figure.subplots(nrow, ncol)
        super(CreateCanvas, self).__init__(figure)


class ControlCenter(MainInterface):
    def __init__(self, parent=None):
        super(ControlCenter, self).__init__(parent)
        self.load_dataset_to_memory()

        # default values
        self.tool_bar = None
        self.categorical_columns = [
            "BORO", "PRECINCT", "JURISDICTION_CODE", "LOCATION_DESC", "STATISTICAL_MURDER_FLAG",
            "PERP_AGE_GROUP", "PERP_SEX", "PERP_RACE", "VIC_AGE_GROUP", "VIC_SEX", "VIC_RACE",
            "OCCUR_DATE_OCCUR_TIME"
        ]
        self.numerical_columns = ["Latitude", "Longitude", "OCCUR_DATE_OCCUR_TIME"]

        self.previous_xaxis_index = 0
        self.previous_yaxis_index = 0

    def load_dataset_to_memory(self):
        self.data = pd.read_csv("NYPD_Shooting.csv", parse_dates=[["OCCUR_DATE", "OCCUR_TIME"]])

        # optimizing tables and remove redundant columns
        self.data = self.data.drop(['Lon_Lat', "X_COORD_CD", "Y_COORD_CD", "INCIDENT_KEY"], axis=1)

        categorical_columns = ['BORO', 'PRECINCT', 'JURISDICTION_CODE', 'LOCATION_DESC', 'PERP_AGE_GROUP', 'PERP_SEX',
                               'PERP_RACE', 'VIC_AGE_GROUP', 'VIC_SEX', 'VIC_RACE']

        self.data[categorical_columns] = self.data[categorical_columns].astype('category')
        self.data = self.data.set_index("OCCUR_DATE_OCCUR_TIME", drop=False)

        # order the age group categories
        self.data['PERP_AGE_GROUP'].cat.reorder_categories(['<18', '18-24', '25-44', '45-64', '65+',
                                                            'UNKNOWN', '224', '940', '1020'],
                                                           ordered=True, inplace=True)
        self.data['VIC_AGE_GROUP'].cat.reorder_categories(['<18', '18-24', '25-44', '45-64', '65+',
                                                           'UNKNOWN'], ordered=True, inplace=True)
        data_columns = ["None", *self.data.columns]
        self.yaxis_comboBox.addItems(data_columns)
        self.xaxis_comboBox.addItems(data_columns)
        self.group_by_comboBox.addItems(data_columns)

    def connect_slots(self):
        super(ControlCenter, self).connect_slots()
        self.plot_type_comboBox.currentTextChanged.connect(self.change_plot_type)
        self.xaxis_comboBox.currentTextChanged.connect(lambda: self.slot_manager('x'))
        self.yaxis_comboBox.currentTextChanged.connect(lambda: self.slot_manager('y'))
        self.vertical_orientation_radioButton.clicked.connect(self.change_bar_plot_orientation)
        self.horizontal_orientation_radioButton.clicked.connect(self.change_bar_plot_orientation)
        self.set_scatter_transparency.valueChanged.connect(self.change_scatter_chart_transparency)
        self.shade_plot.clicked.connect(self.change_scatter_chart_shade)

        self.xaxis_yearly_setting.clicked.connect(lambda: self.slot_manager('x'))
        self.xaxis_monthly_setting.clicked.connect(lambda: self.slot_manager('x'))
        self.xaxis_daily_setting.clicked.connect(lambda: self.slot_manager('x'))

        self.yaxis_yearly_setting.clicked.connect(lambda: self.slot_manager('y'))
        self.yaxis_monthly_setting.clicked.connect(lambda: self.slot_manager('y'))
        self.yaxis_daily_setting.clicked.connect(lambda: self.slot_manager('y'))

    def slot_manager(self, axis):
        if self.plot_type_comboBox.currentText() == "None":
            if axis == "x":
                self.change_xaxis()
            else:
                self.change_yaxis()
        else:
            if axis == "x":
                self.change_xaxis_date_setting()
            else:
                self.change_yaxis_date_setting()
            self.plot_data(axis)

    def change_xaxis(self):
        """Change the x-axis scale of the initial empty chart to mimic the underlying data."""
        axis_label = self.xaxis_comboBox.currentText()
        if axis_label == 'None':
            # set the axis_label to the default axis
            pass
        else:
            values = self.data[axis_label]
            self.axis_x = change_axis(axis_label, values)
            self.chart.setAxisX(self.axis_x)

    def change_yaxis(self):
        """Change the y-axis scale of the initial empty chart to mimic the underlying data."""
        axis_label = self.yaxis_comboBox.currentText()
        if axis_label == 'None':
            pass
        else:
            values = self.data[axis_label]
            self.axis_y = change_axis(axis_label, values, axe="y")
            self.chart.setAxisY(self.axis_y)

    def change_qchart_theme(self):
        """Slot for changing the theme of the chart"""
        theme = self.theme_comboBox.currentText()
        if theme.strip():
            theme = self.themes_dict[self.theme_comboBox.currentText()]
            try:
                self.chart.setTheme(theme)
            except RuntimeError:
                self.chart = QChart()
                self.chart.setTheme(theme)
            self.set_chart_customization()

    def change_mpl_chart_theme(self):
        theme = self.theme_comboBox.currentText()
        if theme.strip():
            mpl.style.use(theme)
            self.plot_data()

    def change_chart_theme(self):
        condition = (
            self.plot_type_comboBox.currentText() == "None"
            or self.plot_type_comboBox.currentText() == "Line plot"
        )
        if condition:
            self.change_qchart_theme()
        else:
            self.change_mpl_chart_theme()

    def change_plot_type(self):
        """Display the necessary sub setting display appropriate for each plot type.
        It also updates the theme comboBox"""
        if self.plot_type_comboBox.currentText() == 'Bar plot':
            self.radio_group.setHidden(False)
            self.slider_group.setHidden(True)
            self.change_bar_plot_orientation()

            self.auto_change_style_comboBox("mpl")
            return

        elif self.plot_type_comboBox.currentText() == "Scatter plot":
            self.radio_group.setHidden(True)
            self.slider_group.setHidden(False)

            self.auto_change_style_comboBox("mpl")

        elif self.plot_type_comboBox.currentText() == "Line plot":
            self.radio_group.setHidden(True)
            self.slider_group.setHidden(True)

            self.auto_change_style_comboBox()

        elif self.plot_type_comboBox.currentText() == "Density plot":
            self.radio_group.setHidden(True)
            self.slider_group.setHidden(True)

            self.auto_change_style_comboBox("mpl")

        elif self.plot_type_comboBox.currentText() == "None":
            self.auto_change_style_comboBox()

        self.xaxis_comboBox.setDisabled(False)
        self.yaxis_comboBox.setDisabled(False)

    def change_bar_plot_orientation(self):
        if self.vertical_orientation_radioButton.isChecked():
            self.yaxis_comboBox.setDisabled(True)
            self.xaxis_comboBox.setDisabled(False)
        else:
            self.yaxis_comboBox.setDisabled(False)
            self.xaxis_comboBox.setDisabled(True)

    def change_xaxis_date_setting(self):
        plot_type = self.plot_type_comboBox.currentText()
        xaxis = self.xaxis_comboBox.currentText()
        is_enabled = self.xaxis_comboBox.isEnabled()
        if xaxis == "OCCUR_DATE_OCCUR_TIME" and is_enabled:
            self.xaxis_date_settings_group.setHidden(False)
            if plot_type == "Bar plot":
                # set the visibility of the yaxis_date_setting to False
                # only if the plot type is a bar plot
                self.yaxis_date_settings_group.setHidden(True)
                return
        else:
            if plot_type == "Bar plot":
                self.yaxis_date_settings_group.setHidden(True)
            self.xaxis_date_settings_group.setHidden(True)

    def change_yaxis_date_setting(self):
        plot_type = self.plot_type_comboBox.currentText()
        yaxis = self.yaxis_comboBox.currentText()
        is_enabled = self.yaxis_comboBox.isEnabled()
        if yaxis == "OCCUR_DATE_OCCUR_TIME" and is_enabled:
            self.yaxis_date_settings_group.setHidden(False)
            if plot_type == "Bar plot":
                # set the visibility of the xaxis_date_setting to False
                # only if the plot type is a bar plot
                self.xaxis_date_settings_group.setHidden(True)
                return
        else:
            if plot_type == "Bar plot":
                self.xaxis_date_settings_group.setHidden(True)
            self.yaxis_date_settings_group.setHidden(True)

    def plot_vertical_bar_chart(self):
        tick_labels = None
        if self.plot_type_comboBox.currentText() == "Bar plot":

            # prepare the data
            column = self.xaxis_comboBox.currentText()

            if column == "None":
                return

            # check if the data columns are categorical else raised error
            if column not in self.categorical_columns:
                message = "This feature data are continuous values and not categorical do you" \
                          "you still want to continue?"
                permission = QMessageBox().information(self, "Invalid data", message,
                                                       QMessageBox.Ok | QMessageBox.Discard)

                if permission == QMessageBox.Discard:
                    self.xaxis_comboBox.setCurrentIndex(self.previous_xaxis_index)
                    return

            data = self.data[column].value_counts()
            # if the column data have intrinsic order, sort by that order
            # rather than the default count order
            if column in ["PERP_AGE_GROUP", "VIC_AGE_GROUP"]:
                data = data.sort_index()

            elif column in ["OCCUR_DATE_OCCUR_TIME"]:
                # if the column feature is the datetime feature plot the chart
                # as specified by the time frequency chosen by the user
                if self.xaxis_daily_setting.isChecked():
                    tick_labels = ["Mon", "Tue", "Wed", "Thurs", "Fri", "Sat", "Sun"]
                    data = self.data.index.isocalendar().day.value_counts().sort_index()
                elif self.xaxis_monthly_setting.isChecked():
                    tick_labels = [
                        "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct",
                        "Nov", "Dec"
                    ]
                    data = self.data.index.month.value_counts().sort_index()
                elif self.xaxis_yearly_setting.isChecked():
                    data = self.data.index.year.value_counts().sort_index()

            index, values = data.index, data.values

            bar_canvas = CreateCanvas()
            bar_canvas.axes.bar([f"{ind}" for ind in index], values, zorder=10)
            bar_canvas.axes.set_xlabel(column)
            bar_canvas.axes.set_ylabel("Count")
            bar_canvas.axes.grid(True, axis='y')

            if tick_labels:
                bar_canvas.axes.set_xticklabels(tick_labels)

            # rotate the angle of the label whose column who have longer names
            if column in ["LOCATION_DESC", "PERP_RACE", "VIC_RACE"]:
                labels = bar_canvas.axes.get_xticklabels()
                plt.setp(labels, rotation=90)

            plt.tight_layout()
            if self.tool_bar is not None:
                self.removeToolBar(self.tool_bar)
            self.tool_bar = NavigationToolbar2QT(bar_canvas, self)
            self.addToolBar(self.tool_bar)
            self.setCentralWidget(bar_canvas)

            self.previous_xaxis_index = self.xaxis_comboBox.currentIndex()

    def plot_horizontal_bar_chart(self):
        tick_labels = None
        if self.plot_type_comboBox.currentText() == "Bar plot":

            # prepare the data
            column = self.yaxis_comboBox.currentText()

            if column == "None":
                return

            # check if the data columns are categorical else raised error
            if column not in self.categorical_columns:
                message = "This feature data are continuous values and not categorical do you" \
                          "you still want to continue?"
                permission = QMessageBox().information(self, "Invalid data", message,
                                                       QMessageBox.Ok | QMessageBox.Discard)

                if permission == QMessageBox.Discard:
                    self.yaxis_comboBox.setCurrentIndex(self.previous_yaxis_index)
                    return
            data = self.data[column].value_counts(ascending=True)
            # if the column data have intrinsic order, sort by that order
            # rather than the default count order
            if column in ["PERP_AGE_GROUP", "VIC_AGE_GROUP"]:
                data = data.sort_index(ascending=False)

            elif column in ["OCCUR_DATE_OCCUR_TIME"]:
                # if the column feature is the datetime feature plot the chart
                # as specified by the time frequency chosen by the user
                if self.yaxis_daily_setting.isChecked():
                    tick_labels = [
                        "Mon", "Tue", "Wed", "Thurs", "Fri", "Sat", "Sun"
                    ]
                    data = self.data.index.isocalendar().day.value_counts().sort_index(ascending=True)
                elif self.yaxis_monthly_setting.isChecked():
                    tick_labels = [
                        "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct",
                        "Nov", "Dec"
                    ]
                    data = self.data.index.month.value_counts().sort_index()
                elif self.yaxis_yearly_setting.isChecked():
                    data = self.data.index.year.value_counts().sort_index()

            index, values = data.index, data.values

            bar_canvas = CreateCanvas()
            bar_canvas.axes.barh([f"{ind}" for ind in index], values, zorder=10)
            bar_canvas.axes.set_ylabel(column)
            bar_canvas.axes.set_xlabel("Count")
            bar_canvas.axes.grid(True, axis='x')

            if tick_labels:
                bar_canvas.axes.set_yticklabels(tick_labels)

            if self.tool_bar is not None:
                self.removeToolBar(self.tool_bar)
            self.tool_bar = NavigationToolbar2QT(bar_canvas, self)
            self.addToolBar(self.tool_bar)
            self.setCentralWidget(bar_canvas)

            self.previous_yaxis_index = self.yaxis_comboBox.currentIndex()

    def change_scatter_chart_transparency(self):
        self.plot_scatter_chart()

    def change_scatter_chart_shade(self):
        if self.shade_plot.isChecked():
            self.set_scatter_transparency.setDisabled(True)
        else:
            self.set_scatter_transparency.setDisabled(False)
        self.plot_scatter_chart()

    def plot_scatter_chart(self, axis=None):
        tick_labels = None
        if self.plot_type_comboBox.currentText() == "Scatter plot":

            xaxis = self.xaxis_comboBox.currentText()
            yaxis = self.yaxis_comboBox.currentText()

            # display an error message to the user if the column chosen is
            # not a numerical column
            if (xaxis not in self.numerical_columns) or (yaxis not in self.numerical_columns):
                message = "Feature do not contain numeric data"
                if axis == "x" and xaxis not in self.numerical_columns:
                    if xaxis == "None":
                        return
                    QMessageBox().warning(self, "Invalid data", message)
                elif axis == "y" and yaxis not in self.numerical_columns:
                    if yaxis == "None":
                        return
                    QMessageBox().warning(self, "Invalid data", message)
                return

            xaxis = self.data[xaxis]
            yaxis = self.data[yaxis]

            x_label = xaxis.name
            y_label = yaxis.name

            # if the column of the axis is the datetime feature
            # prepare the data to enable it display correctly
            if xaxis.name == "OCCUR_DATE_OCCUR_TIME":

                if self.xaxis_daily_setting.isChecked():
                    if not self.shade_plot.isChecked():
                        tick_labels = ["0", "Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun", "8"]
                    x_label = "Day"
                    xaxis = list(self.data.index.isocalendar().day)

                elif self.xaxis_monthly_setting.isChecked():
                    xaxis = self.data.index.month
                    x_label = "Month"

            if yaxis.name == "OCCUR_DATE_OCCUR_TIME":

                if self.yaxis_daily_setting.isChecked():
                    yaxis = list(self.data.index.isocalendar().day)
                    y_label = "Day"
                elif self.yaxis_monthly_setting.isChecked():
                    yaxis = self.data.index.month
                    y_label = "Month"

            alpha = self.set_scatter_transparency.value() / 10
            self.set_scatter_transparency.setToolTip(f"{alpha}")

            scatter_canvas = CreateCanvas()
            if self.shade_plot.isChecked():
                if x_label == y_label:
                    sns.histplot(x=xaxis, y=yaxis, ax=scatter_canvas.axes)
                else:
                    sns.kdeplot(x=xaxis, y=yaxis, fill=True, ax=scatter_canvas.axes)
            else:
                scatter_canvas.axes.scatter(xaxis, yaxis, alpha=alpha)
            scatter_canvas.axes.set_xlabel(x_label)
            scatter_canvas.axes.set_ylabel(y_label)

            if tick_labels:
                scatter_canvas.axes.set_xticklabels(tick_labels)

            if self.tool_bar is not None:
                self.removeToolBar(self.tool_bar)
            self.tool_bar = NavigationToolbar2QT(scatter_canvas, self)
            self.addToolBar(self.tool_bar)
            self.setCentralWidget(scatter_canvas)

    def plot_line_chart(self, axis=None):
        if self.plot_type_comboBox.currentText() == "Line plot":

            xaxis = self.xaxis_comboBox.currentText()
            yaxis = self.yaxis_comboBox.currentText()

            # display an error message to the user if the column chosen is
            # not a numerical column
            if (xaxis not in self.numerical_columns) or (yaxis not in self.numerical_columns):
                message = "Feature do not contain numeric data"
                if axis == "x" and xaxis not in self.numerical_columns:
                    if xaxis == "None":
                        return
                    QMessageBox().warning(self, "Invalid data", message)
                elif axis == "y" and yaxis not in self.numerical_columns:
                    if yaxis == "None":
                        return
                    QMessageBox().warning(self, "Invalid data", message)
                return

            xaxis = self.data[xaxis]
            yaxis = self.data[yaxis]

            self.axis_x = None
            self.axis_y = None

            # if the column of the axis is the datetime feature
            # prepare the data to enable it display correctly
            if xaxis.name == "OCCUR_DATE_OCCUR_TIME":

                self.axis_x = QValueAxis()
                self.axis_x.setTitleText(xaxis.name)
                self.axis_x.setLabelsEditable(False)
                self.axis_x.setLabelFormat("%i")

                if self.xaxis_daily_setting.isChecked():
                    self.axis_x.setRange(1, 7)
                    self.axis_x.setTickCount(7)
                    xaxis = self.data.index.isocalendar().day

                elif self.xaxis_monthly_setting.isChecked():
                    self.axis_x.setRange(1, 12)
                    self.axis_x.setTickCount(12)
                    xaxis = self.data.index.month

                elif self.xaxis_yearly_setting.isChecked():
                    self.axis_x.setRange(xaxis.min().year, xaxis.max().year)
                    self.axis_x.setTickCount((xaxis.max().year - xaxis.min().year) + 1)
                    xaxis = self.data.index.year

            if yaxis.name == "OCCUR_DATE_OCCUR_TIME":
                self.axis_y = QValueAxis()
                self.axis_y.setTitleText(yaxis.name)
                self.axis_y.setLabelsEditable(False)
                self.axis_y.setLabelFormat("%i")

                if self.yaxis_daily_setting.isChecked():
                    self.axis_y.setRange(1, 7)
                    self.axis_y.setTickCount(7)
                    yaxis = self.data.index.isocalendar().day

                elif self.yaxis_monthly_setting.isChecked():
                    self.axis_y.setRange(1, 12)
                    self.axis_y.setTickCount(12)
                    yaxis = self.data.index.month

                elif self.yaxis_yearly_setting.isChecked():
                    self.axis_y.setRange(yaxis.min().year, yaxis.max().year)
                    self.axis_y.setTickCount((yaxis.max().year - yaxis.min().year) + 1)
                    yaxis = self.data.index.year

            line_series = QLineSeries()
            for x, y in zip(xaxis, yaxis):
                line_series.append(x, y)

            try:
                self.chart.removeAllSeries()
            except RuntimeError:
                self.chart = QChart()

            self.chart.legend().hide()
            self.chart.addSeries(line_series)

            if self.axis_x is not None:
                line_series.attachAxis(self.axis_x)
                self.chart.setAxisX(self.axis_x)
            else:
                self.chart.removeAxis(self.axis_x)
                self.chart.createDefaultAxes()

                self.axis_x = self.chart.axes(Qt.Horizontal)
                self.axis_x[0].setTitleText(xaxis.name)

            if self.axis_y is not None:
                line_series.attachAxis(self.axis_y)
                self.chart.setAxisY(self.axis_y)
            else:
                self.chart.removeAxis(self.axis_y)
                self.chart.createDefaultAxes()

                self.axis_y = self.chart.axes(Qt.Vertical)
                self.axis_y[0].setTitleText(yaxis.name)

            if self.axis_x is None and self.axis_y is None:
                self.chart.removeAxis(self.axis_x)
                self.chart.removeAxis(self.axis_y)

                self.chart.createDefaultAxes()
                self.axis_x = self.chart.axes(Qt.Horizontal)
                self.axis_y = self.chart.axes(Qt.Vertical)

                self.axis_x[0].setTitleText(xaxis.name)
                self.axis_y[0].setTitleText(yaxis.name)
            try:
                self.chart_view.setChart(self.chart)
            except RuntimeError:
                self.chart_view = QChartView(self.chart)
            self.setCentralWidget(self.chart_view)

    def plot_density_chart(self, axis=None):
        if self.plot_type_comboBox.currentText() == "Density plot":

            xaxis = self.xaxis_comboBox.currentText()
            yaxis = self.yaxis_comboBox.currentText()

            # display an error message to the user if the column chosen is
            # not a numerical column
            if (xaxis not in self.numerical_columns) or (yaxis not in self.numerical_columns):
                message = "Feature do not contain numeric data"
                if axis == "x" and xaxis not in self.numerical_columns:
                    if xaxis == "None":
                        return
                    QMessageBox().warning(self, "Invalid data", message)
                elif axis == "y" and yaxis not in self.numerical_columns:
                    if yaxis == "None":
                        return
                    QMessageBox().warning(self, "Invalid data", message)

            density_canvas = CreateCanvas()

            if xaxis in self.numerical_columns and yaxis in self.numerical_columns:
                xaxis = self.data[xaxis]
                yaxis = self.data[yaxis]

                x_label = xaxis.name
                y_label = xaxis.name

                if xaxis.name == "OCCUR_DATE_OCCUR_TIME":

                    if self.xaxis_daily_setting.isChecked():
                        xaxis = self.data.index.isocalendar().day
                        x_label = "Day"
                        xaxis = list(xaxis)

                    elif self.xaxis_monthly_setting.isChecked():
                        xaxis = self.data.index.month
                        x_label = "Month"

                if yaxis.name == "OCCUR_DATE_OCCUR_TIME":

                    if self.yaxis_daily_setting.isChecked():
                        yaxis = self.data.index.isocalendar().day
                        y_label = "Day"
                        yaxis = list(yaxis)

                    elif self.yaxis_monthly_setting.isChecked():
                        yaxis = self.data.index.month
                        y_label = "Month"

                if x_label == y_label:
                    sns.histplot(x=xaxis, y=yaxis, ax=density_canvas.axes)
                else:
                    sns.kdeplot(x=xaxis, y=yaxis, fill=True, ax=density_canvas.axes)
                density_canvas.axes.set_xlabel(x_label)
                density_canvas.axes.set_ylabel(y_label)

            elif axis == "x" and xaxis in self.numerical_columns:
                xaxis = self.data[xaxis]
                x_label = xaxis.name

                if xaxis.name == "OCCUR_DATE_OCCUR_TIME":
                    if self.xaxis_daily_setting.isChecked():
                        xaxis = list(self.data.index.isocalendar().day)
                    elif self.xaxis_monthly_setting.isChecked():
                        xaxis = self.data.index.month

                sns.kdeplot(x=xaxis, fill=True, ax=density_canvas.axes)
                density_canvas.axes.set_xlabel(x_label)

            elif axis == "y" and yaxis in self.numerical_columns:
                yaxis = self.data[yaxis]
                y_label = yaxis.name
                if yaxis.name == "OCCUR_DATE_OCCUR_TIME":
                    if self.yaxis_daily_setting.isChecked():
                        yaxis = list(self.data.index.isocalendar().day)
                    elif self.yaxis_monthly_setting.isChecked():
                        yaxis = self.data.index.month

                sns.kdeplot(y=yaxis, fill=True, ax=density_canvas.axes)
                density_canvas.axes.set_ylabel(y_label)

            if self.tool_bar is not None:
                self.removeToolBar(self.tool_bar)
            self.tool_bar = NavigationToolbar2QT(density_canvas, self)
            self.addToolBar(self.tool_bar)
            self.setCentralWidget(density_canvas)

    def plot_data(self, axis=None):
        """Plot the data as specified by the plot type using the appropriate plotting
        sub functions."""
        plot_type = self.plot_type_comboBox.currentText()
        self.setCursor(change_cursor())

        if plot_type == "Bar plot":
            if self.xaxis_comboBox.isEnabled():
                self.plot_vertical_bar_chart()
            else:
                self.plot_horizontal_bar_chart()

        elif plot_type == "Scatter plot":
            self.plot_scatter_chart(axis)

        elif plot_type == "Line plot":
            self.plot_line_chart(axis)

        elif plot_type == "Density plot":
            self.plot_density_chart(axis)

        self.setCursor(change_cursor("off"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ControlCenter()
    window.show()
    sys.exit(app.exec_())
