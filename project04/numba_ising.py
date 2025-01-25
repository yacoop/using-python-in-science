import argparse
import numpy as np
from numba import njit
from PIL import Image, ImageDraw
import rich
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
import rich.traceback

rich.traceback.install()
rich.get_console().clear()
rich.get_console().rule("Ising simulation", style="bold cyan")


def get_arguments():
    parser = argparse.ArgumentParser(description="Analysis of words number")
    parser.add_argument(
        "--number",
        "-n",
        type=int,
        default=10,
        help="Size of grid (default 10).",
        required=True,
    )
    parser.add_argument(
        "--j_value",
        "-J",
        type=float,
        default=1,
        help="Value of J (default 1)",
        required=True,
    )
    parser.add_argument(
        "--beta",
        "-b",
        type=float,
        default=1,
        help="Value of parameter Beta (default 1).",
        required=True,
    )
    parser.add_argument(
        "--B_value",
        "-B",
        type=float,
        default=1,
        help="Value of field B (default 1).",
        required=True,
    )
    parser.add_argument(
        "--steps",
        "-s",
        type=int,
        default=100,
        help="Number of macrosteps (default 100).",
        required=True,
    )
    parser.add_argument(
        "--density",
        "-d",
        type=float,
        default=0.5,
        help="Initial spin density (default 0.5).",
    )
    parser.add_argument(
        "--image_prefix",
        "-ip",
        type=str,
        help="Prefix of images (if not provided no images saved)",
    )
    parser.add_argument(
        "--animation_file",
        "-af",
        type=str,
        help="Animation filename (if not provided no animation saved)",
    )
    parser.add_argument(
        "--magnetization_file",
        "-mf",
        type=str,
        help="Magnetization filename (if not provided no magnetization saved)",
    )
    args = parser.parse_args()

    return args

def save_img(grid, n, step, image_prefix):
    images = []
    image = Image.new("RGB", (n, n))
    draw = ImageDraw.Draw(image)
    for i in range(n):
        for j in range(n):
            color = (255, 0, 0) if grid[i, j] == 1 else (0, 0, 255)
            draw.point((j, i), fill=color)

    image = image.resize((1000, 1000), Image.NEAREST)
    images.append(image)
    if image_prefix:
        image.save(f"project04/out/{image_prefix}_{step}.png")

    return images

@njit
def energy_change(grid, n, J, B, i, j):
    spin = grid[i, j]
    neighbors = (
        grid[(i + 1) % n, j]
        + grid[(i - 1) % n, j]
        + grid[i, (j + 1) % n]
        + grid[i, (j - 1) % n]
    )
    dE = 2 * spin * (J * neighbors + B)
    return dE
@njit
def monte_carlo_step(grid, n, J, B, beta):
    for _ in range(n * n):
        i, j = np.random.randint(0, n, size=2)
        dE = energy_change(grid, n, J, B, i, j)
        if dE < 0 or np.random.rand() < np.exp(-beta * dE):
            grid[i, j] *= -1

    return grid

def simulate(self):
    progress_bar = Progress(
        TextColumn("Simulating:"),
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
    n = args.number
    J = args.j_value
    beta = args.beta
    B = args.B_value
    steps = args.steps
    spin_density = args.density
    image_prefix = args.image_prefix
    animation_file = args.animation_file
    magnetization_file = args.magnetization_file

    grid = np.random.choice(
        [-1, 1], size=(n, n), p=[1 - spin_density, spin_density]
    )

    magnetizations = []

    images = []
    with progress_bar as p:
        for step in p.track(range(steps)):
            grid = monte_carlo_step(grid, n, J, B, beta)
            magnetization = np.sum(grid) / (n * n)
            magnetizations.append(magnetization)

            if animation_file or image_prefix:
                images = save_img(grid, n, step, image_prefix)

    if animation_file:
        images[0].save(
            f"project04/out/{animation_file}",
            save_all=True,
            append_images=images[1:],
            duration=100,
            loop=0,
        )

    if magnetization_file:
        with open(f"project04/out/{magnetization_file}", "w") as f:
            for step, m in enumerate(magnetizations):
                f.write(f"{step}\t{m}\n")


args = get_arguments()
simulate(args)

rich.get_console().rule("Completed!", style="bold cyan")
