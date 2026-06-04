import panel as pn

from service.data import get_dataframe, data_index

pn.extension()


def update(legislature):
    df = get_dataframe('camera', legislature)
    return pn.pane.DataFrame(df)


legislature = data_index()['camera']
select = pn.widgets.Select(label='Select', options=legislature)
root = pn.Column(
    select,
    pn.bind(update, select),
)
root.servable(title='Il parlamento')
