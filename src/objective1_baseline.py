import argparse
from typing import List

import fastf1
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


FEATURE_COLUMNS = ["Speed", "RPM", "nGear", "Throttle", "Brake", "DRS"]


def lap_to_seconds(value) -> float:
    if pd.isna(value):
        return np.nan
    return value.total_seconds()


def interpolate_telemetry(lap, points: int) -> np.ndarray | None:
    try:
        telemetry = lap.get_car_data().add_distance()
    except Exception:
        return None

    if telemetry.empty:
        return None

    max_distance = float(telemetry["Distance"].max())
    if max_distance <= 0:
        return None

    distance_grid = np.linspace(0.0, max_distance, points)
    vectors = []

    for col in FEATURE_COLUMNS:
        col_data = telemetry[["Distance", col]].dropna()
        if len(col_data) < 2:
            return None
        interpolated = np.interp(distance_grid, col_data["Distance"], col_data[col])
        vectors.append(interpolated)

    return np.concatenate(vectors, axis=0)


def build_dataset(year: int, rounds: List[int], max_laps: int, points: int) -> pd.DataFrame:
    cache_dir = "data/raw"
    fastf1.Cache.enable_cache(cache_dir)

    rows = []

    for round_number in rounds:
        print(f"\nLoading year={year}, round={round_number}, session=Race ...")
        session = fastf1.get_session(year, round_number, "R")
        session.load()

        laps = session.laps.copy()
        laps = laps[laps["IsAccurate"] == True]
        laps = laps[laps["Deleted"] == False]
        laps = laps[laps["PitOutTime"].isna() & laps["PitInTime"].isna()]
        laps = laps.dropna(subset=["Driver", "LapTime"])
        laps = laps.head(max_laps)

        for _, lap in laps.iterrows():
            telemetry_vector = interpolate_telemetry(lap, points)
            if telemetry_vector is None:
                continue

            weather = lap.get_weather_data()

            row = {
                "driver_label": lap["Driver"],
                "circuit_label": session.event["EventName"],
                "round_number": int(round_number),
                "lap_time_s": lap_to_seconds(lap["LapTime"]),
                "sector1_s": lap_to_seconds(lap["Sector1Time"]),
                "sector2_s": lap_to_seconds(lap["Sector2Time"]),
                "sector3_s": lap_to_seconds(lap["Sector3Time"]),
                "compound": str(lap["Compound"]),
                "tyre_life": float(lap["TyreLife"]) if not pd.isna(lap["TyreLife"]) else np.nan,
                "stint": float(lap["Stint"]) if not pd.isna(lap["Stint"]) else np.nan,
                "track_temp": float(weather["TrackTemp"]) if "TrackTemp" in weather else np.nan,
                "air_temp": float(weather["AirTemp"]) if "AirTemp" in weather else np.nan,
            }

            for idx, value in enumerate(telemetry_vector):
                row[f"tel_{idx}"] = value

            rows.append(row)

    if not rows:
        raise RuntimeError("No valid laps found. Try different rounds or increase max-laps.")

    df = pd.DataFrame(rows)
    df = pd.get_dummies(df, columns=["compound"], dummy_na=True)
    df = df.dropna()
    return df


def train_and_report_random_split(df: pd.DataFrame, label_col: str, title: str) -> None:
    x = df.drop(columns=["driver_label", "circuit_label", "round_number"])
    y = df[label_col]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    preds = model.predict(x_test)

    print(f"\n===== {title} (Random split) =====")
    print(classification_report(y_test, preds, zero_division=0))


def parse_rounds(raw: str) -> List[int]:
    return [int(r.strip()) for r in raw.split(",") if r.strip()]


def train_and_report_holdout_rounds(
    df: pd.DataFrame,
    label_col: str,
    title: str,
    test_rounds: List[int],
) -> None:
    if not test_rounds:
        return

    train_df = df[~df["round_number"].isin(test_rounds)].copy()
    test_df = df[df["round_number"].isin(test_rounds)].copy()

    if train_df.empty or test_df.empty:
        print(f"\n===== {title} (Holdout rounds) =====")
        print("Skipped: train or test split is empty for selected holdout rounds.")
        return

    x_train = train_df.drop(columns=["driver_label", "circuit_label", "round_number"])
    y_train = train_df[label_col]
    x_test = test_df.drop(columns=["driver_label", "circuit_label", "round_number"])
    y_test = test_df[label_col]

    # For circuit prediction, holdout-by-round means unseen classes in test.
    if label_col == "circuit_label":
        unseen = sorted(set(y_test.unique()) - set(y_train.unique()))
        if unseen:
            print(f"\n===== {title} (Holdout rounds) =====")
            print(
                "Skipped: circuit labels in holdout are unseen in train "
                f"(unseen circuits: {', '.join(unseen)})."
            )
            return

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    preds = model.predict(x_test)

    print(f"\n===== {title} (Holdout rounds: {test_rounds}) =====")
    print(classification_report(y_test, preds, zero_division=0))


def main() -> None:
    parser = argparse.ArgumentParser(description="Objective 1 baseline: driver + circuit classification.")
    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument("--rounds", type=str, default="1,2,3", help="Comma-separated round numbers, e.g. 1,2,3")
    parser.add_argument("--max-laps", type=int, default=80, help="Max laps to use per round")
    parser.add_argument("--telemetry-points", type=int, default=250, help="Points per lap after interpolation")
    parser.add_argument(
        "--holdout-rounds",
        type=str,
        default="",
        help="Comma-separated test rounds for stricter evaluation (e.g. 3).",
    )
    args = parser.parse_args()

    rounds = parse_rounds(args.rounds)
    holdout_rounds = parse_rounds(args.holdout_rounds) if args.holdout_rounds else []

    if holdout_rounds:
        missing = sorted(set(holdout_rounds) - set(rounds))
        if missing:
            raise ValueError(
                "--holdout-rounds must be included in --rounds. "
                f"Missing from --rounds: {missing}"
            )

    print("Building dataset...")
    dataset = build_dataset(
        year=args.year,
        rounds=rounds,
        max_laps=args.max_laps,
        points=args.telemetry_points,
    )
    print(f"Dataset shape: {dataset.shape}")
    print(f"Drivers: {dataset['driver_label'].nunique()} | Circuits: {dataset['circuit_label'].nunique()}")

    train_and_report_random_split(dataset, "driver_label", "Driver classification")
    train_and_report_random_split(dataset, "circuit_label", "Circuit classification")

    if holdout_rounds:
        train_and_report_holdout_rounds(
            dataset,
            "driver_label",
            "Driver classification",
            holdout_rounds,
        )
        train_and_report_holdout_rounds(
            dataset,
            "circuit_label",
            "Circuit classification",
            holdout_rounds,
        )


if __name__ == "__main__":
    main()
