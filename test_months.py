from months import month_weeks, shift_month


def test_november_2026_starts_on_sunday():
    weeks = month_weeks(2026, 11)
    assert weeks[0] == [0, 0, 0, 0, 0, 0, 1]


def test_november_2026_has_six_weeks_and_ends_on_30():
    weeks = month_weeks(2026, 11)
    assert len(weeks) == 6
    assert weeks[-1][0] == 30


def test_shift_forward_across_year():
    assert shift_month(2026, 12, 1) == (2027, 1)


def test_shift_back_across_year():
    assert shift_month(2026, 1, -1) == (2025, 12)


def test_shift_zero_changes_nothing():
    assert shift_month(2026, 11, 0) == (2026, 11)
