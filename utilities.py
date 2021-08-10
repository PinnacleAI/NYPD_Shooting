from typing import List

import pandas as pd
import seaborn as sns

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtChart import QValueAxis, QDateTimeAxis, QBarCategoryAxis
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class CreateCanvas(FigureCanvasQTAgg):
    def __init__(self, nrow=1, ncol=1):
        # create Matplotlib Figure object
        figure = Figure(dpi=100, tight_layout=True)

        # reserve width and height space for subplots
        figure.subplots_adjust(wspace=.3, hspace=.4)

        # create the axes and set the number of rows/ columns for the subplots(s)
        self.axes = figure.subplots(nrow, ncol)
        super(CreateCanvas, self).__init__(figure)

    def plot_bar_chart(self, orientation, labels: List[str], values: List[int],
                       axis_label=None, grid_on=False, grid_axis=None,
                       tick_labels: List[str] = None):
        """Plots vertical bar chart on the created figure"""
        labels = [f"{ind}" for ind in labels]

        if orientation == "Vertical":
            self.axes.bar(labels, values, zorder=10)

            if axis_label:
                self.axes.set_xlabel(axis_label)
            self.axes.set_ylabel("Count")

            if tick_labels:
                self.axes.set_xticklabels(tick_labels)

        elif orientation == "Horizontal":
            self.axes.barh(labels, values, zorder=10)

            if axis_label:
                self.axes.set_ylabel(axis_label)
            self.axes.set_xlabel("Count")

            if tick_labels:
                self.axes.set_yticklabels(tick_labels)

        if grid_on and grid_axis:
            self.axes.grid(grid_on, axis=grid_axis)

    def plot_scatter_chart(self, xaxis: List[int], yaxis: List[int], x_label: str,
                           y_label: str, x_tick_labels: bool = False, y_tick_labels: bool = False,
                           fill: bool = False, alpha=1.0, hue=None, data: pd.DataFrame = None):
        tick_labels = ["0", "Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun", "8"]
        if fill:
            if x_label == y_label:
                sns.histplot(x=xaxis, y=yaxis, ax=self.axes)
            else:
                sns.kdeplot(x=xaxis, y=yaxis, fill=fill, hue=hue, data=data, ax=self.axes)
        else:
            if hue is None:
                self.axes.scatter(xaxis, yaxis, alpha=alpha)
            else:
                sns.scatterplot(x=xaxis, y=yaxis, hue=hue, data=data, alpha=alpha, ax=self.axes)
        self.axes.set_xlabel(x_label)
        self.axes.set_ylabel(y_label)

        if x_tick_labels:
            self.axes.set_xticklabels(tick_labels)
        if y_tick_labels:
            self.axes.set_yticklabels(tick_labels)

    def rotate_ticks(self):
        labels = self.axes.get_xticklabels()
        plt.setp(labels, rotation=90)

    def plot_charts(self):
        raise NotImplementedError


def reorder_series(axis_label, series):
    if axis_label == 'JURISDICTION' or axis_label == "PERP_AGE_GROUP" or axis_label == "VIC_AGE_GROUP":
        ordered = series.cat.as_ordered()
        return ordered
    return series


def _change_axis(axis_label, values, axe="x") -> QValueAxis or QBarCategoryAxis or QDateTimeAxis:
    """Change the axis of the initial empty chart using the settings chosen by the user."""
    if axis_label == 'Latitude' or axis_label == 'Longitude':
        min_, max_ = values.min(), values.max()
        axis = QValueAxis()
        axis.setLabelFormat("%i" + "<sup>0</sup>")
        axis.setRange(min_, max_)
    elif axis_label == "OCCUR_DATE_OCCUR_TIME":
        min_, max_ = values.min(), values.max()
        axis = QDateTimeAxis()

        axis.setLabelsEditable(False)
        axis.setFormat("yyyy")
        axis.setRange(min_, max_)
    else:
        values = reorder_series(axis_label, values)
        if axis_label == "STATISTICAL_MURDER_FLAG":
            unique_cat = values.unique()
        else:
            unique_cat = values.cat.categories

        axis = QBarCategoryAxis()
        unique_cat = [f"{cat}".replace("<", "less than ") for cat in unique_cat]
        axis.append(unique_cat)

        if axe == "x":
            if axis_label in ["PRECINCT", "LOCATION_DESC", "PERP_RACE", "VIC_RACE"]:
                axis.setLabelsAngle(90)

    return axis


def _change_cursor(status="on") -> QCursor:
    """Change the cursor shape of the application to indicate it busy state"""
    cursor = QCursor()
    if status == "on":
        cursor.setShape(Qt.WaitCursor)
        return cursor
    cursor.setShape(Qt.ArrowCursor)
    return cursor


def _load_dataset_from_memory() -> pd.DataFrame:
    data = pd.read_csv("NYPD_Shooting.csv", parse_dates=[["OCCUR_DATE", "OCCUR_TIME"]])

    # optimizing tables and remove redundant columns
    data = data.drop(["Lon_Lat", "X_COORD_CD", "Y_COORD_CD", "INCIDENT_KEY"], axis=1)

    categorical_columns = [
        'BORO', 'PRECINCT', 'JURISDICTION_CODE', 'LOCATION_DESC', 'PERP_AGE_GROUP',
        'PERP_SEX', 'PERP_RACE', 'VIC_AGE_GROUP', 'VIC_SEX', 'VIC_RACE'
    ]

    data[categorical_columns] = data[categorical_columns].astype('category')
    data = data.set_index("OCCUR_DATE_OCCUR_TIME", drop=False)

    # order the age group categories
    ordering = ['<18', '18-24', '25-44', '45-64', '65+', 'UNKNOWN', '224', '940', '1020']
    data["PERP_AGE_GROUP"].cat.reorder_categories(ordering, ordered=True, inplace=True)

    ordering = ['<18', '18-24', '25-44', '45-64', '65+', 'UNKNOWN']
    data["VIC_AGE_GROUP"].cat.reorder_categories(ordering, ordered=True, inplace=True)

    return data


def _display_bar_chart_warning(parent) -> bool:
    """Display the error argument for the bar chart"""
    message = "This feature data are continuous values and not categorical, do you still " \
              "want to continue?"
    permission = QMessageBox().information(parent, "Invalid_data", message,
                                           QMessageBox.Ok | QMessageBox.Discard)
    return permission


class UtilityManager:
    @staticmethod
    def change_axis(axis_label, values, axe) -> QValueAxis or QBarCategoryAxis or QDateTimeAxis:
        return _change_axis(axis_label, values, axe)

    @staticmethod
    def change_cursor(status) -> QCursor:
        return _change_cursor(status)

    @staticmethod
    def load_dataset_from_memory() -> pd.DataFrame:
        return _load_dataset_from_memory()

    @staticmethod
    def display_bar_chart_warning(parent) -> bool:
        return _display_bar_chart_warning(parent)
