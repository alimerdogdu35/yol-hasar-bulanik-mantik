"""Basit doğrulama testleri.

Çalıştırma:
    python -m pytest tests/test_engine.py
"""
from src.fuzzy_engine import calculate_priority, fuzzify_inputs, run_sample_scenarios


def test_priority_low_scenario():
    result = calculate_priority(10, 10, 10)
    assert 0 <= result["score"] <= 100
    assert result["class"] == "Düşük"


def test_priority_critical_scenario():
    result = calculate_priority(95, 90, 90)
    assert result["score"] >= 75
    assert result["class"] == "Kritik"


def test_membership_values_are_valid():
    memberships = fuzzify_inputs(50, 50, 50)
    for variable_memberships in memberships.values():
        for degree in variable_memberships.values():
            assert 0 <= degree <= 1


def test_sample_scenarios_exist():
    scenarios = run_sample_scenarios()
    assert len(scenarios) >= 5
    assert all("Öncelik Skoru" in row for row in scenarios)
