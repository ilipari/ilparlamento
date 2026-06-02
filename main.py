# Press Maiusc+F10 to execute it or replace it with your code.
import service.data


def test(name):
    dati = service.data.data_index()
    df = service.data.get_dataframe('camera', 18)
    json = service.data.get_data('camera', 17)
    print(f'Hi, {name}')


if __name__ == '__main__':
    test('PyCharm')
