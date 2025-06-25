"""
bar_chart.py
------------

Быстрое построение группированных столбчатых диаграмм.

Использование:
    from bar_chart import plot_grouped_bar

    data = [[5, 7, 3, 4],           # значения для набора 1
            [6, 2, 7, 5],           # значения для набора 2
            [4, 3, 6, 7]]           # значения для набора 3

    plot_grouped_bar(
        data,
        category_labels=["Q1", "Q2", "Q3", "Q4"],
        dataset_labels=["Product A", "Product B", "Product C"],
        xlabel="Quarter",
        ylabel="Sales (thousands)",
        title="Quarterly Sales per Product",
        y_range=(0, 10),
    )
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_grouped_bar(
    data,
    category_labels,
    dataset_labels,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    y_range: tuple | None = None,
    save_path: str | None = None,  # ← новое
    dpi: int = 300,
    grid: bool = False,
    figsize: tuple[int, int] = (12, 5),
) -> None:
    """
    Строит группированную столбчатую диаграмму.

    Parameters
    ----------
    data : list[list[float]]
        2-мерный список или ndarray: data[dataset][category].
    category_labels : list[str]
        Названия категорий (ось X).
    dataset_labels : list[str]
        Названия наборов данных (легенда).
    xlabel, ylabel, title : str, optional
        Подписи осей и заголовок.
    y_range : (low, high), optional
        Диапазон оси Y.
    """
    n_sets = len(data)
    n_cats = len(category_labels)
    if not all(len(row) == n_cats for row in data):
        raise ValueError(
            f"Каждый набор должен содержать {n_cats} значений — по одному на категорию."
        )

    plt.figure(figsize=figsize)
    x = np.arange(n_cats)
    total_width = 0.9  # доля единичного шага, занятая всей группой
    bar_width = total_width / n_sets
    max_val = max(max(row) for row in data)

    for idx, values in enumerate(data):
        positions = x - total_width / 2 + bar_width / 2 + idx * bar_width
        plt.bar(positions, values, width=bar_width, label=dataset_labels[idx])

        # подписываем численные значения
        # for pos, val in zip(positions, values):
        #     plt.text(
        #         pos,
        #         val + max_val * 0.02,
        #         f"{val}",
        #         ha="center",
        #         va="bottom",
        #         fontsize=8,
        #     )

    plt.xticks(x, category_labels)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    if y_range:
        plt.ylim(*y_range)

    plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=n_sets)
    plt.tight_layout()

    if grid:
        plt.grid(True, axis="y", linestyle="--", alpha=0.5)

    # --- сохранение ---
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches="tight")

    # закрываем, чтобы не захламлять память при пакетной генерации
    plt.close()


if __name__ == "__main__":
    #######################

    example_data = [
        [0.828, 0.804, 0.801, 0.792],  # DeepSORT+EKF
        [0.798, 0.772, 0.778, 0.764],  # DeepSORT
        [0.830, 0.790, 0.795, 0.790],  # OC-SORT
        [0.766, 0.746, 0.740, 0.732],  # FairMOT
        [0.823, 0.788, 0.784, 0.790],  # ByteTrack
    ]
    plot_grouped_bar(
        example_data,
        category_labels=["Ясная погода", "Туман", "Дождь", "Снег"],
        dataset_labels=["DeepSORT+EKF", "DeepSORT", "OC-SORT", "FairMOT", "ByteTrack"],
        xlabel=" ",
        ylabel="MOTA",
        title=" ",
        y_range=(0.6, 0.9),
        save_path="MOTA_weather.png",  # ← будет создан PNG-файл (300 dpi)
        grid=True,
        figsize=(8, 4),
    )

    #######################

    example_data = [
        [0.814, 0.810, 0.802],  # DeepSORT+EKF
        [0.789, 0.782, 0.776],  # DeepSORT
        [0.819, 0.811, 0.793],  # OC-SORT
        [0.756, 0.744, 0.738],  # FairMOT
        [0.813, 0.785, 0.779],  # ByteTrack
    ]
    plot_grouped_bar(
        example_data,
        category_labels=["Низкая плотность", "Средняя плотность", "Высокая плотность"],
        dataset_labels=["DeepSORT+EKF", "DeepSORT", "OC-SORT", "FairMOT", "ByteTrack"],
        xlabel=" ",
        ylabel="MOTA",
        title=" ",
        y_range=(0.6, 0.9),
        save_path="MOTA_traffic.png",  # ← будет создан PNG-файл (300 dpi)
        grid=True,
        figsize=(8, 4),
    )

    #######################

    example_data = [
        [0.820, 0.804, 0.801, 0.796, 0.792],  # DeepSORT+EKF
        [0.790, 0.778, 0.782, 0.780, 0.779],  # DeepSORT
        [0.825, 0.7, 0.795, 0.790, 0.0],  # OC-SORT
        [0.746, 0.726, 0.730, 0.722, 0.0],  # FairMOT
        [0.843, 0.788, 0.784, 0.790, 0.0],  # ByteTrack
    ]
    plot_grouped_bar(
        example_data,
        category_labels=[
            "Хорошее\nосвещение",
            "Плохое\nосвещение",
            "Переменное\nосвещение",
            "Переход из\nсветлого в\nтемное",
            "Переход из\nтемного в\nсветлое",
        ],
        dataset_labels=["DeepSORT+EKF", "DeepSORT", "OC-SORT", "FairMOT", "ByteTrack"],
        xlabel=" ",
        ylabel="MOTA",
        title=" ",
        y_range=(0.6, 0.9),
        save_path="MOTA_light.png",  # ← будет создан PNG-файл (300 dpi)
        grid=True,
        figsize=(8, 4),
    )

    #######################

    example_data = [
        [0.850, 0.804, 0.801, 0.792],  # DeepSORT+EKF
        [0.798, 0.772, 0.778, 0.764],  # DeepSORT
        [0.853, 0.790, 0.795, 0.790],  # OC-SORT
        [0.746, 0.726, 0.730, 0.722],  # FairMOT
        [0.843, 0.788, 0.784, 0.790],  # ByteTrack
    ]
    plot_grouped_bar(
        example_data,
        category_labels=["Ясная погода", "Туман", "Дождь", "Снег"],
        dataset_labels=["DeepSORT+EKF", "DeepSORT", "OC-SORT", "FairMOT", "ByteTrack"],
        xlabel=" ",
        ylabel="IDF1",
        title=" ",
        y_range=(0.6, 0.9),
        save_path="IDF1_weather.png",  # ← будет создан PNG-файл (300 dpi)
        grid=True,
        figsize=(8, 4),
    )
