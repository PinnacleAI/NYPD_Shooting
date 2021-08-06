# import pandas as pd

from PyQt5.QtChart import QValueAxis, QDateTimeAxis, QBarCategoryAxis
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt


def reorder_series(axis_label, series):
    if axis_label == 'JURISDICTION' or axis_label == "PERP_AGE_GROUP" or axis_label == "VIC_AGE_GROUP":
        ordered = series.cat.as_ordered()
        return ordered
    return series


def change_axis(axis_label, values, axe="x") -> QValueAxis or QBarCategoryAxis or QDateTimeAxis:
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


def change_cursor(status="on") -> QCursor:
    """Change the cursor shape of the application to indicate it busy state"""
    cursor = QCursor()
    if status == "on":
        cursor.setShape(Qt.WaitCursor)
        return cursor
    cursor.setShape(Qt.ArrowCursor)
    return cursor

