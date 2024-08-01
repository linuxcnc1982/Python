import pandas as pd


def export_xlsx():
    fio='Петров Петр Петрович'
    d = {'x':fio, 
         'y':'18.09.1982', 
         'z': 3, 'a':4,'b':5, 'c':6}
    ser = pd.Series(data=d)
    try:
        with pd.ExcelWriter('1.xlsx', mode='a', if_sheet_exists='replace') as writer:
            ser.to_excel(writer, sheet_name='Данные')
    except PermissionError:
        print('Permission error')

if __name__ =='__main__':
    print('Pandas test')
    export_xlsx()