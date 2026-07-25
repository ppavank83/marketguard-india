"""Command-line entry point for the MarketGuard prediction snapshot pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from marketguard.prediction_snapshot import (  # noqa: E402
    SnapshotPaths,
    run_snapshot_pipeline,
)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Generate the latest MarketGuard rank-based prediction snapshot."
        )
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="MarketGuard project root directory.",
    )

    parser.add_argument(
        "--feature-data",
        type=Path,
        default=None,
        help="Optional feature dataset path.",
    )

    parser.add_argument(
        "--outperform-model",
        type=Path,
        default=None,
        help="Optional outperform model path.",
    )

    parser.add_argument(
        "--downside-model",
        type=Path,
        default=None,
        help="Optional downside model path.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional output directory.",
    )

    return parser.parse_args()


def resolve_paths(arguments: argparse.Namespace) -> SnapshotPaths:
    """Resolve default paths and apply optional CLI overrides."""

    default_paths = SnapshotPaths.from_project_root(
        arguments.project_root
    )

    return SnapshotPaths(
        feature_data=(
            arguments.feature_data.resolve()
            if arguments.feature_data
            else default_paths.feature_data
        ),
        outperform_model=(
            arguments.outperform_model.resolve()
            if arguments.outperform_model
            else default_paths.outperform_model
        ),
        downside_model=(
            arguments.downside_model.resolve()
            if arguments.downside_model
            else default_paths.downside_model
        ),
        output_dir=(
            arguments.output_dir.resolve()
            if arguments.output_dir
            else default_paths.output_dir
        ),
    )


def main() -> int:
    """Run the production prediction snapshot pipeline."""

    arguments = parse_arguments()
    paths = resolve_paths(arguments)

    try:
        result, artifacts = run_snapshot_pipeline(paths)
    except Exception as error:
        print(
            f"Snapshot pipeline failed: {error}",
            file=sys.stderr,
        )
        return 1

    snapshot = result.snapshot
    audit = result.audit

    print("MarketGuard rank-based prediction snapshot")
    print("Snapshot date:", result.metadata["snapshot_date"])
    print("Total stocks:", len(snapshot))
    print("Prediction-ready stocks:", int(snapshot["prediction_ready"].sum()))
    print("Limited-confidence stocks:", int((~snapshot["prediction_ready"]).sum()))
    print("V1-to-V2 classification changes:", int(audit["classification_changed"].sum()))
    print("Output directory:", paths.output_dir)

    print("\nSaved artifacts:")
    for path in artifacts.__dict__.values():
        print(f"[SAVED] {path.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())