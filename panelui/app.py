import panel as pn

from service.data import get_dataframe, data_index

pn.extension()

legislature = data_index()['camera']
select = pn.widgets.Select(label='Select', options=legislature)
data_pane = pn.pane.DataFrame()
root = pn.Column(
    select,
    data_pane,
)
root.servable(title='Il parlamento')


def update(legislature):
    data_pane.object = get_dataframe('camera', legislature)


pn.bind(update, select, watch=True)

