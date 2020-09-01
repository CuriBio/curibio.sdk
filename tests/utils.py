# -*- coding: utf-8 -*-
def get_cell_value(sheet, zero_based_row, zero_based_col):
    return sheet.cell(row=zero_based_row + 1, column=zero_based_col + 1).value
