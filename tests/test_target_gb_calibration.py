from data_generator.generate import rows_for_target_gb


def test_rows_for_target_gb_is_zero_at_zero():
    assert rows_for_target_gb(0) == 0


def test_rows_for_target_gb_scales_roughly_linearly():
    small = rows_for_target_gb(1)
    large = rows_for_target_gb(10)
    assert small > 0
    assert 9.9 <= large / small <= 10.1
