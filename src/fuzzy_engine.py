"""Yol Hasar Müdahale Önceliği Sistemi - Mamdani bulanık çıkarım motoru.

Bu modül, Streamlit arayüzünden bağımsız olarak çalışır. Böylece hem test edilebilir
hem de ileride farklı arayüzlere kolayca entegre edilebilir.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import numpy as np


Number = float | int


@dataclass(frozen=True)
class FuzzySet:
    """Tek bir bulanık kümenin üyelik fonksiyonu tanımı."""

    name: str
    kind: str
    points: Tuple[float, ...]

    def membership(self, x: np.ndarray | Number) -> np.ndarray | float:
        if self.kind == "trimf":
            return trimf(x, self.points)
        if self.kind == "trapmf":
            return trapmf(x, self.points)
        raise ValueError(f"Bilinmeyen üyelik fonksiyonu türü: {self.kind}")


@dataclass(frozen=True)
class Rule:
    """Mamdani tipinde bir IF-THEN kuralı."""

    damage: str
    traffic: str
    accident: str
    output: str
    explanation: str

    def label(self) -> str:
        return (
            f"EĞER hasar şiddeti {self.damage}, yol kullanım yoğunluğu {self.traffic} "
            f"ve kaza riski {self.accident} İSE müdahale önceliği {self.output}."
        )


# Evrensel kümeler
DAMAGE_UNIVERSE = np.arange(0, 101, 1)
TRAFFIC_UNIVERSE = np.arange(0, 101, 1)
ACCIDENT_UNIVERSE = np.arange(0, 101, 1)
PRIORITY_UNIVERSE = np.arange(0, 101, 1)


INPUT_SETS: Dict[str, Dict[str, FuzzySet]] = {
    "damage": {
        "Düşük": FuzzySet("Düşük", "trapmf", (0, 0, 20, 40)),
        "Orta": FuzzySet("Orta", "trimf", (25, 50, 75)),
        "Yüksek": FuzzySet("Yüksek", "trapmf", (60, 80, 100, 100)),
    },
    "traffic": {
        "Düşük": FuzzySet("Düşük", "trapmf", (0, 0, 20, 45)),
        "Orta": FuzzySet("Orta", "trimf", (30, 55, 80)),
        "Yüksek": FuzzySet("Yüksek", "trapmf", (65, 85, 100, 100)),
    },
    "accident": {
        "Düşük": FuzzySet("Düşük", "trapmf", (0, 0, 20, 40)),
        "Orta": FuzzySet("Orta", "trimf", (25, 50, 75)),
        "Yüksek": FuzzySet("Yüksek", "trapmf", (60, 80, 100, 100)),
    },
}


OUTPUT_SETS: Dict[str, FuzzySet] = {
    "Düşük": FuzzySet("Düşük", "trapmf", (0, 0, 15, 35)),
    "Orta": FuzzySet("Orta", "trimf", (25, 45, 65)),
    "Yüksek": FuzzySet("Yüksek", "trimf", (55, 70, 85)),
    "Kritik": FuzzySet("Kritik", "trapmf", (75, 90, 100, 100)),
}


# 27 kural: 3x3x3 kombinasyonun tamamı kapsanır. Proje şartındaki 15 kural sınırı aşılmıştır.
RULES: List[Rule] = [
    Rule("Düşük", "Düşük", "Düşük", "Düşük", "Hasar ve risk düşük olduğu için rutin takip yeterlidir."),
    Rule("Düşük", "Düşük", "Orta", "Düşük", "Risk orta olsa da yol kullanımı ve hasar sınırlıdır."),
    Rule("Düşük", "Düşük", "Yüksek", "Orta", "Kaza riski yüksek olduğu için düşük hasara rağmen takip önceliği artar."),
    Rule("Düşük", "Orta", "Düşük", "Düşük", "Orta yoğunluk tek başına yüksek müdahale gerektirmez."),
    Rule("Düşük", "Orta", "Orta", "Orta", "Yoğunluk ve risk birlikte orta seviyede öncelik üretir."),
    Rule("Düşük", "Orta", "Yüksek", "Yüksek", "Kaza riski yüksek olduğunda düşük hasar dahi güvenlik açısından önem kazanır."),
    Rule("Düşük", "Yüksek", "Düşük", "Orta", "Yol yoğunluğu yüksek olduğu için düşük hasarlı nokta daha görünür hale gelir."),
    Rule("Düşük", "Yüksek", "Orta", "Yüksek", "Yoğun kullanım ve orta risk müdahaleyi hızlandırır."),
    Rule("Düşük", "Yüksek", "Yüksek", "Yüksek", "Yoğun yol ve yüksek risk, hasar düşük olsa bile yüksek öncelik doğurur."),
    Rule("Orta", "Düşük", "Düşük", "Orta", "Orta hasar güvenlik açısından göz ardı edilmemelidir."),
    Rule("Orta", "Düşük", "Orta", "Orta", "Hasar ve risk orta düzeyde olduğundan planlı müdahale uygundur."),
    Rule("Orta", "Düşük", "Yüksek", "Yüksek", "Yüksek kaza riski orta hasarı acil sınıfa yaklaştırır."),
    Rule("Orta", "Orta", "Düşük", "Orta", "Hasar ve kullanım orta düzeyde olduğundan öncelik orta kalır."),
    Rule("Orta", "Orta", "Orta", "Yüksek", "Üç değişkenin orta düzeyde birleşmesi sahada belirgin öncelik oluşturur."),
    Rule("Orta", "Orta", "Yüksek", "Yüksek", "Kaza riski yüksekse müdahale önceliği yükseltilir."),
    Rule("Orta", "Yüksek", "Düşük", "Yüksek", "Yoğun kullanılan yoldaki orta hasar hizmet kalitesini düşürür."),
    Rule("Orta", "Yüksek", "Orta", "Yüksek", "Orta risk ve yüksek yoğunluk güçlü öncelik üretir."),
    Rule("Orta", "Yüksek", "Yüksek", "Kritik", "Yoğun kullanım ve yüksek risk kritik müdahale gerektirir."),
    Rule("Yüksek", "Düşük", "Düşük", "Yüksek", "Yüksek hasar az yoğun yolda bile yapısal risk taşır."),
    Rule("Yüksek", "Düşük", "Orta", "Yüksek", "Yüksek hasar ve orta risk acil olmayan fakat yüksek öncelikli müdahale gerektirir."),
    Rule("Yüksek", "Düşük", "Yüksek", "Kritik", "Hasar ve kaza riski birlikte kritik seviyeye çıkar."),
    Rule("Yüksek", "Orta", "Düşük", "Yüksek", "Orta yoğunlukta yüksek hasar güvenlik ve konforu azaltır."),
    Rule("Yüksek", "Orta", "Orta", "Kritik", "Yüksek hasar, orta yoğunluk ve orta risk kritik karar oluşturur."),
    Rule("Yüksek", "Orta", "Yüksek", "Kritik", "Yüksek hasar ve yüksek risk acil müdahaleyi zorunlu kılar."),
    Rule("Yüksek", "Yüksek", "Düşük", "Kritik", "Yüksek hasarlı ve yoğun kullanılan yol hızlı onarım gerektirir."),
    Rule("Yüksek", "Yüksek", "Orta", "Kritik", "Yoğun kullanım ve yüksek hasar, orta riskle bile kritik sonuç verir."),
    Rule("Yüksek", "Yüksek", "Yüksek", "Kritik", "Üç değişkenin yüksek olması en üst düzey müdahale önceliğidir."),
]


def trimf(x: np.ndarray | Number, abc: Tuple[float, ...]) -> np.ndarray | float:
    """Üçgen üyelik fonksiyonu."""
    a, b, c = abc
    x_arr = np.asarray(x, dtype=float)
    y = np.zeros_like(x_arr, dtype=float)

    left = (a < x_arr) & (x_arr < b)
    right = (b < x_arr) & (x_arr < c)
    y[x_arr == b] = 1.0
    y[left] = (x_arr[left] - a) / (b - a)
    y[right] = (c - x_arr[right]) / (c - b)
    y = np.clip(y, 0, 1)
    return float(y) if np.isscalar(x) else y


def trapmf(x: np.ndarray | Number, abcd: Tuple[float, ...]) -> np.ndarray | float:
    """Yamuk üyelik fonksiyonu."""
    a, b, c, d = abcd
    x_arr = np.asarray(x, dtype=float)
    y = np.zeros_like(x_arr, dtype=float)

    if b != a:
        left = (a < x_arr) & (x_arr < b)
        y[left] = (x_arr[left] - a) / (b - a)
    else:
        y[(x_arr >= a) & (x_arr <= c)] = 1.0

    plateau = (b <= x_arr) & (x_arr <= c)
    y[plateau] = 1.0

    if d != c:
        right = (c < x_arr) & (x_arr < d)
        y[right] = (d - x_arr[right]) / (d - c)
    else:
        y[(x_arr >= b) & (x_arr <= d)] = 1.0

    y = np.clip(y, 0, 1)
    return float(y) if np.isscalar(x) else y


def fuzzify_inputs(damage: Number, traffic: Number, accident: Number) -> Dict[str, Dict[str, float]]:
    """Keskin giriş değerlerini bulanık üyelik derecelerine dönüştürür."""
    values = {"damage": float(damage), "traffic": float(traffic), "accident": float(accident)}
    _validate_range(values)
    return {
        variable: {label: float(fuzzy_set.membership(values[variable])) for label, fuzzy_set in sets.items()}
        for variable, sets in INPUT_SETS.items()
    }


def evaluate_rules(memberships: Dict[str, Dict[str, float]]) -> List[Dict[str, object]]:
    """Kuralları min operatörüyle değerlendirir."""
    evaluations: List[Dict[str, object]] = []
    for rule in RULES:
        activation = min(
            memberships["damage"][rule.damage],
            memberships["traffic"][rule.traffic],
            memberships["accident"][rule.accident],
        )
        evaluations.append(
            {
                "rule": rule,
                "activation": float(activation),
                "output": rule.output,
                "label": rule.label(),
                "explanation": rule.explanation,
            }
        )
    return evaluations


def aggregate_outputs(rule_evaluations: Iterable[Dict[str, object]]) -> np.ndarray:
    """Aktif kuralların çıktısını max-min birleşimi ile toplulaştırır."""
    aggregated = np.zeros_like(PRIORITY_UNIVERSE, dtype=float)
    for evaluation in rule_evaluations:
        activation = float(evaluation["activation"])
        if activation <= 0:
            continue
        output_label = str(evaluation["output"])
        consequent = OUTPUT_SETS[output_label].membership(PRIORITY_UNIVERSE)
        clipped = np.fmin(activation, consequent)
        aggregated = np.fmax(aggregated, clipped)
    return aggregated


def centroid(universe: np.ndarray, membership_values: np.ndarray) -> float:
    """Ağırlık merkezi yöntemiyle durulaştırma yapar."""
    denominator = np.sum(membership_values)
    if denominator == 0:
        return 0.0
    return float(np.sum(universe * membership_values) / denominator)


def classify_priority(score: float) -> str:
    """Sayısal öncelik skorunu sözel sınıfa çevirir."""
    if score < 35:
        return "Düşük"
    if score < 60:
        return "Orta"
    if score < 78:
        return "Yüksek"
    return "Kritik"


def calculate_priority(damage: Number, traffic: Number, accident: Number) -> Dict[str, object]:
    """Tam bulanık kontrolcü hesaplama akışını yürütür."""
    memberships = fuzzify_inputs(damage, traffic, accident)
    rule_evaluations = evaluate_rules(memberships)
    aggregated = aggregate_outputs(rule_evaluations)
    score = centroid(PRIORITY_UNIVERSE, aggregated)
    active_rules = [item for item in rule_evaluations if float(item["activation"]) > 0]
    active_rules.sort(key=lambda item: float(item["activation"]), reverse=True)
    return {
        "score": round(score, 2),
        "class": classify_priority(score),
        "memberships": memberships,
        "rule_evaluations": rule_evaluations,
        "active_rules": active_rules,
        "aggregated": aggregated,
        "universe": PRIORITY_UNIVERSE,
    }


def membership_table(variable: str) -> Dict[str, np.ndarray]:
    """Grafikler için seçilen değişkenin üyelik eğrilerini döndürür."""
    if variable == "priority":
        return {label: fset.membership(PRIORITY_UNIVERSE) for label, fset in OUTPUT_SETS.items()}
    if variable not in INPUT_SETS:
        raise KeyError(f"Bilinmeyen değişken: {variable}")
    universe_map = {
        "damage": DAMAGE_UNIVERSE,
        "traffic": TRAFFIC_UNIVERSE,
        "accident": ACCIDENT_UNIVERSE,
    }
    universe = universe_map[variable]
    return {label: fset.membership(universe) for label, fset in INPUT_SETS[variable].items()}


def get_universe(variable: str) -> np.ndarray:
    if variable == "damage":
        return DAMAGE_UNIVERSE
    if variable == "traffic":
        return TRAFFIC_UNIVERSE
    if variable == "accident":
        return ACCIDENT_UNIVERSE
    if variable == "priority":
        return PRIORITY_UNIVERSE
    raise KeyError(f"Bilinmeyen değişken: {variable}")


def run_sample_scenarios() -> List[Dict[str, object]]:
    scenarios = [
        (15, 20, 10, "Rutin takip senaryosu"),
        (35, 75, 60, "Yoğun yolda orta hasar"),
        (70, 40, 80, "Riskli bölgede yüksek hasar"),
        (90, 90, 85, "Acil müdahale gerektiren kritik yol"),
        (55, 55, 55, "Dengeli orta seviye senaryo"),
    ]
    output = []
    for damage, traffic, accident, name in scenarios:
        result = calculate_priority(damage, traffic, accident)
        output.append(
            {
                "Senaryo": name,
                "Hasar Şiddeti": damage,
                "Yol Kullanım Yoğunluğu": traffic,
                "Kaza Riski": accident,
                "Öncelik Skoru": result["score"],
                "Sınıf": result["class"],
                "Aktif Kural Sayısı": len(result["active_rules"]),
            }
        )
    return output


def _validate_range(values: Dict[str, float]) -> None:
    for key, value in values.items():
        if not 0 <= value <= 100:
            raise ValueError(f"{key} değeri 0-100 aralığında olmalıdır. Gelen değer: {value}")


if __name__ == "__main__":
    demo = calculate_priority(85, 90, 80)
    print(f"Öncelik skoru: {demo['score']} / Sınıf: {demo['class']}")
    print("Aktif kural sayısı:", len(demo["active_rules"]))
