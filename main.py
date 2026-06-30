import argparse
from run_extract import main as extract_main
from run_transform_load import main as transform_main
from EDA import run_exploratory_data_analysis
from dashboard_etl import run_dashboard_etl

def main():

    parser = argparse.ArgumentParser(
        description="League of Legends Analytics Pipeline"
    )

    parser.add_argument(
        "--stage",
        required=True,
        choices=[
            "extract",
            "transform",
            "eda",
            "dashboard",
            "pipeline"
        ],
        help="Pipeline stage to execute."
    )

    args = parser.parse_args()

    if args.stage == "extract":
        extract_main()

    elif args.stage == "transform":
        transform_main()

    elif args.stage == "eda":
        run_exploratory_data_analysis()

    elif args.stage == "dashboard":
        run_dashboard_etl()

    elif args.stage == "pipeline":
        extract_main()
        transform_main()
        run_exploratory_data_analysis()
        run_dashboard_etl()


if __name__ == "__main__":
    main()
