# -*- coding: utf-8 -*-
"""Tests for excel chart creation using PlateRecording subclass."""
import os
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from curibio.sdk import PlateRecording
import pytest
from stdlib_utils import get_current_file_abs_directory

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
                "chart_num": 1,
                "well_name": "A1",
                "x_range": "$A$2:$A$355",
                "y_range_w": "$B$2:$B$355",
                "y_range_c": "$CW$2:$CW$355",
                "y_range_r": "$CX$2:$CX$355",
                "from_col": 1,
                "from_row": 1,
                "to_col": 9,
                "to_row": 16,
                "first_c_idx": 7,
                "first_c_y": -156778.33,
                "first_r_idx": 56,
                "first_r_y": 156838.0,
            },
            {
                "chart_num": 2,
                "well_name": "B2",
                "x_range": "$A$2:$A$356",
                "y_range_w": "$G$2:$G$356",
                "y_range_c": "$DG$2:$DG$356",
                "y_range_r": "$DH$2:$DH$356",
                "from_col": 10,
                "from_row": 17,
                "to_col": 18,
                "to_row": 32,
                "first_c_idx": 7,
                "first_c_y": -942193.83,
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
                "chart_num": 1,
                "well_name": "A1",
                "x_range": "$A$10543:$A$11543",
                "y_range_w": "$B$10543:$B$11543",
                "y_range_c": "$CW$10543:$CW$11543",
                "y_range_r": "$CX$10543:$CX$11543",
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
                "chart_num": 2,
                "well_name": "B2",
                "x_range": "$A$10543:$A$11543",
                "y_range_w": "$G$10543:$G$11543",
                "y_range_c": "$DG$10543:$DG$11543",
                "y_range_r": "$DH$10543:$DH$11543",
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
    test_file_name = "test_file.xlsx"
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = "New Folder"
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
            x_axis_label = chart_root.find(
                "c:chart/c:plotArea/c:catAx/c:title/c:tx/c:rich/a:p/a:r/a:t", NS
            )
            assert (x_axis_label.text, expected_well_name) == (
                "Time (seconds)",
                expected_well_name,
            )
            y_axis_label = chart_root.find(
                "c:chart/c:plotArea/c:valAx/c:title/c:tx/c:rich/a:p/a:r/a:t", NS
            )
            assert (y_axis_label.text, expected_well_name) == (
                "Magnetic Sensor Data",
                expected_well_name,
            )
            assert (expected_well_name == expected_attrs["well_name"]) and (
                chart_root.find("c:chart/c:plotArea/c:valAx/c:majorGridlines", NS)
                is None
            )
            waveform_series_node = chart_root.find(
                "c:chart/c:plotArea/c:lineChart/c:ser", NS
            )
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
                waveform_series_node.find("c:cat/c:numRef/c:f", NS).text
                == f"'continuous-waveforms'!{expected_attrs['x_range']}"
            )
            assert (
                waveform_series_node.find("c:val/c:numRef/c:f", NS).text
                == f"'continuous-waveforms'!{expected_attrs['y_range_w']}"
            )
            for ser_node in chart_root.findall(
                "c:chart/c:plotArea/c:scatterChart/c:ser", NS
            ):
                assert (
                    expected_well_name == expected_attrs["well_name"]
                ) and ser_node.find("c:xVal/c:numRef/c:f", NS).text is None
                assert (
                    expected_well_name == expected_attrs["well_name"]
                ) and ser_node.find("c:marker/c:spPr/a:noFill", NS).text is None
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
