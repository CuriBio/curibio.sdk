# -*- coding: utf-8 -*-
"""Tests for excel chart creation using PlateRecording subclass.

To create a file to look at: python3 -c "import os; from curibio.sdk import PlateRecording; PlateRecording([os.path.join('tests','h5','v0.3.1','MA20123456__2020_08_17_145752__A1.h5')]).write_xlsx('.',file_name='temp.xlsx')"
To create a file to look at: python3 -c "import os; from curibio.sdk import PlateRecording; PlateRecording([os.path.join('tests','h5','v0.3.1','MA201110001__2020_09_03_213024__A3.h5')]).write_xlsx('.',file_name='temp.xlsx')"
To create a file to look at: python3 -c "import os; from curibio.sdk import PlateRecording; PlateRecording.from_directory(os.path.join('tests','h5','v0.3.1')).write_xlsx('.',file_name='temp.xlsx')"
"""
import os
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from curibio.sdk import PlateRecording
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


def test_write_xlsx__creates_two_snapshot_charts_correctly__with_data_shorter_than_chart_window():
    pr = PlateRecording(
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
    )
    expected_A1_attrs = {
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
    }
    expected_B2_attrs = {
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
    }
    ns = {
        "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
    }

    test_file_name = "test_file.xlsx"
    with tempfile.TemporaryDirectory() as tmp_dir:
        # tmp_dir = 'New Folder'
        pr.write_xlsx(tmp_dir, file_name=test_file_name)
        with zipfile.ZipFile(os.path.join(tmp_dir, test_file_name), "r") as zip_ref:
            zip_ref.extractall(tmp_dir)

        for expected_attrs in (expected_A1_attrs, expected_B2_attrs):
            chart_root = ET.parse(
                os.path.join(
                    tmp_dir, "xl", "charts", f"chart{expected_attrs['chart_num']}.xml"
                )
            ).getroot()
            chart_title = chart_root.find("c:chart/c:title/c:tx/c:rich/a:p/a:r/a:t", ns)
            assert chart_title.text == f"Well {expected_attrs['well_name']}"
            x_axis_label = chart_root.find(
                "c:chart/c:plotArea/c:catAx/c:title/c:tx/c:rich/a:p/a:r/a:t", ns
            )
            assert x_axis_label.text == "Time (seconds)"
            y_axis_label = chart_root.find(
                "c:chart/c:plotArea/c:valAx/c:title/c:tx/c:rich/a:p/a:r/a:t", ns
            )
            assert y_axis_label.text == "Magnetic Sensor Data"
            assert (
                chart_root.find("c:chart/c:plotArea/c:valAx/c:majorGridlines", ns)
                is None
            )
            waveform_series_node = chart_root.find(
                "c:chart/c:plotArea/c:lineChart/c:ser", ns
            )
            assert waveform_series_node.find("c:tx/c:v", ns).text == "Waveform Data"
            assert (
                waveform_series_node.find(
                    "c:spPr/a:ln/a:solidFill/a:srgbClr", ns
                ).attrib["val"]
                == "1B9E77"
            )
            assert (
                waveform_series_node.find("c:cat/c:numRef/c:f", ns).text
                == f"'continuous-waveforms'!{expected_attrs['x_range']}"
            )
            assert (
                waveform_series_node.find("c:val/c:numRef/c:f", ns).text
                == f"'continuous-waveforms'!{expected_attrs['y_range_w']}"
            )
            for node in chart_root.findall(
                "c:chart/c:plotArea/c:scatterChart/c:ser", ns
            ):
                series_label = node.find("c:tx/c:v", ns)
                series_color = node.find(
                    "c:marker/c:spPr/a:solidFill/a:srgbClr", ns
                ).attrib["val"]
                y_range = node.find("c:yVal/c:numRef/c:f", ns).text
                assert node.find("c:xVal/c:numRef/c:f", ns).text is None
                if int(node.find("c:idx", ns).attrib["val"]) == 1:
                    assert series_label.text == "Contraction"
                    assert series_color == "7570B3"
                    assert (
                        y_range
                        == f"'continuous-waveforms'!{expected_attrs['y_range_c']}"
                    )
                else:
                    assert series_label.text == "Relaxation"
                    assert series_color == "D95F02"
                    assert (
                        y_range
                        == f"'continuous-waveforms'!{expected_attrs['y_range_r']}"
                    )

        drawing_root = ET.parse(
            os.path.join(tmp_dir, "xl", "drawings", "drawing1.xml")
        ).getroot()
        for chart_node in drawing_root.findall("xdr:twoCellAnchor", ns):
            chart_name = chart_node.find(
                "xdr:graphicFrame/xdr:nvGraphicFramePr/xdr:cNvPr", ns
            ).attrib["name"]
            expected_attrs = (
                expected_A1_attrs if chart_name == "Chart 1" else expected_B2_attrs
            )
            from_node = chart_node.find("xdr:from", ns)
            assert int(from_node.find("xdr:col", ns).text) == expected_attrs["from_col"]
            assert (chart_name, int(from_node.find("xdr:colOff", ns).text)) == (
                chart_name,
                0,
            )
            assert int(from_node.find("xdr:row", ns).text) == expected_attrs["from_row"]
            assert (chart_name, int(from_node.find("xdr:rowOff", ns).text)) == (
                chart_name,
                0,
            )
            to_node = chart_node.find("xdr:to", ns)
            assert int(to_node.find("xdr:col", ns).text) == expected_attrs["to_col"]
            assert (chart_name, int(to_node.find("xdr:colOff", ns).text)) == (
                chart_name,
                0,
            )
            assert int(to_node.find("xdr:row", ns).text) == expected_attrs["to_row"]
            assert (chart_name, int(to_node.find("xdr:rowOff", ns).text)) == (
                chart_name,
                0,
            )


def test_write_xlsx__creates_two_snapshot_charts_correctly__with_data_longer_than_chart_window():
    pr = PlateRecording(
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
    )
    test_file_name = "test_file.xlsx"

    with tempfile.TemporaryDirectory() as tmp_dir:
        pr.write_xlsx(tmp_dir, file_name=test_file_name)
