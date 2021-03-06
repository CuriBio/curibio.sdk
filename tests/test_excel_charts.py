# -*- coding: utf-8 -*-
"""Tests for excel chart creation using PlateRecording subclass."""
import os
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from curibio.sdk import NUMBER_OF_PER_TWITCH_METRICS
from curibio.sdk import PlateRecording
from curibio.sdk.constants import CALCULATED_METRIC_DISPLAY_NAMES
from curibio.sdk.constants import PER_TWITCH_METRICS_SHEET_NAME
from curibio.sdk.constants import TWENTY_FOUR_WELL_PLATE
from mantarray_waveform_analysis import AMPLITUDE_UUID
from mantarray_waveform_analysis import TWITCH_FREQUENCY_UUID
import pytest
from stdlib_utils import get_current_file_abs_directory
from xlsxwriter.utility import xl_col_to_name

from .fixtures import fixture_generic_excel_well_file_0_1_0
from .fixtures import fixture_generic_well_file_0_3_1
from .fixtures import fixture_generic_well_file_0_3_1__2
from .fixtures import fixture_generic_well_file_0_3_2
from .fixtures import fixture_plate_recording_in_tmp_dir_for_24_wells_0_3_2
from .fixtures import fixture_plate_recording_in_tmp_dir_for_generic_well_file_0_3_1
from .fixtures import fixture_plate_recording_in_tmp_dir_for_generic_well_file_0_3_2
from .fixtures import fixture_plate_recording_in_tmp_dir_for_multiple_well_files_0_3_1
from .fixtures import fixture_plate_recording_in_tmp_dir_for_real_3min_well_file_0_3_1
from .fixtures import fixture_real_3min_well_file_0_3_1


__fixtures__ = (
    fixture_generic_well_file_0_3_1,
    fixture_generic_well_file_0_3_2,
    fixture_plate_recording_in_tmp_dir_for_generic_well_file_0_3_2,
    fixture_plate_recording_in_tmp_dir_for_real_3min_well_file_0_3_1,
    fixture_plate_recording_in_tmp_dir_for_generic_well_file_0_3_1,
    fixture_plate_recording_in_tmp_dir_for_multiple_well_files_0_3_1,
    fixture_plate_recording_in_tmp_dir_for_24_wells_0_3_2,
    fixture_generic_well_file_0_3_1__2,
    fixture_real_3min_well_file_0_3_1,
    fixture_generic_excel_well_file_0_1_0,
)

PATH_OF_CURRENT_FILE = get_current_file_abs_directory()

# XML namespaces in excel file
NS = {
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
}

# variable descriptions
# "chart_num":      Chart number in XML
# "well_name":      Name of well the data in the chart pertains to
# "x_range":        Excel data range for x-axis
# "y_range_w":      Excel data range for y values of waveforms
# "y_range_c":      Excel data range for y values of contraction markers
# "y_range_r":      Excel data range for y values of relaxation markers
# "from_col":       left-most column occupied by chart
# "from_row":       top-most column occupied by chart
# "to_col":         right-most column occupied by chart
# "to_row":         bottom-most row occupied by chart
# "first_c_idx":    first XML 'idx' value of contraction markers
# "first_c_y":      first y value of contraction markers
# "first_r_idx":    first XML 'idx' value of relaxation markers
# "first_r_y":      first y value of relaxation markers


# pylint: disable=too-many-locals
@pytest.mark.slow
@pytest.mark.parametrize(
    "pr,expected_A1_attrs,expected_B2_attrs,test_description",
    [
        (
            PlateRecording(
                [
                    os.path.join(
                        PATH_OF_CURRENT_FILE,
                        "h5",
                        "v0.3.1",
                        "MA201110001__2020_09_03_213024",
                        "MA201110001__2020_09_03_213024__A1.h5",
                    ),
                    os.path.join(
                        PATH_OF_CURRENT_FILE,
                        "h5",
                        "v0.3.1",
                        "MA201110001__2020_09_03_213024",
                        "MA201110001__2020_09_03_213024__B2.h5",
                    ),
                ]
            ),
            {
                "chart_num": 7,
                "well_name": "A1",
                "from_col": 1,
                "from_row": 1,
                "to_col": 9,
                "to_row": 16,
                "num_twitches": 242,
            },
            {
                "chart_num": 8,
                "well_name": "B2",
                "from_col": 10,
                "from_row": 17,
                "to_col": 18,
                "to_row": 32,
                "num_twitches": 429,
            },
            "creates chart correctly with given data",
        ),
    ],
)
def test_write_xlsx__creates_two_force_frequency_relationship_charts_correctly(
    pr, expected_A1_attrs, expected_B2_attrs, test_description
):
    test_file_name = "test_chart.xlsx"
    with tempfile.TemporaryDirectory() as tmp_dir:
        pr.write_xlsx(tmp_dir, file_name=test_file_name)
        with zipfile.ZipFile(os.path.join(tmp_dir, test_file_name), "r") as zip_ref:
            zip_ref.extractall(tmp_dir)

        for expected_attrs in (expected_A1_attrs, expected_B2_attrs):
            expected_well_name = expected_attrs["well_name"]
            chart_root = ET.parse(
                os.path.join(
                    tmp_dir, "xl", "charts", f"chart{expected_attrs['chart_num']}.xml"
                )
            ).getroot()
            chart_title = chart_root.find("c:chart/c:title/c:tx/c:rich/a:p/a:r/a:t", NS)
            assert chart_title.text == f"Well {expected_well_name}"

            root_elements = chart_root.findall("c:chart/c:plotArea/c:valAx", NS)
            assert len(root_elements) == 2
            for node in root_elements:
                axis_label = node.find("c:title/c:tx/c:rich/a:p/a:r/a:t", NS)
                if (
                    node.find("c:axId", NS).attrib["val"]
                    == f"500{expected_attrs['chart_num']}0001"
                ):
                    assert (expected_well_name == expected_attrs["well_name"]) and (
                        axis_label.text
                        == CALCULATED_METRIC_DISPLAY_NAMES[TWITCH_FREQUENCY_UUID]
                    )
                elif (
                    node.find("c:axId", NS).attrib["val"]
                    == f"500{expected_attrs['chart_num']}0002"
                ):
                    assert (expected_well_name == expected_attrs["well_name"]) and (
                        axis_label.text
                        == CALCULATED_METRIC_DISPLAY_NAMES[AMPLITUDE_UUID]
                    )
            assert (expected_well_name == expected_attrs["well_name"]) and (
                chart_root.find("c:chart/c:plotArea/c:valAx/c:majorGridlines", NS)
                is None
            )

            # testing frequency series
            root_elements = chart_root.findall(
                "c:chart/c:plotArea/c:scatterChart/c:ser", NS
            )
            assert len(root_elements) == 1

            force_frequency_series_node = None
            for node in root_elements:
                if node.find("c:idx", NS).attrib["val"] == "0":
                    force_frequency_series_node = node
                    break

            well_index = TWENTY_FOUR_WELL_PLATE.get_well_index_from_well_name(
                expected_attrs["well_name"]
            )
            x_range_row = (
                well_index * (NUMBER_OF_PER_TWITCH_METRICS + 2) + 4
            )  # adjusting with +2 to reflect timepoint of twitch on per twitch metrics sheet for the given well
            y_range_row = (
                well_index * (NUMBER_OF_PER_TWITCH_METRICS + 2) + 5
            )  # adjusting with +4 to reflect frequency of twitch on per twitch metrics sheet for the given well
            col_range = xl_col_to_name(expected_attrs["num_twitches"])

            # x - range
            assert (
                force_frequency_series_node.find("c:xVal/c:numRef/c:f", NS).text
                == f"'{PER_TWITCH_METRICS_SHEET_NAME}'!$B${x_range_row}:${col_range}${x_range_row}"
            )
            # y - range
            assert (
                force_frequency_series_node.find("c:yVal/c:numRef/c:f", NS).text
                == f"'{PER_TWITCH_METRICS_SHEET_NAME}'!$B${y_range_row}:${col_range}${y_range_row}"
            )

        # testing formatting of charts on sheet
        drawing_root = ET.parse(
            os.path.join(tmp_dir, "xl", "drawings", "drawing1.xml")
        ).getroot()

        drawing_root_elements = drawing_root.findall("xdr:twoCellAnchor", NS)
        assert len(drawing_root_elements) == 2

        for chart_node in drawing_root_elements:
            chart_name = chart_node.find(
                "xdr:graphicFrame/xdr:nvGraphicFramePr/xdr:cNvPr", NS
            ).attrib["name"]
            expected_attrs = (
                expected_A1_attrs if chart_name == "Chart 1" else expected_B2_attrs
            )

            from_node = chart_node.find("xdr:from", NS)
            left_col_of_chart = from_node.find("xdr:col", NS)
            top_row_of_chart = from_node.find("xdr:row", NS)

            assert (int(left_col_of_chart.text), chart_name) == (
                expected_attrs["from_col"],
                chart_name,
            )
            assert (chart_name, int(from_node.find("xdr:colOff", NS).text)) == (
                chart_name,
                0,
            )
            assert int(top_row_of_chart.text) == expected_attrs["from_row"]
            assert (chart_name, int(from_node.find("xdr:rowOff", NS).text)) == (
                chart_name,
                0,
            )

            to_node = chart_node.find("xdr:to", NS)
            right_col_of_chart = to_node.find("xdr:col", NS)
            bottom_row_of_chart = to_node.find("xdr:row", NS)

            assert int(right_col_of_chart.text) == expected_attrs["to_col"]
            assert (chart_name, int(to_node.find("xdr:colOff", NS).text)) == (
                chart_name,
                0,
            )
            assert int(bottom_row_of_chart.text) == expected_attrs["to_row"]
            assert (chart_name, int(to_node.find("xdr:rowOff", NS).text)) == (
                chart_name,
                0,
            )


# pylint: disable=too-many-locals
@pytest.mark.slow
@pytest.mark.parametrize(
    "pr,expected_A1_attrs,expected_B2_attrs,test_description",
    [
        (
            PlateRecording(
                [
                    os.path.join(
                        PATH_OF_CURRENT_FILE,
                        "h5",
                        "v0.3.1",
                        "MA20123456__2020_08_17_145752__A1.h5",
                    ),
                    os.path.join(
                        PATH_OF_CURRENT_FILE,
                        "h5",
                        "v0.3.1",
                        "MA20123456__2020_08_17_145752__B2.h5",
                    ),
                ]
            ),
            {
                "chart_num": 5,
                "well_name": "A1",
                "x_range": "$B$2:$C$2",
                "y_range": "$B$4:$C$4",
                "from_col": 1,
                "from_row": 1,
                "to_col": 9,
                "to_row": 16,
                "num_twitches": 2,
            },
            {
                "chart_num": 6,
                "well_name": "B2",
                "x_range": "$B$102:$C$102",
                "y_range": "$B$104:$C$104",
                "from_col": 10,
                "from_row": 17,
                "to_col": 18,
                "to_row": 32,
                "num_twitches": 2,
            },
            "creates chart correctly with data shorter than chart window",
        ),
        (
            PlateRecording(
                [
                    os.path.join(
                        PATH_OF_CURRENT_FILE,
                        "h5",
                        "v0.3.1",
                        "MA201110001__2020_09_03_213024",
                        "MA201110001__2020_09_03_213024__A1.h5",
                    ),
                    os.path.join(
                        PATH_OF_CURRENT_FILE,
                        "h5",
                        "v0.3.1",
                        "MA201110001__2020_09_03_213024",
                        "MA201110001__2020_09_03_213024__B2.h5",
                    ),
                ]
            ),
            {
                "chart_num": 5,
                "well_name": "A1",
                "from_col": 1,
                "from_row": 1,
                "to_col": 9,
                "to_row": 16,
                "num_twitches": 242,
            },
            {
                "chart_num": 6,
                "well_name": "B2",
                "from_col": 10,
                "from_row": 17,
                "to_col": 18,
                "to_row": 32,
                "num_twitches": 429,
            },
            "creates chart correctly with data longer than chart window",
        ),
    ],
)
def test_write_xlsx__creates_two_frequency_vs_time_charts_correctly(
    pr, expected_A1_attrs, expected_B2_attrs, test_description
):
    test_file_name = "test_chart.xlsx"
    with tempfile.TemporaryDirectory() as tmp_dir:
        pr.write_xlsx(tmp_dir, file_name=test_file_name)
        with zipfile.ZipFile(os.path.join(tmp_dir, test_file_name), "r") as zip_ref:
            zip_ref.extractall(tmp_dir)

        for expected_attrs in (expected_A1_attrs, expected_B2_attrs):
            expected_well_name = expected_attrs["well_name"]
            chart_root = ET.parse(
                os.path.join(
                    tmp_dir, "xl", "charts", f"chart{expected_attrs['chart_num']}.xml"
                )
            ).getroot()
            chart_title = chart_root.find("c:chart/c:title/c:tx/c:rich/a:p/a:r/a:t", NS)
            assert chart_title.text == f"Well {expected_well_name}"

            root_elements = chart_root.findall("c:chart/c:plotArea/c:valAx", NS)
            assert len(root_elements) == 2
            for node in root_elements:
                axis_label = node.find("c:title/c:tx/c:rich/a:p/a:r/a:t", NS)
                if (
                    node.find("c:axId", NS).attrib["val"]
                    == f"500{expected_attrs['chart_num']}0001"
                ):
                    assert (expected_well_name == expected_attrs["well_name"]) and (
                        axis_label.text == "Time (seconds)"
                    )
                elif (
                    node.find("c:axId", NS).attrib["val"]
                    == f"500{expected_attrs['chart_num']}0002"
                ):
                    assert (expected_well_name == expected_attrs["well_name"]) and (
                        axis_label.text
                        == CALCULATED_METRIC_DISPLAY_NAMES[TWITCH_FREQUENCY_UUID]
                    )
            assert (expected_well_name == expected_attrs["well_name"]) and (
                chart_root.find("c:chart/c:plotArea/c:valAx/c:majorGridlines", NS)
                is None
            )

            # testing frequency series

            root_elements = chart_root.findall(
                "c:chart/c:plotArea/c:scatterChart/c:ser", NS
            )
            assert len(root_elements) == 1

            frequency_series_node = None
            for node in root_elements:
                if node.find("c:idx", NS).attrib["val"] == "0":
                    frequency_series_node = node
                    break

            well_index = TWENTY_FOUR_WELL_PLATE.get_well_index_from_well_name(
                expected_attrs["well_name"]
            )
            x_range_row = (
                well_index * (NUMBER_OF_PER_TWITCH_METRICS + 2) + 2
            )  # adjusting with +2 to reflect timepoint of twitch on per twitch metrics sheet for the given well
            y_range_row = (
                well_index * (NUMBER_OF_PER_TWITCH_METRICS + 2) + 4
            )  # adjusting with +4 to reflect frequency of twitch on per twitch metrics sheet for the given well
            col_range = xl_col_to_name(expected_attrs["num_twitches"])

            # x - range
            assert (
                frequency_series_node.find("c:xVal/c:numRef/c:f", NS).text
                == f"'{PER_TWITCH_METRICS_SHEET_NAME}'!$B${x_range_row}:${col_range}${x_range_row}"
            )
            # y - range
            assert (
                frequency_series_node.find("c:yVal/c:numRef/c:f", NS).text
                == f"'{PER_TWITCH_METRICS_SHEET_NAME}'!$B${y_range_row}:${col_range}${y_range_row}"
            )

        # testing formatting of charts on sheet
        drawing_root = ET.parse(
            os.path.join(tmp_dir, "xl", "drawings", "drawing1.xml")
        ).getroot()
        drawing_root_elements = drawing_root.findall("xdr:twoCellAnchor", NS)
        assert len(drawing_root_elements) == 2

        for chart_node in drawing_root_elements:
            chart_name = chart_node.find(
                "xdr:graphicFrame/xdr:nvGraphicFramePr/xdr:cNvPr", NS
            ).attrib["name"]
            expected_attrs = (
                expected_A1_attrs if chart_name == "Chart 1" else expected_B2_attrs
            )

            from_node = chart_node.find("xdr:from", NS)
            left_col_of_chart = from_node.find("xdr:col", NS)
            top_row_of_chart = from_node.find("xdr:row", NS)

            assert (int(left_col_of_chart.text), chart_name) == (
                expected_attrs["from_col"],
                chart_name,
            )
            assert (chart_name, int(from_node.find("xdr:colOff", NS).text)) == (
                chart_name,
                0,
            )
            assert int(top_row_of_chart.text) == expected_attrs["from_row"]
            assert (chart_name, int(from_node.find("xdr:rowOff", NS).text)) == (
                chart_name,
                0,
            )

            to_node = chart_node.find("xdr:to", NS)
            right_col_of_chart = to_node.find("xdr:col", NS)
            bottom_row_of_chart = to_node.find("xdr:row", NS)

            assert int(right_col_of_chart.text) == expected_attrs["to_col"]
            assert (chart_name, int(to_node.find("xdr:colOff", NS).text)) == (
                chart_name,
                0,
            )
            assert int(bottom_row_of_chart.text) == expected_attrs["to_row"]
            assert (chart_name, int(to_node.find("xdr:rowOff", NS).text)) == (
                chart_name,
                0,
            )


# pylint: disable=too-many-locals
@pytest.mark.slow
@pytest.mark.parametrize(
    "pr,expected_A1_attrs,expected_B2_attrs,test_description",
    [
        (
            PlateRecording(
                [
                    os.path.join(
                        PATH_OF_CURRENT_FILE,
                        "h5",
                        "v0.3.1",
                        "MA20123456__2020_08_17_145752__A1.h5",
                    ),
                    os.path.join(
                        PATH_OF_CURRENT_FILE,
                        "h5",
                        "v0.3.1",
                        "MA20123456__2020_08_17_145752__B2.h5",
                    ),
                ]
            ),
            {
                "chart_num": 3,
                "well_name": "A1",
                "x_range": "$A$2:$A$354",
                "y_range_w": "$B$2:$B$354",
                "y_range_c": "$CW$2:$CW$354",
                "y_range_r": "$CX$2:$CX$354",
                "from_col": 1,
                "from_row": 1,
                "to_col": 9,
                "to_row": 16,
                "first_c_idx": 107,
                "first_c_y": -156924.17,
                "first_r_idx": 56,
                "first_r_y": 156838.0,
            },
            {
                "chart_num": 4,
                "well_name": "B2",
                "x_range": "$A$2:$A$355",
                "y_range_w": "$G$2:$G$355",
                "y_range_c": "$DG$2:$DG$355",
                "y_range_r": "$DH$2:$DH$355",
                "from_col": 10,
                "from_row": 17,
                "to_col": 18,
                "to_row": 32,
                "first_c_idx": 107,
                "first_c_y": -942203.25,
                "first_r_idx": 56,
                "first_r_y": 943009.0,
            },
            "creates chart correctly with data shorter than chart window",
        ),
        (
            PlateRecording(
                [
                    os.path.join(
                        PATH_OF_CURRENT_FILE,
                        "h5",
                        "v0.3.1",
                        "MA201110001__2020_09_03_213024",
                        "MA201110001__2020_09_03_213024__A1.h5",
                    ),
                    os.path.join(
                        PATH_OF_CURRENT_FILE,
                        "h5",
                        "v0.3.1",
                        "MA201110001__2020_09_03_213024",
                        "MA201110001__2020_09_03_213024__B2.h5",
                    ),
                ]
            ),
            {
                "chart_num": 3,
                "well_name": "A1",
                "x_range": "$A$2:$A$22087",
                "y_range_w": "$B$2:$B$22087",
                "y_range_c": "$CW$2:$CW$22087",
                "y_range_r": "$CX$2:$CX$22087",
                "from_col": 1,
                "from_row": 1,
                "to_col": 9,
                "to_row": 16,
                "first_c_idx": 71,
                "first_c_y": -95944.38,
                "first_r_idx": 28,
                "first_r_y": 7530.80,
            },
            {
                "chart_num": 4,
                "well_name": "B2",
                "x_range": "$A$2:$A$22087",
                "y_range_w": "$G$2:$G$22087",
                "y_range_c": "$DG$2:$DG$22087",
                "y_range_r": "$DH$2:$DH$22087",
                "from_col": 10,
                "from_row": 17,
                "to_col": 18,
                "to_row": 32,
                "first_c_idx": 34,
                "first_c_y": -127349.83,
                "first_r_idx": 8,
                "first_r_y": -50245.47,
            },
            "creates chart correctly with data longer than chart window",
        ),
    ],
)
def test_write_xlsx__creates_two_snapshot_charts_correctly(
    pr, expected_A1_attrs, expected_B2_attrs, test_description
):
    test_file_name = "test_chart.xlsx"
    with tempfile.TemporaryDirectory() as tmp_dir:
        pr.write_xlsx(tmp_dir, file_name=test_file_name)
        with zipfile.ZipFile(os.path.join(tmp_dir, test_file_name), "r") as zip_ref:
            zip_ref.extractall(tmp_dir)

        for expected_attrs in (expected_A1_attrs, expected_B2_attrs):
            expected_well_name = expected_attrs["well_name"]
            chart_root = ET.parse(
                os.path.join(
                    tmp_dir, "xl", "charts", f"chart{expected_attrs['chart_num']}.xml"
                )
            ).getroot()
            chart_title = chart_root.find("c:chart/c:title/c:tx/c:rich/a:p/a:r/a:t", NS)
            assert chart_title.text == f"Well {expected_well_name}"
            for node in chart_root.findall("c:chart/c:plotArea/c:valAx", NS):
                axis_label = node.find("c:title/c:tx/c:rich/a:p/a:r/a:t", NS)
                if node.find("c:axId", NS).attrib["val"] == "50010001":
                    assert (expected_well_name == expected_attrs["well_name"]) and (
                        axis_label.text == "Time (seconds)"
                    )
                elif node.find("c:axId", NS).attrib["val"] == "50010002":
                    assert (expected_well_name == expected_attrs["well_name"]) and (
                        axis_label.text == "Magnetic Sensor Data"
                    )
            assert (expected_well_name == expected_attrs["well_name"]) and (
                chart_root.find("c:chart/c:plotArea/c:valAx/c:majorGridlines", NS)
                is None
            )
            waveform_series_node = None
            for node in chart_root.findall(
                "c:chart/c:plotArea/c:scatterChart/c:ser", NS
            ):
                if node.find("c:idx", NS).attrib["val"] == "0":
                    waveform_series_node = node
                    break
            assert (
                waveform_series_node.find("c:tx/c:v", NS).text,
                expected_well_name,
            ) == ("Waveform Data", expected_well_name)
            assert (
                waveform_series_node.find(
                    "c:spPr/a:ln/a:solidFill/a:srgbClr", NS
                ).attrib["val"],
                expected_well_name,
            ) == ("1B9E77", expected_well_name)
            assert (
                waveform_series_node.find("c:xVal/c:numRef/c:f", NS).text
                == f"'continuous-waveforms'!{expected_attrs['x_range']}"
            )
            assert (
                waveform_series_node.find("c:yVal/c:numRef/c:f", NS).text
                == f"'continuous-waveforms'!{expected_attrs['y_range_w']}"
            )
            for ser_node in chart_root.findall(
                "c:chart/c:plotArea/c:scatterChart/c:ser", NS
            ):
                if node.find("c:idx", NS).attrib["val"] == "0":
                    continue
                assert (expected_well_name == expected_attrs["well_name"]) and (
                    ser_node.find("c:xVal/c:numRef/c:f", NS).text
                    == f"'continuous-waveforms'!{expected_attrs['x_range']}"
                )
                no_fill_node = ser_node.find("c:marker/c:spPr/a:noFill", NS)
                if no_fill_node is not None:
                    assert (expected_well_name == expected_attrs["well_name"]) and (
                        no_fill_node.text is None
                    )
                fill_node = ser_node.find("c:marker/c:spPr/a:noFill", NS)
                if fill_node is not None:
                    assert (expected_well_name == expected_attrs["well_name"]) and (
                        fill_node.text is None
                    )
                assert (
                    ser_node.find("c:marker/c:symbol", NS).attrib["val"],
                    expected_well_name,
                ) == ("circle", expected_well_name)
                assert (
                    int(ser_node.find("c:marker/c:spPr/a:ln", NS).attrib["w"]),
                    expected_well_name,
                ) == (19050, expected_well_name)
                series_color = ser_node.find(
                    "c:marker/c:spPr/a:ln/a:solidFill/a:srgbClr", NS
                ).attrib["val"]
                y_range = ser_node.find("c:yVal/c:numRef/c:f", NS).text
                if int(ser_node.find("c:idx", NS).attrib["val"]) == 1:
                    assert (
                        ser_node.find("c:tx/c:v", NS).text,
                        expected_well_name,
                        ser_node,
                    ) == ("Contraction", expected_well_name, ser_node)
                    assert (series_color, expected_well_name, ser_node) == (
                        "7570B3",
                        expected_well_name,
                        ser_node,
                    )
                    assert (y_range, expected_well_name, ser_node) == (
                        f"'continuous-waveforms'!{expected_attrs['y_range_c']}",
                        expected_well_name,
                        ser_node,
                    )
                    first_c_marker_idx = expected_attrs["first_c_idx"]
                    first_c_marker_node = ser_node.find(
                        f"c:yVal/c:numRef/c:numCache/c:pt/[@idx='{first_c_marker_idx}']",
                        NS,
                    )
                    assert (
                        round(float(first_c_marker_node.find("c:v", NS).text), 2),
                        expected_well_name,
                        ser_node,
                    ) == (expected_attrs["first_c_y"], expected_well_name, ser_node)
                elif int(ser_node.find("c:idx", NS).attrib["val"]) == 2:
                    assert (
                        ser_node.find("c:tx/c:v", NS).text,
                        expected_well_name,
                        ser_node,
                    ) == ("Relaxation", expected_well_name, ser_node)
                    assert (series_color, expected_well_name, ser_node) == (
                        "D95F02",
                        expected_well_name,
                        ser_node,
                    )
                    assert (y_range, expected_well_name, ser_node) == (
                        f"'continuous-waveforms'!{expected_attrs['y_range_r']}",
                        expected_well_name,
                        ser_node,
                    )
                    first_r_marker_idx = expected_attrs["first_r_idx"]
                    first_r_marker_node = ser_node.find(
                        f"c:yVal/c:numRef/c:numCache/c:pt/[@idx='{first_r_marker_idx}']",
                        NS,
                    )
                    assert (
                        round(float(first_r_marker_node.find("c:v", NS).text), 2),
                        expected_well_name,
                        ser_node,
                    ) == (expected_attrs["first_r_y"], expected_well_name, ser_node)

        drawing_root = ET.parse(
            os.path.join(tmp_dir, "xl", "drawings", "drawing1.xml")
        ).getroot()
        for chart_node in drawing_root.findall("xdr:twoCellAnchor", NS):
            chart_name = chart_node.find(
                "xdr:graphicFrame/xdr:nvGraphicFramePr/xdr:cNvPr", NS
            ).attrib["name"]
            expected_attrs = (
                expected_A1_attrs if chart_name == "Chart 1" else expected_B2_attrs
            )
            from_node = chart_node.find("xdr:from", NS)
            assert (int(from_node.find("xdr:col", NS).text), chart_name) == (
                expected_attrs["from_col"],
                chart_name,
            )
            assert (chart_name, int(from_node.find("xdr:colOff", NS).text)) == (
                chart_name,
                0,
            )
            assert int(from_node.find("xdr:row", NS).text) == expected_attrs["from_row"]
            assert (chart_name, int(from_node.find("xdr:rowOff", NS).text)) == (
                chart_name,
                0,
            )
            to_node = chart_node.find("xdr:to", NS)
            assert int(to_node.find("xdr:col", NS).text) == expected_attrs["to_col"]
            assert (chart_name, int(to_node.find("xdr:colOff", NS).text)) == (
                chart_name,
                0,
            )
            assert int(to_node.find("xdr:row", NS).text) == expected_attrs["to_row"]
            assert (chart_name, int(to_node.find("xdr:rowOff", NS).text)) == (
                chart_name,
                0,
            )


def test_write_xlsx__uses_correct_axis_names_for_optical_data(
    generic_excel_well_file_0_1_0,
):
    test_file_name = "test_file.xlsx"
    pr = PlateRecording([generic_excel_well_file_0_1_0])
    with tempfile.TemporaryDirectory() as tmp_dir:
        pr.write_xlsx(tmp_dir, file_name=test_file_name)
        with zipfile.ZipFile(os.path.join(tmp_dir, test_file_name), "r") as zip_ref:
            zip_ref.extractall(tmp_dir)
        chart_root = ET.parse(
            os.path.join(tmp_dir, "xl", "charts", "chart1.xml")
        ).getroot()
        valAxs = list(chart_root.findall("c:chart/c:plotArea/c:valAx", NS))
        assert len(valAxs) == 2
        for node in valAxs:
            axis_label = node.find("c:title/c:tx/c:rich/a:p/a:r/a:t", NS)
            if node.find("c:axId", NS).attrib["val"] == "50010002":
                assert axis_label.text == "Post Displacement (microns)"
            else:
                assert axis_label.text == "Time (seconds)"


# pylint: disable=too-many-locals
@pytest.mark.slow
@pytest.mark.parametrize(
    "pr,expected_A1_attrs,expected_B2_attrs,test_description",
    [
        (
            PlateRecording(
                [
                    os.path.join(
                        PATH_OF_CURRENT_FILE,
                        "h5",
                        "v0.3.1",
                        "MA201110001__2020_09_03_213024",
                        "MA201110001__2020_09_03_213024__A1.h5",
                    ),
                    os.path.join(
                        PATH_OF_CURRENT_FILE,
                        "h5",
                        "v0.3.1",
                        "MA201110001__2020_09_03_213024",
                        "MA201110001__2020_09_03_213024__B2.h5",
                    ),
                ]
            ),
            {
                "chart_num": 1,
                "well_name": "A1",
                "x_range": "$A$2:$A$22087",
                "y_range_w": "$B$2:$B$22087",
                "y_range_c": "$CW$2:$CW$22087",
                "y_range_r": "$CX$2:$CX$22087",
                "from_col": 1,
                "from_row": 1,
                "to_col": 93,
                "to_row": 16,
                "first_c_idx": 71,
                "first_c_y": -95944.38,
                "first_r_idx": 28,
                "first_r_y": 7530.80,
            },
            {
                "chart_num": 2,
                "well_name": "B2",
                "x_range": "$A$2:$A$22087",
                "y_range_w": "$G$2:$G$22087",
                "y_range_c": "$DG$2:$DG$22087",
                "y_range_r": "$DH$2:$DH$22087",
                "from_col": 1,
                "from_row": 17,
                "to_col": 93,
                "to_row": 32,
                "first_c_idx": 34,
                "first_c_y": -127349.83,
                "first_r_idx": 8,
                "first_r_y": -50245.47,
            },
            "creates 2 full length charts correctly",
        ),
    ],
)
def test_write_xlsx__creates_two_full_charts_correctly(
    pr, expected_A1_attrs, expected_B2_attrs, test_description
):
    test_file_name = "test_full.xlsx"
    with tempfile.TemporaryDirectory() as tmp_dir:
        pr.write_xlsx(tmp_dir, file_name=test_file_name)
        with zipfile.ZipFile(os.path.join(tmp_dir, test_file_name), "r") as zip_ref:
            zip_ref.extractall(tmp_dir)

        for expected_attrs in (expected_A1_attrs, expected_B2_attrs):
            expected_well_name = expected_attrs["well_name"]
            chart_root = ET.parse(
                os.path.join(
                    tmp_dir, "xl", "charts", f"chart{expected_attrs['chart_num']}.xml"
                )
            ).getroot()
            chart_title = chart_root.find("c:chart/c:title/c:tx/c:rich/a:p/a:r/a:t", NS)
            assert chart_title.text == f"Well {expected_well_name}"
            for node in chart_root.findall("c:chart/c:plotArea/c:valAx", NS):
                axis_label = node.find("c:title/c:tx/c:rich/a:p/a:r/a:t", NS)
                if node.find("c:axId", NS).attrib["val"] == "50010001":
                    assert (expected_well_name == expected_attrs["well_name"]) and (
                        axis_label.text == "Time (seconds)"
                    )
                elif node.find("c:axId", NS).attrib["val"] == "50010002":
                    assert (expected_well_name == expected_attrs["well_name"]) and (
                        axis_label.text == "Magnetic Sensor Data"
                    )
            assert (expected_well_name == expected_attrs["well_name"]) and (
                chart_root.find("c:chart/c:plotArea/c:valAx/c:majorGridlines", NS)
                is None
            )
            waveform_series_node = None
            for node in chart_root.findall(
                "c:chart/c:plotArea/c:scatterChart/c:ser", NS
            ):
                if node.find("c:idx", NS).attrib["val"] == "0":
                    waveform_series_node = node
                    break
            assert (
                waveform_series_node.find("c:tx/c:v", NS).text,
                expected_well_name,
            ) == ("Waveform Data", expected_well_name)
            assert (
                waveform_series_node.find(
                    "c:spPr/a:ln/a:solidFill/a:srgbClr", NS
                ).attrib["val"],
                expected_well_name,
            ) == ("1B9E77", expected_well_name)
            assert (
                waveform_series_node.find("c:xVal/c:numRef/c:f", NS).text
                == f"'continuous-waveforms'!{expected_attrs['x_range']}"
            )
            assert (
                waveform_series_node.find("c:yVal/c:numRef/c:f", NS).text
                == f"'continuous-waveforms'!{expected_attrs['y_range_w']}"
            )
            for ser_node in chart_root.findall(
                "c:chart/c:plotArea/c:scatterChart/c:ser", NS
            ):
                if node.find("c:idx", NS).attrib["val"] == "0":
                    continue
                assert (expected_well_name == expected_attrs["well_name"]) and (
                    ser_node.find("c:xVal/c:numRef/c:f", NS).text
                    == f"'continuous-waveforms'!{expected_attrs['x_range']}"
                )
                no_fill_node = ser_node.find("c:marker/c:spPr/a:noFill", NS)
                if no_fill_node is not None:
                    assert (expected_well_name == expected_attrs["well_name"]) and (
                        no_fill_node.text is None
                    )
                fill_node = ser_node.find("c:marker/c:spPr/a:noFill", NS)
                if fill_node is not None:
                    assert (expected_well_name == expected_attrs["well_name"]) and (
                        fill_node.text is None
                    )
                assert (
                    ser_node.find("c:marker/c:symbol", NS).attrib["val"],
                    expected_well_name,
                ) == ("circle", expected_well_name)
                assert (
                    int(ser_node.find("c:marker/c:spPr/a:ln", NS).attrib["w"]),
                    expected_well_name,
                ) == (19050, expected_well_name)
                series_color = ser_node.find(
                    "c:marker/c:spPr/a:ln/a:solidFill/a:srgbClr", NS
                ).attrib["val"]
                y_range = ser_node.find("c:yVal/c:numRef/c:f", NS).text
                if int(ser_node.find("c:idx", NS).attrib["val"]) == 1:
                    assert (
                        ser_node.find("c:tx/c:v", NS).text,
                        expected_well_name,
                        ser_node,
                    ) == ("Contraction", expected_well_name, ser_node)
                    assert (series_color, expected_well_name, ser_node) == (
                        "7570B3",
                        expected_well_name,
                        ser_node,
                    )
                    assert (y_range, expected_well_name, ser_node) == (
                        f"'continuous-waveforms'!{expected_attrs['y_range_c']}",
                        expected_well_name,
                        ser_node,
                    )
                    first_c_marker_idx = expected_attrs["first_c_idx"]
                    first_c_marker_node = ser_node.find(
                        f"c:yVal/c:numRef/c:numCache/c:pt/[@idx='{first_c_marker_idx}']",
                        NS,
                    )
                    assert (
                        round(float(first_c_marker_node.find("c:v", NS).text), 2),
                        expected_well_name,
                        ser_node,
                    ) == (expected_attrs["first_c_y"], expected_well_name, ser_node)
                elif int(ser_node.find("c:idx", NS).attrib["val"]) == 2:
                    assert (
                        ser_node.find("c:tx/c:v", NS).text,
                        expected_well_name,
                        ser_node,
                    ) == ("Relaxation", expected_well_name, ser_node)
                    assert (series_color, expected_well_name, ser_node) == (
                        "D95F02",
                        expected_well_name,
                        ser_node,
                    )
                    assert (y_range, expected_well_name, ser_node) == (
                        f"'continuous-waveforms'!{expected_attrs['y_range_r']}",
                        expected_well_name,
                        ser_node,
                    )
                    first_r_marker_idx = expected_attrs["first_r_idx"]
                    first_r_marker_node = ser_node.find(
                        f"c:yVal/c:numRef/c:numCache/c:pt/[@idx='{first_r_marker_idx}']",
                        NS,
                    )
                    assert (
                        round(float(first_r_marker_node.find("c:v", NS).text), 2),
                        expected_well_name,
                        ser_node,
                    ) == (expected_attrs["first_r_y"], expected_well_name, ser_node)

        drawing_root = ET.parse(
            os.path.join(tmp_dir, "xl", "drawings", "drawing2.xml")
        ).getroot()
        for chart_node in drawing_root.findall("xdr:twoCellAnchor", NS):
            chart_name = chart_node.find(
                "xdr:graphicFrame/xdr:nvGraphicFramePr/xdr:cNvPr", NS
            ).attrib["name"]
            expected_attrs = (
                expected_A1_attrs if chart_name == "Chart 1" else expected_B2_attrs
            )
            from_node = chart_node.find("xdr:from", NS)
            assert (int(from_node.find("xdr:col", NS).text), chart_name) == (
                expected_attrs["from_col"],
                chart_name,
            )
            assert (chart_name, int(from_node.find("xdr:colOff", NS).text)) == (
                chart_name,
                0,
            )
            assert int(from_node.find("xdr:row", NS).text) == expected_attrs["from_row"]
            assert (chart_name, int(from_node.find("xdr:rowOff", NS).text)) == (
                chart_name,
                0,
            )
            to_node = chart_node.find("xdr:to", NS)
            assert int(to_node.find("xdr:col", NS).text) == expected_attrs["to_col"]
            assert (chart_name, int(to_node.find("xdr:colOff", NS).text)) == (
                chart_name,
                0,
            )
            assert int(to_node.find("xdr:row", NS).text) == expected_attrs["to_row"]
            assert (chart_name, int(to_node.find("xdr:rowOff", NS).text)) == (
                chart_name,
                0,
            )
