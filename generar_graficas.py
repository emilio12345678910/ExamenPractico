import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "datos.csv")
IMG_DIR = os.path.join(BASE_DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)

WEIGHT_BINS = [6.0, 7.5, 9.0, 10.5, 12.0, 13.5]
WEIGHT_LABELS = ["6.0-7.5", "7.5-9.0", "9.0-10.5", "10.5-12.0", "12.0-13.5"]

HEIGHT_BINS = [60, 65, 70, 75, 80, 85]
HEIGHT_LABELS = ["60-65", "65-70", "70-75", "75-80", "80-85"]

SPEED_BINS = [5, 10, 15, 20, 25, 30, 35]
SPEED_LABELS = ["5-10", "10-15", "15-20", "20-25", "25-30", "30-35"]


def cargar_datos():
    df = pd.read_csv(CSV_FILE)
    for col in ["peso", "altura", "velocidad"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", ".", regex=False),
            errors="coerce"
        )
    df["color"] = df["color"].fillna("NA")
    return df


def calcular_estadisticas(df):
    stats = {}
    for col in ["peso", "altura", "velocidad"]:
        serie = df[col].dropna()
        moda = serie.mode().tolist()
        stats[col] = {
            "media": round(serie.mean(), 2),
            "mediana": round(serie.median(), 2),
            "moda": ", ".join(str(x) for x in moda) if moda else "Sin moda"
        }
    colores = df["color"].fillna("NA").value_counts().to_dict()
    stats["colores"] = colores
    return stats


def calcular_frecuencias(df, columna, bins=None, labels=None):
    if columna == "color":
        frecuencia_abs = df[columna].value_counts(sort=False)
        frecuencia_rel = (frecuencia_abs / frecuencia_abs.sum()).round(4)
        frecuencia_acum = frecuencia_abs.cumsum()
        x_labels = frecuencia_abs.index.astype(str).tolist()
        x_values = list(range(len(x_labels)))
        return frecuencia_abs, frecuencia_rel, frecuencia_acum, x_values, x_labels

    serie = pd.cut(df[columna], bins=bins, labels=labels, right=False)
    frecuencia_abs = serie.value_counts(sort=False)
    frecuencia_rel = (frecuencia_abs / frecuencia_abs.sum()).round(4)
    frecuencia_acum = frecuencia_abs.cumsum()
    puntos_medio = [(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)]
    return frecuencia_abs, frecuencia_rel, frecuencia_acum, puntos_medio, labels


def guardar_grafico_frecuencias_absolutas(frecuencia_abs, columna, xlabel):
    plt.figure(figsize=(8, 5))
    frecuencia_abs.plot(kind="bar", color="#4f46e5")
    plt.title(f"Frecuencia Absoluta de {columna.capitalize()}")
    plt.xlabel(xlabel)
    plt.ylabel("Frecuencia absoluta")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, f"{columna}-frecuencia-absoluta.png"))
    plt.close()


def guardar_grafico_frecuencias_relativas(frecuencia_rel, columna):
    plt.figure(figsize=(7, 7))
    frecuencia_rel.plot(kind="pie", autopct="%1.1f%%", startangle=140, textprops={"color": "white"})
    plt.title(f"Frecuencia Relativa de {columna.capitalize()}")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, f"{columna}-frecuencia-relativa.png"), facecolor="#111111")
    plt.close()


def guardar_grafico_poligono_frecuencias(x_values, frecuencia_abs, columna, xlabel, x_labels=None):
    plt.figure(figsize=(8, 5))
    plt.plot(x_values, frecuencia_abs.values, marker="o", linestyle="-", color="#f59e0b")
    plt.title(f"Polígono de Frecuencia de {columna.capitalize()}")
    plt.xlabel(xlabel)
    plt.ylabel("Frecuencia absoluta")
    if x_labels is not None:
        plt.xticks(x_values, x_labels, rotation=45)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, f"{columna}-poligono-frecuencias.png"))
    plt.close()


def guardar_grafico_frecuencia_acumulada(x_values, frecuencia_acum, columna, xlabel, x_labels=None):
    plt.figure(figsize=(8, 5))
    plt.plot(x_values, frecuencia_acum.values, marker="o", linestyle="--", color="#22c55e")
    plt.title(f"Frecuencia Acumulada de {columna.capitalize()}")
    plt.xlabel(xlabel)
    plt.ylabel("Frecuencia acumulada")
    if x_labels is not None:
        plt.xticks(x_values, x_labels, rotation=45)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, f"{columna}-frecuencia-acumulada.png"))
    plt.close()


def generar_html_dinamico(estadisticas):
    html_path = os.path.join(BASE_DIR, "index.html")
    with open(html_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido = contenido.replace("{{peso_media}}", str(estadisticas["peso"]["media"]))
    contenido = contenido.replace("{{peso_mediana}}", str(estadisticas["peso"]["mediana"]))
    contenido = contenido.replace("{{peso_moda}}", estadisticas["peso"]["moda"])
    contenido = contenido.replace("{{altura_media}}", str(estadisticas["altura"]["media"]))
    contenido = contenido.replace("{{altura_mediana}}", str(estadisticas["altura"]["mediana"]))
    contenido = contenido.replace("{{altura_moda}}", estadisticas["altura"]["moda"])
    contenido = contenido.replace("{{velocidad_media}}", str(estadisticas["velocidad"]["media"]))
    contenido = contenido.replace("{{velocidad_mediana}}", str(estadisticas["velocidad"]["mediana"]))
    contenido = contenido.replace("{{velocidad_moda}}", estadisticas["velocidad"]["moda"])
    colores_str = ", ".join(f"{k}: {v}" for k, v in estadisticas["colores"].items())
    contenido = contenido.replace("{{colores}}", colores_str)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(contenido)


def main():
    df = cargar_datos()
    estadisticas = calcular_estadisticas(df)

    datos = [
        {"columna": "peso", "bins": WEIGHT_BINS, "labels": WEIGHT_LABELS, "xlabel": "Intervalo de peso"},
        {"columna": "altura", "bins": HEIGHT_BINS, "labels": HEIGHT_LABELS, "xlabel": "Punto medio del intervalo de altura"},
        {"columna": "velocidad", "bins": SPEED_BINS, "labels": SPEED_LABELS, "xlabel": "Punto medio del intervalo de velocidad"},
        {"columna": "color", "bins": None, "labels": None, "xlabel": "Categoría de color"}
    ]

    for dato in datos:
        frecuencia_abs, frecuencia_rel, frecuencia_acum, puntos_x, x_labels = calcular_frecuencias(
            df,
            dato["columna"],
            dato["bins"],
            dato["labels"]
        )

        guardar_grafico_frecuencias_absolutas(frecuencia_abs, dato["columna"], dato["xlabel"])
        guardar_grafico_frecuencias_relativas(frecuencia_rel, dato["columna"])
        guardar_grafico_frecuencia_acumulada(puntos_x, frecuencia_acum, dato["columna"], dato["xlabel"], x_labels)
        guardar_grafico_poligono_frecuencias(puntos_x, frecuencia_abs, dato["columna"], dato["xlabel"], x_labels)

    generar_html_dinamico(estadisticas)

    print("Gráficos generados en la carpeta img/")
    print("HTML actualizado con estadísticas calculadas.")
    print("--- Estadísticas ---")
    for campo in ["peso", "altura", "velocidad"]:
        print(f"{campo.capitalize()}: media = {estadisticas[campo]['media']}, mediana = {estadisticas[campo]['mediana']}, moda = {estadisticas[campo]['moda']}")
    print("Colores:")
    for color, cuenta in estadisticas["colores"].items():
        print(f"  {color}: {cuenta}")


if __name__ == "__main__":
    main()
