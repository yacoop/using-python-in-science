import argparse
import numpy as np
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


class IsingModel:
    def __init__(self, args):
        self.n = args.number
        self.J = args.j_value
        self.beta = args.beta
        self.B = args.B_value
        self.steps = args.steps
        self.spin_density = args.density
        self.image_prefix = args.image_prefix
        self.animation_file = args.animation_file
        self.magnetization_file = args.magnetization_file

        self.grid = np.random.choice(
            [-1, 1], size=(self.n, self.n), p=[1 - args.density, args.density]
        )

        self.magnetization = []

    def energy_change(self, i, j):
        spin = self.grid[i, j]
        neighbors = (
            self.grid[(i + 1) % self.n, j]
            + self.grid[(i - 1) % self.n, j]
            + self.grid[i, (j + 1) % self.n]
            + self.grid[i, (j - 1) % self.n]
        )
        dE = 2 * spin * (self.J * neighbors + self.B)
        return dE

    def monte_carlo_step(self):
        for _ in range(self.n * self.n):
            i, j = np.random.randint(0, self.n, size=2)
            dE = self.energy_change(i, j)
            if dE < 0 or np.random.rand() < np.exp(-self.beta * dE):
                self.grid[i, j] *= -1

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
        images = []
        with progress_bar as p:
            for step in p.track(range(self.steps)):
                self.monte_carlo_step()
                magnetization = np.sum(self.grid) / (self.n * self.n)
                self.magnetization.append(magnetization)

                if self.animation_file or self.image_prefix:
                    image = Image.new("RGB", (self.n, self.n))
                    draw = ImageDraw.Draw(image)
                    for i in range(self.n):
                        for j in range(self.n):
                            color = (255, 0, 0) if self.grid[i, j] == 1 else (0, 0, 255)
                            draw.point((j, i), fill=color)

                    image = image.resize((1000, 1000), Image.NEAREST)
                    images.append(image)
                    if self.image_prefix:
                        image.save(f"project02/out/{self.image_prefix}_{step}.png")

        if self.animation_file:
            images[0].save(
                f"project02/out/{self.animation_file}",
                save_all=True,
                append_images=images[1:],
                duration=100,
                loop=0,
            )

        if self.magnetization_file:
            with open(f"project02/out/{self.magnetization_file}", "w") as f:
                for step, m in enumerate(self.magnetization):
                    f.write(f"{step}\t{m}\n")


args = get_arguments()
ising = IsingModel(args)
ising.simulate()

rich.get_console().rule("Completed!", style="bold cyan")
