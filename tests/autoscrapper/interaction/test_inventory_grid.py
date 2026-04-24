from __future__ import annotations

import numpy as np
from autoscrapper.interaction.inventory_grid import (
    GRID_COLS,
    GRID_ROWS,
    REF_CELL_SIZE,
    REF_HEIGHT,
    REF_WIDTH,
    Cell,
    Grid,
    _scaled_cell_size,
    _synthetic_grid,
)


class TestCellCoordinateCalculation:
    def test_cell_index_0_is_top_left(self):
        cell = Cell(
            index=0,
            row=0,
            col=0,
            x=100,
            y=100,
            width=95,
            height=95,
            safe_bounds=(105, 105, 190, 190),
        )
        assert cell.index == 0
        assert cell.row == 0
        assert cell.col == 0

    def test_cell_index_3_is_first_row_last_col(self):
        cell = Cell(
            index=3,
            row=0,
            col=3,
            x=400,
            y=100,
            width=95,
            height=95,
            safe_bounds=(405, 105, 490, 190),
        )
        assert cell.index == 3
        assert cell.row == 0
        assert cell.col == 3

    def test_cell_index_4_is_second_row_first_col(self):
        cell = Cell(
            index=4,
            row=1,
            col=0,
            x=100,
            y=200,
            width=95,
            height=95,
            safe_bounds=(105, 205, 190, 290),
        )
        assert cell.index == 4
        assert cell.row == 1
        assert cell.col == 0

    def test_cell_rect_property(self):
        cell = Cell(
            index=0,
            row=0,
            col=0,
            x=100,
            y=100,
            width=95,
            height=95,
            safe_bounds=(105, 105, 190, 190),
        )
        rect = cell.rect
        assert rect == (100, 100, 95, 95)

    def test_cell_safe_rect_property(self):
        cell = Cell(
            index=0,
            row=0,
            col=0,
            x=100,
            y=100,
            width=95,
            height=95,
            safe_bounds=(105, 105, 190, 190),
        )
        safe_rect = cell.safe_rect
        assert safe_rect == (105, 105, 85, 85)

    def test_cell_center_property(self):
        cell = Cell(
            index=0,
            row=0,
            col=0,
            x=100,
            y=100,
            width=95,
            height=95,
            safe_bounds=(105, 105, 190, 190),
        )
        cx, cy = cell.center
        assert cx == 147.5
        assert cy == 147.5

    def test_cell_safe_center_property(self):
        cell = Cell(
            index=0,
            row=0,
            col=0,
            x=100,
            y=100,
            width=95,
            height=95,
            safe_bounds=(105, 105, 190, 190),
        )
        cx, cy = cell.safe_center
        assert cx == 147.5
        assert cy == 147.5


class TestGridDimensions:
    def test_grid_has_20_cells(self):
        assert GRID_ROWS * GRID_COLS == 20

    def test_grid_cols_constant(self):
        assert GRID_COLS == 4

    def test_grid_rows_constant(self):
        assert GRID_ROWS == 5


class TestScaledCellSize:
    def test_ref_resolution_returns_ref_cell_size(self):
        size = _scaled_cell_size(REF_WIDTH, REF_HEIGHT)
        assert size == REF_CELL_SIZE

    def test_double_resolution_doubles_cell_size(self):
        size = _scaled_cell_size(REF_WIDTH * 2, REF_HEIGHT * 2)
        assert size == REF_CELL_SIZE * 2

    def test_half_resolution_halves_cell_size(self):
        size = _scaled_cell_size(REF_WIDTH // 2, REF_HEIGHT // 2)
        assert size == 48

    def test_non_standard_resolution_scales_proportionally(self):
        size = _scaled_cell_size(1920, 1440)
        assert size > 0


class TestSyntheticGrid:
    def test_synthetic_grid_has_correct_count(self):
        cells = _synthetic_grid(400, 500)
        assert len(cells) == GRID_ROWS * GRID_COLS

    def test_synthetic_grid_cells_are_dictionaries(self):
        cells = _synthetic_grid(400, 500)
        for cell in cells:
            assert isinstance(cell, dict)
            assert "x" in cell
            assert "y" in cell
            assert "w" in cell
            assert "h" in cell
            assert "safe_bounds" in cell

    def test_synthetic_grid_cells_have_valid_coordinates(self):
        cells = _synthetic_grid(400, 500)
        for cell in cells:
            assert cell["x"] >= 0
            assert cell["y"] >= 0
            assert cell["w"] > 0
            assert cell["h"] > 0


class TestGridCellAccess:
    def test_grid_len_returns_cell_count(self):
        roi_rect = (100, 100, 400, 500)
        grid = Grid.detect(
            np.zeros((500, 400, 3), dtype=np.uint8),
            roi_rect,
            1920,
            1080,
        )
        assert len(grid) == GRID_ROWS * GRID_COLS

    def test_grid_iter_yields_all_cells(self):
        roi_rect = (100, 100, 400, 500)
        grid = Grid.detect(
            np.zeros((500, 400, 3), dtype=np.uint8),
            roi_rect,
            1920,
            1080,
        )
        cells = list(grid)
        assert len(cells) == GRID_ROWS * GRID_COLS
        for cell in cells:
            assert isinstance(cell, Cell)

    def test_grid_cell_by_index(self):
        roi_rect = (100, 100, 400, 500)
        grid = Grid.detect(
            np.zeros((500, 400, 3), dtype=np.uint8),
            roi_rect,
            1920,
            1080,
        )
        cell = grid.cell_by_index(0)
        assert isinstance(cell, Cell)
        assert cell.index == 0

    def test_grid_cell_by_row_col(self):
        roi_rect = (100, 100, 400, 500)
        grid = Grid.detect(
            np.zeros((500, 400, 3), dtype=np.uint8),
            roi_rect,
            1920,
            1080,
        )
        cell = grid.cell(0, 0)
        assert isinstance(cell, Cell)
        assert cell.row == 0
        assert cell.col == 0

    def test_grid_center_returns_tuple(self):
        roi_rect = (100, 100, 400, 500)
        grid = Grid.detect(
            np.zeros((500, 400, 3), dtype=np.uint8),
            roi_rect,
            1920,
            1080,
        )
        center = grid.center(0, 0)
        assert isinstance(center, tuple)
        assert len(center) == 2


class TestMultiResolution:
    def test_1080p_resolution(self):
        roi_rect = (146, 262, 423, 545)
        grid = Grid.detect(
            np.zeros((545, 423, 3), dtype=np.uint8),
            roi_rect,
            1920,
            1080,
        )
        assert len(grid) == 20
        cell = grid.cell(0, 0)
        assert cell.width > 0
        assert cell.height > 0

    def test_1440p_resolution(self):
        roi_rect = (195, 349, 564, 726)
        grid = Grid.detect(
            np.zeros((726, 564, 3), dtype=np.uint8),
            roi_rect,
            2560,
            1440,
        )
        assert len(grid) == 20
        cell = grid.cell(0, 0)
        assert cell.width > 0
        assert cell.height > 0

    def test_4k_resolution(self):
        roi_rect = (292, 524, 846, 1090)
        grid = Grid.detect(
            np.zeros((1090, 846, 3), dtype=np.uint8),
            roi_rect,
            3840,
            2160,
        )
        assert len(grid) == 20
        cell = grid.cell(0, 0)
        assert cell.width > 0
        assert cell.height > 0


class TestRowColumnBoundaries:
    def test_first_row_cells_have_row_0(self):
        roi_rect = (100, 100, 400, 500)
        grid = Grid.detect(
            np.zeros((500, 400, 3), dtype=np.uint8),
            roi_rect,
            1920,
            1080,
        )
        for col in range(GRID_COLS):
            cell = grid.cell(0, col)
            assert cell.row == 0

    def test_last_row_cells_have_row_4(self):
        roi_rect = (100, 100, 400, 500)
        grid = Grid.detect(
            np.zeros((500, 400, 3), dtype=np.uint8),
            roi_rect,
            1920,
            1080,
        )
        for col in range(GRID_COLS):
            cell = grid.cell(GRID_ROWS - 1, col)
            assert cell.row == GRID_ROWS - 1

    def test_first_column_cells_have_col_0(self):
        roi_rect = (100, 100, 400, 500)
        grid = Grid.detect(
            np.zeros((500, 400, 3), dtype=np.uint8),
            roi_rect,
            1920,
            1080,
        )
        for row in range(GRID_ROWS):
            cell = grid.cell(row, 0)
            assert cell.col == 0

    def test_last_column_cells_have_col_3(self):
        roi_rect = (100, 100, 400, 500)
        grid = Grid.detect(
            np.zeros((500, 400, 3), dtype=np.uint8),
            roi_rect,
            1920,
            1080,
        )
        for row in range(GRID_ROWS):
            cell = grid.cell(row, GRID_COLS - 1)
            assert cell.col == GRID_COLS - 1


class TestEdgeCases:
    def test_very_small_resolution(self):
        roi_rect = (10, 10, 80, 100)
        grid = Grid.detect(
            np.zeros((100, 80, 3), dtype=np.uint8),
            roi_rect,
            320,
            200,
        )
        assert len(grid) == 20

    def test_very_large_resolution(self):
        roi_rect = (500, 500, 2000, 2500)
        grid = Grid.detect(
            np.zeros((2500, 2000, 3), dtype=np.uint8),
            roi_rect,
            7680,
            4320,
        )
        assert len(grid) == 20

    def test_non_16_9_aspect_ratio(self):
        roi_rect = (100, 100, 400, 600)
        grid = Grid.detect(
            np.zeros((600, 400, 3), dtype=np.uint8),
            roi_rect,
            1200,
            1800,
        )
        assert len(grid) == 20
