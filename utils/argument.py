import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s",
                        "--size",
                        default=150,
                        type=int,
                        help="""Number of students""")
    parser.add_argument("-g",
                        "--nb_grades",
                        default=3,
                        type=int,
                        help="""nb_grades""")
    parser.add_argument("-n",
                        "--nb_class",
                        default=1,
                        type=int,
                        help="""nb_class""")
    parser.add_argument("-b",
                        "--noise",
                        default=0,
                        type=float,
                        help="""noise""")
    parser.add_argument("--seed",
                        default=None,
                        type=int,
                        help="""int""")
    parser.add_argument("-m",
                        "--model",
                        default='MILP',
                        choices=['MILP', 'SAT','Max-SAT'],
                        help='Choosing the model used for prediction (default: %(default)s)')
    parser.add_argument("-c",
                        "--csv",
                        default='',
                        help='Choosing the dataset used (default: %(default)s)')
    return parser.parse_args()


def main():
    args = parse_arguments()
    return args


if __name__ == "__main__":
    main()
