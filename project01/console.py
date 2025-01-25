# poetry run python project01/console.py
# poetry run python project01/console.py -f project01/books/The_Way_of_Kings-Sanderson-Brandon.txt project01/books/Droga_Krolow-Brandon_Sanderson.txt -m 7 -ml 3
# poetry run python project01/console.py -c project01/books/ -m 7 -ml 3 -chs th -mhs al

import argparse
import glob
import rich
import rich.traceback
from ascii_graph import Pyasciigraph
from ascii_graph.colors import Gre, Yel, Red, Blu
from ascii_graph.colordata import vcolor

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

import collections
from _collections_abc import Iterable

collections.Iterable = Iterable


def load_file(filename: str):
    with open(filename, encoding="utf8") as book:
        text = book.read().lower()
        words = text.split()
    return words


def get_words_set(
    words,
    min_length,
    ignore_words=None,
    must_have_sequence=None,
    cant_have_sequence=None,
):
    words_set = set(words)
    for word in words_set.copy():
        if len(word) < min_length:
            words_set.discard(word)

        if ignore_words is not None:
            if word in ignore_words:
                words_set.discard(word)

        if must_have_sequence is not None:
            for sequence in must_have_sequence:
                if sequence not in word:
                    words_set.discard(word)

        if cant_have_sequence is not None:
            for sequence in cant_have_sequence:
                if sequence in word:
                    words_set.discard(word)

    return words_set


def count_words(words, words_set, num_words):
    progress_bar = Progress(
        TextColumn("Words Counting:"),
        TextColumn("[bold green]{task.percentage:>3.0f}% "),
        BarColumn(
            bar_width=120,
            style="black",
            complete_style="bold blue",
            finished_style="bold green",
        ),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TextColumn("[bold black]/"),
        TimeRemainingColumn(),
    )
    words_dict = {word: 0 for word in words_set}
    with progress_bar as p:
        for word in p.track(words):
            if word in words_dict.keys():
                words_dict[word] += 1

    most_common_words = sorted(
        words_dict.items(), key=lambda item: item[1], reverse=True
    )

    return most_common_words[:num_words]


def create_histogram(most_common_words, file):
    graph = Pyasciigraph(
        line_length=120,
        min_graph_length=50,
        separator_length=4,
        multivalue=False,
        human_readable="si",
        graphsymbol="█",
        float_format="{0:,.2f}",
        force_max_value=2000,
    )

    pattern = [Blu, Gre, Yel, Red]
    data = vcolor(most_common_words, pattern[: len(most_common_words)])

    for line in graph.graph(file, data):
        print(line)

def get_arguments():
    parser = argparse.ArgumentParser(description="Analysis of words number")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--file", "-f", nargs="+", type=str, help="Path to the input file(s)"
    )
    group.add_argument("--catalog", "-c", nargs=1, type=str, help="Path to the catalog(s)")
    parser.add_argument(
        "--num_words",
        "-nw",
        type=int,
        default=10,
        help="Number of words in hist (default 10).",
    )
    parser.add_argument(
        "--min_length", "-ml", type=int, default=0, help="Min length of words (default 0)."
    )
    parser.add_argument(
        "--ignore_words", "-iw", nargs="*", type=str, help="List of words to ignore"
    )
    parser.add_argument(
        "--must_have_sequence",
        "-mhs",
        nargs="*",
        type=str,
        help="Sequence that words must to have",
    )
    parser.add_argument(
        "--cant_have_sequence",
        "-chs",
        nargs="*",
        type=str,
        help="Sequence that words cant to have",
    )
    args = parser.parse_args()

    return args

rich.traceback.install()
rich.get_console().clear()
rich.get_console().rule("Console program", style="bold cyan")

args = get_arguments()

if args.file:
    files = args.file
elif args.catalog:
    files = glob.glob(args.catalog[0] + "*")

for file_name in files:
    words = load_file(file_name)
    words_set = get_words_set(
        words,
        min_length=args.min_length,
        ignore_words=args.ignore_words,
        must_have_sequence=args.must_have_sequence,
        cant_have_sequence=args.cant_have_sequence,
    )
    most_common = count_words(words, words_set, num_words=args.num_words)
    create_histogram(most_common, file_name)
    print()

rich.get_console().rule("Completed!", style=" bold cyan")
