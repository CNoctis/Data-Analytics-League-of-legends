import pathlib
import pandas
import time
import matplotlib.pyplot as plt
from data_extractor import user_data

#Start of timer
start_time = time.time()
def transform_data(data_pro):
   #data_pro['win'] = data_pro['win'].map({True:1, False:0})
    data_pro = data_pro.sort_values('win')
    xa = data_pro.win.value_counts().tolist()
    ya = data_pro.win.unique()
    data_pro.plot.scatter(x='goldEarned', y= 'goldSpent')
    plt.show()

    plt.bar(xa,ya)
    plt.show()


def data_player(name):
    data = []
    file_path = str(pathlib.Path().absolute()) + "/files"
    directorio = pathlib.Path(file_path)
    for fichero in directorio.iterdir():
        filename = fichero
        data_csv= pandas.read_csv(filename)
        player = data_csv.loc[:,'summonerName'] == name
        df_player = data_csv.loc[player]
        data.append(df_player)
    data_select = pandas.concat(data[0:-1], ignore_index=True)
    data_userq = data[-1]

    return [data_select, data_userq]

def main():
    data_user = user_data()
    name = data_user.user
    data_pro = data_player(name)
    transform_data(data_pro[0])

    #End of timer
    stop_time= (time.time() - start_time)
    print("Tiempo de ejecucion:", stop_time)


if __name__ == '__main__':
    main()