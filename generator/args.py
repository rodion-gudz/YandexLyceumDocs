import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="yandex lyceum docs generator")
    parser.add_argument("--login", type=str, required=True)
    parser.add_argument("--password", type=str, required=True)
    parser.add_argument("--materials", action="store_true")
    parser.add_argument("--solutions", action="store_true")
    parser.add_argument("--teacher", action="store_true")
    return parser.parse_args()
