import pandas as pd
from main import procesar_archivo1
from utils import procesar_archivo2

def main():
    df1 = procesar_archivo1()
    df2 = procesar_archivo2()

    with pd.ExcelWriter('resultado.xlsx') as writer:
        df1.to_excel(writer, sheet_name='alertas', index=False)
        df2.to_excel(writer, sheet_name='inconsistencias', index=False)

    print("Archivo generado correctamente")

if __name__ == "__main__":
    main()
