
"""
This module contains function needed to perform several action throughout the
program.

Note the functions in this module follow the purely functional paradigm. That is
the function are strictly functional in that they do not change the state of
application, they only receive information through their parameter, process it
and return appropriate answers or perform appropriate actions based on that information.

This programming style has greatly helps in making the code simple, readable and detecting
bug easier. But there is only so much it can do, when not given the permission to change
the application state

"""

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

import resources


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
        """Plots vertical bar chart on the created figure

        Parameter:
        orientation: str (Vertical | Horizontal)
            The axis on which to plot the bar
        labels: list[str]
            The categorical part of the chart made up of list of str containing
             the name of each bar plotted on the graph
        values: list[int]
            The numerical part of the chart made up of list of int containing
            the height or length of each bar plotted if orientation is vertical
            or horizontal respectively
        axis_label: optional
            The name of axis been plotted on as decided by the orientation
        grid_on: bool (default = False)
            if True, the grid line will be displayed.
        grid_axis: optional
            The axis on which the grid line will be display. If None, the grid line
            will be displayed on both axis

            see matplotlib documentation for more control
        """
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
        """Plot a scatter chart on the created figure

        Parameter:
        xaxis, yaxis: list[int]
            The values to plot on the x and y axis respectively

        x_labels, y_labels: str
            The title to used in both x and y axis
        x_tick_labels, y_tick_labels: bool
            if True, the default label would be used in place of the default tick label

            see matplotlib documentation for more control
        """
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
        """Rotate the labels of the x axis by 90 deg"""
        labels = self.axes.get_xticklabels()
        plt.setp(labels, rotation=90)


def reorder_series(axis_label, series):
    """Set the order of the features that has intrinsic ordering"""
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
    """A factory class, who purpose is to group the utility function in a simple namespace
    for easier access"""
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
