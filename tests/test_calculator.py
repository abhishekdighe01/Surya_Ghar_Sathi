import pytest

from app.tools import solar_cfa_calculator


def test_calculator_1kw():
    res = solar_cfa_calculator(capacity_kw=1.0, monthly_bill=2000.0, available_terrace_sqm=40.0)
    assert res["eligible_subsidy_inr"] == 30000.0
    assert res["required_terrace_sqm"] == 10.0
    assert res["is_area_sufficient"] is True


def test_calculator_2kw():
    res = solar_cfa_calculator(capacity_kw=2.0, monthly_bill=2000.0, available_terrace_sqm=40.0)
    assert res["eligible_subsidy_inr"] == 60000.0
    assert res["required_terrace_sqm"] == 20.0
    assert res["is_area_sufficient"] is True


def test_calculator_3kw_kopargaon_benchmark():
    res = solar_cfa_calculator(capacity_kw=3.0, monthly_bill=2000.0, available_terrace_sqm=40.0)
    assert res["eligible_subsidy_inr"] == 78000.0
    assert res["net_cost_to_consumer_inr"] == 72000.0
    assert res["required_terrace_sqm"] == 30.0
    assert res["is_area_sufficient"] is True
    assert res["payback_period_years"] == 3.0


def test_calculator_above_3kw_capped():
    res_5kw = solar_cfa_calculator(capacity_kw=5.0, monthly_bill=3500.0, available_terrace_sqm=40.0)
    assert res_5kw["eligible_subsidy_inr"] == 78000.0  # Capped at ₹78,000
    assert res_5kw["required_terrace_sqm"] == 50.0
    assert res_5kw["is_area_sufficient"] is False      # 50 sq m needed > 40 sq m available


def test_calculator_invalid_capacity():
    with pytest.raises(ValueError):
        solar_cfa_calculator(capacity_kw=0.0)

    with pytest.raises(ValueError):
        solar_cfa_calculator(capacity_kw=-2.5)
