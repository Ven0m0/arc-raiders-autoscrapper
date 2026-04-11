import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from autoscrapper.ocr import tesseract
from autoscrapper.ocr.tesseract import OcrBackendInfo, _empty_data_dict


@pytest.fixture(autouse=True)
def reset_tesseract_state():
    """Reset global state in tesseract module before and after each test."""
    # Store original state
    orig_api = tesseract._api
    orig_api_line = tesseract._api_line
    orig_tessdata_dir = tesseract._tessdata_dir
    orig_backend_info = tesseract._backend_info

    # Reset state
    tesseract._api = None
    tesseract._api_line = None
    tesseract._tessdata_dir = None
    tesseract._backend_info = None

    yield

    # Restore state
    tesseract._api = orig_api
    tesseract._api_line = orig_api_line
    tesseract._tessdata_dir = orig_tessdata_dir
    tesseract._backend_info = orig_backend_info


def test_has_eng_returns_true_if_dir_and_file_exist(tmp_path):
    (tmp_path / "eng.traineddata").touch()
    assert tesseract._has_eng(tmp_path) is True


def test_has_eng_returns_false_if_file_missing(tmp_path):
    assert tesseract._has_eng(tmp_path) is False


def test_has_eng_returns_false_if_not_dir(tmp_path):
    file_path = tmp_path / "not_a_dir"
    file_path.touch()
    assert tesseract._has_eng(file_path) is False


@patch.dict(os.environ, {"TESSDATA_PREFIX": "/mock/env/path", "APPDATA": "/mock/appdata"})
@patch("tessdata.data_path", return_value="/mock/tessdata/path")
@patch("src.autoscrapper.ocr.tesseract.tessdata.__file__", "/mock/pkg/tessdata/__init__.py")
def test_candidate_tessdata_paths_order(mock_tessdata_path):
    paths = tesseract._candidate_tessdata_paths()

    # Check that paths are generated and deduplicated in order
    assert paths[0] == Path("/mock/env/path")
    assert paths[1] == Path("/mock/tessdata/path")
    assert paths[2] == Path("/mock/pkg/share/tessdata")
    assert paths[3] == Path("/mock/appdata/Python/share/tessdata")
    py_ver = f"Python{sys.version_info.major}{sys.version_info.minor}"
    assert paths[4] == Path(f"/mock/appdata/Python/{py_ver}/share/tessdata")


@patch("src.autoscrapper.ocr.tesseract._has_eng", return_value=True)
@patch("src.autoscrapper.ocr.tesseract._candidate_tessdata_paths", return_value=[Path("/mock/path")])
@patch("src.autoscrapper.ocr.tesseract.PyTessBaseAPI")
def test_create_api_success(mock_api_class, mock_paths, mock_has_eng):
    mock_api_instance = MagicMock()
    mock_api_class.return_value = mock_api_instance

    api = tesseract._create_api()

    assert api == mock_api_instance
    mock_api_class.assert_called_once_with(path="/mock/path", lang="eng", psm=tesseract.PSM.SINGLE_BLOCK)
    mock_api_instance.SetVariable.assert_called_once()
    assert tesseract._tessdata_dir == "/mock/path"


@patch("src.autoscrapper.ocr.tesseract._has_eng", return_value=True)
@patch("src.autoscrapper.ocr.tesseract._candidate_tessdata_paths", return_value=[Path("/mock/path")])
@patch("src.autoscrapper.ocr.tesseract.PyTessBaseAPI", side_effect=Exception("mock init error"))
def test_create_api_fails_all_candidates(mock_api_class, mock_paths, mock_has_eng):
    with pytest.raises(RuntimeError) as exc_info:
        tesseract._create_api()

    assert "Could not initialize Tesseract API" in str(exc_info.value)
    assert "/mock/path: mock init error" in str(exc_info.value)


def test_as_pil_image_converts_2d():
    img_2d = np.zeros((10, 10), dtype=np.uint8)
    pil_img = tesseract._as_pil_image(img_2d)
    assert pil_img.size == (10, 10)
    assert pil_img.mode == "L"


def test_as_pil_image_converts_3d_bgr():
    img_3d = np.zeros((10, 10, 3), dtype=np.uint8)
    img_3d[:, :, 0] = 255 # Blue channel
    pil_img = tesseract._as_pil_image(img_3d)
    assert pil_img.size == (10, 10)
    assert pil_img.mode == "RGB"
    # OpenCV BGR to PIL RGB conversion check
    assert np.array(pil_img)[0, 0, 2] == 255


def test_as_pil_image_converts_3d_bgra():
    img_4d = np.zeros((10, 10, 4), dtype=np.uint8)
    img_4d[:, :, 0] = 255 # Blue channel
    img_4d[:, :, 3] = 255 # Alpha channel
    pil_img = tesseract._as_pil_image(img_4d)
    assert pil_img.size == (10, 10)
    assert pil_img.mode == "RGBA"
    # OpenCV BGRA to PIL RGBA conversion check
    assert np.array(pil_img)[0, 0, 2] == 255
    assert np.array(pil_img)[0, 0, 3] == 255


def test_as_pil_image_raises_value_error_for_invalid_shape():
    img_invalid = np.zeros((10, 10, 5), dtype=np.uint8)
    with pytest.raises(ValueError, match="Unsupported image shape"):
        tesseract._as_pil_image(img_invalid)


@patch("src.autoscrapper.ocr.tesseract._get_api")
def test_image_to_string_success(mock_get_api):
    mock_api = MagicMock()
    mock_api.GetUTF8Text.return_value = "Mock Text"
    mock_get_api.return_value = mock_api

    img = np.zeros((10, 10), dtype=np.uint8)
    text = tesseract.image_to_string(img)

    assert text == "Mock Text"
    mock_api.SetImage.assert_called_once()
    mock_api.GetUTF8Text.assert_called_once()


@patch("src.autoscrapper.ocr.tesseract._get_api")
def test_image_to_string_empty(mock_get_api):
    mock_api = MagicMock()
    mock_api.GetUTF8Text.return_value = None
    mock_get_api.return_value = mock_api

    img = np.zeros((10, 10), dtype=np.uint8)
    text = tesseract.image_to_string(img)

    assert text == ""


@patch("src.autoscrapper.ocr.tesseract._get_api")
def test_image_to_data_empty_iterator(mock_get_api):
    mock_api = MagicMock()
    mock_api.GetIterator.return_value = None
    mock_get_api.return_value = mock_api

    img = np.zeros((10, 10), dtype=np.uint8)
    data = tesseract.image_to_data(img)

    assert data == _empty_data_dict()


def test_build_data_dict_with_iterator():
    mock_word = MagicMock()
    mock_word.IsAtBeginningOf.side_effect = lambda level: level in (tesseract.RIL.BLOCK, tesseract.RIL.PARA, tesseract.RIL.TEXTLINE)
    mock_word.BoundingBox.return_value = (10, 10, 100, 30)
    mock_word.Confidence.return_value = 95.5
    mock_word.GetUTF8Text.return_value = "TestWord"

    # We need iterate_level to yield our mock word
    with patch("src.autoscrapper.ocr.tesseract.iterate_level", return_value=[mock_word]):
        data = tesseract._build_data_dict(MagicMock())

        assert len(data["text"]) == 1
        assert data["text"][0] == "TestWord"
        assert data["conf"][0] == "95.50"
        assert data["left"][0] == 10
        assert data["top"][0] == 10
        assert data["width"][0] == 90
        assert data["height"][0] == 20
        assert data["level"][0] == int(tesseract.RIL.WORD)


def test_record_backend_info():
    mock_api = MagicMock()
    mock_api.Version.return_value = "1.2.3"
    mock_api.GetAvailableLanguages.return_value = ["eng", "fra"]

    # Needs a mock tessdata dir
    tesseract._tessdata_dir = "/mock/tessdata"

    tesseract._record_backend_info(mock_api)

    info = tesseract.get_ocr_backend_info()
    assert info is not None
    assert info.tesseract_version == "1.2.3"
    assert info.tessdata_dir == "/mock/tessdata"
    assert info.languages == ["eng", "fra"]


def test_record_backend_info_no_version_attr():
    mock_api = MagicMock(spec=["GetAvailableLanguages"])
    mock_api.GetAvailableLanguages.return_value = ["eng"]

    tesseract._tessdata_dir = "/mock/tessdata"
    tesseract._record_backend_info(mock_api)

    info = tesseract.get_ocr_backend_info()
    assert info is not None
    assert info.tesseract_version == ""


@patch("src.autoscrapper.ocr.tesseract._get_api")
@patch("src.autoscrapper.ocr.tesseract._get_api_line")
@patch("src.autoscrapper.ocr.tesseract._record_backend_info")
def test_initialize_ocr(mock_record, mock_get_line, mock_get):
    mock_api = MagicMock()
    mock_get.return_value = mock_api

    # We need to simulate setting the backend info since the mock won't do it
    tesseract._backend_info = OcrBackendInfo("1.0", "/path", ["eng"])

    info = tesseract.initialize_ocr()

    assert info is not None
    assert info.tesseract_version == "1.0"
    mock_get.assert_called_once()
    mock_get_line.assert_called_once()
    mock_record.assert_called_once_with(mock_api)


@patch("src.autoscrapper.ocr.tesseract._create_api")
@patch("src.autoscrapper.ocr.tesseract._record_backend_info")
def test_get_api_creates_instance(mock_record, mock_create):
    mock_api = MagicMock()
    mock_create.return_value = mock_api

    api = tesseract._get_api()

    assert api == mock_api
    mock_create.assert_called_once_with()
    mock_record.assert_called_once_with(mock_api)


@patch("src.autoscrapper.ocr.tesseract._create_api")
@patch("src.autoscrapper.ocr.tesseract._record_backend_info")
def test_get_api_line_creates_instance(mock_record, mock_create):
    mock_api = MagicMock()
    mock_create.return_value = mock_api

    api = tesseract._get_api_line()

    assert api == mock_api
    mock_create.assert_called_once_with(psm=tesseract.PSM.SINGLE_LINE)
    mock_record.assert_called_once_with(mock_api)


@patch("src.autoscrapper.ocr.tesseract._get_api_line")
def test_image_to_string_single_line(mock_get_api_line):
    mock_api = MagicMock()
    mock_api.GetUTF8Text.return_value = "Line Text"
    mock_get_api_line.return_value = mock_api

    img = np.zeros((10, 10), dtype=np.uint8)
    text = tesseract.image_to_string(img, single_line=True)

    assert text == "Line Text"
    mock_api.SetImage.assert_called_once()


@patch("src.autoscrapper.ocr.tesseract._get_api_line")
def test_image_to_data_single_line(mock_get_api_line):
    mock_api = MagicMock()
    mock_api.GetIterator.return_value = None
    mock_get_api_line.return_value = mock_api

    img = np.zeros((10, 10), dtype=np.uint8)
    data = tesseract.image_to_data(img, single_line=True)

    assert data == _empty_data_dict()
    mock_api.SetImage.assert_called_once()


def test_record_backend_info_already_set():
    mock_api = MagicMock()
    # We should return early if backend_info is already set
    tesseract._backend_info = OcrBackendInfo("1.0", "/path", ["eng"])

    tesseract._record_backend_info(mock_api)

    # Verify no calls were made to mock_api
    mock_api.Version.assert_not_called()


@patch("src.autoscrapper.ocr.tesseract._get_api_line")
@patch("src.autoscrapper.ocr.tesseract._get_api")
def test_image_to_data_with_iterator(mock_get_api, mock_get_api_line):
    # This tests the full path from image_to_data down to _build_data_dict
    mock_api = MagicMock()
    mock_get_api.return_value = mock_api

    mock_iterator = MagicMock()
    mock_api.GetIterator.return_value = mock_iterator

    mock_word = MagicMock()
    mock_word.IsAtBeginningOf.side_effect = lambda level: level in (tesseract.RIL.BLOCK, tesseract.RIL.PARA, tesseract.RIL.TEXTLINE)
    mock_word.BoundingBox.return_value = (10, 10, 100, 30)
    mock_word.Confidence.return_value = 95.5
    mock_word.GetUTF8Text.return_value = "TestWord"

    img = np.zeros((10, 10), dtype=np.uint8)

    with patch("src.autoscrapper.ocr.tesseract.iterate_level", return_value=[mock_word]):
        data = tesseract.image_to_data(img)

    assert data["text"][0] == "TestWord"
    mock_api.SetImage.assert_called_once()
    mock_api.Recognize.assert_called_once()
    mock_api.GetIterator.assert_called_once()


def test_build_data_dict_no_bbox():
    mock_word = MagicMock()
    mock_word.IsAtBeginningOf.side_effect = lambda level: level in (tesseract.RIL.BLOCK, tesseract.RIL.PARA, tesseract.RIL.TEXTLINE)
    mock_word.BoundingBox.return_value = None
    mock_word.Confidence.return_value = 95.5
    mock_word.GetUTF8Text.return_value = "TestWord"

    with patch("src.autoscrapper.ocr.tesseract.iterate_level", return_value=[mock_word]):
        data = tesseract._build_data_dict(MagicMock())

        # Word should be skipped if bbox is None
        assert len(data["text"]) == 0

def test_build_data_dict_none_confidence():
    mock_word = MagicMock()
    mock_word.IsAtBeginningOf.side_effect = lambda level: level in (tesseract.RIL.BLOCK, tesseract.RIL.PARA, tesseract.RIL.TEXTLINE)
    mock_word.BoundingBox.return_value = (10, 10, 100, 30)
    mock_word.Confidence.return_value = None
    mock_word.GetUTF8Text.return_value = "TestWord"

    with patch("src.autoscrapper.ocr.tesseract.iterate_level", return_value=[mock_word]):
        data = tesseract._build_data_dict(MagicMock())

        assert len(data["text"]) == 1
        assert data["conf"][0] == "-1"

def test_build_data_dict_none_text():
    mock_word = MagicMock()
    mock_word.IsAtBeginningOf.side_effect = lambda level: level in (tesseract.RIL.BLOCK, tesseract.RIL.PARA, tesseract.RIL.TEXTLINE)
    mock_word.BoundingBox.return_value = (10, 10, 100, 30)
    mock_word.Confidence.return_value = 95.5
    mock_word.GetUTF8Text.return_value = None

    with patch("src.autoscrapper.ocr.tesseract.iterate_level", return_value=[mock_word]):
        data = tesseract._build_data_dict(MagicMock())

        assert len(data["text"]) == 1
        assert data["text"][0] == ""

def test_get_api_already_initialized():
    mock_api = MagicMock()
    tesseract._api = mock_api

    assert tesseract._get_api() == mock_api

def test_get_api_line_already_initialized():
    mock_api = MagicMock()
    tesseract._api_line = mock_api

    assert tesseract._get_api_line() == mock_api

def test_candidate_tessdata_paths_exception_in_tessdata_data_path():
    with patch.dict(os.environ, clear=True):
        with patch("tessdata.data_path", side_effect=Exception("mock error")):
            with patch("src.autoscrapper.ocr.tesseract.tessdata.__file__", "/mock/pkg/tessdata/__init__.py"):
                paths = tesseract._candidate_tessdata_paths()

                # Should not include tessdata.data_path since it threw an exception
                assert Path("/mock/pkg/share/tessdata") in paths

@patch("src.autoscrapper.ocr.tesseract._get_api")
@patch("src.autoscrapper.ocr.tesseract._get_api_line")
def test_image_to_string_exception(mock_get_api_line, mock_get_api):
    mock_api = MagicMock()
    mock_api.GetUTF8Text.side_effect = Exception("OCR failed")
    mock_get_api.return_value = mock_api

    img = np.zeros((10, 10), dtype=np.uint8)
    with pytest.raises(Exception, match="OCR failed"):
        tesseract.image_to_string(img)

@patch("src.autoscrapper.ocr.tesseract._get_api")
@patch("src.autoscrapper.ocr.tesseract._get_api_line")
def test_image_to_data_exception(mock_get_api_line, mock_get_api):
    mock_api = MagicMock()
    mock_api.GetIterator.side_effect = Exception("OCR failed")
    mock_get_api.return_value = mock_api

    img = np.zeros((10, 10), dtype=np.uint8)
    with pytest.raises(Exception, match="OCR failed"):
        tesseract.image_to_data(img)

def test_build_data_dict_all_levels():
    mock_word = MagicMock()
    # Let IsAtBeginningOf return True for all levels when we pass them
    mock_word.IsAtBeginningOf.return_value = True
    mock_word.BoundingBox.return_value = (10, 10, 100, 30)
    mock_word.Confidence.return_value = 95.5
    mock_word.GetUTF8Text.return_value = "TestWord"

    with patch("src.autoscrapper.ocr.tesseract.iterate_level", return_value=[mock_word, mock_word]):
        data = tesseract._build_data_dict(MagicMock())

        assert len(data["text"]) == 2
        # First word
        assert data["block_num"][0] == 1
        assert data["par_num"][0] == 1
        assert data["line_num"][0] == 1
        assert data["word_num"][0] == 1
        # Second word (everything resets to 1, word_num to 1 since line reset)
        assert data["block_num"][1] == 2
        assert data["par_num"][1] == 1
        assert data["line_num"][1] == 1
        assert data["word_num"][1] == 1

def test_initialize_ocr_without_metadata():
    with patch("src.autoscrapper.ocr.tesseract._get_api"), \
         patch("src.autoscrapper.ocr.tesseract._get_api_line"), \
         patch("src.autoscrapper.ocr.tesseract._record_backend_info"):

        # Ensure _backend_info remains None
        tesseract._backend_info = None

        with pytest.raises(RuntimeError, match="OCR backend initialized but metadata is missing"):
            tesseract.initialize_ocr()
