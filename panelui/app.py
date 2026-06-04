import panel as pn

from service.data import get_dataframe, data_index

pn.extension()

name_to_legislature = data_index()
select_institution = pn.widgets.Select(label='Institution', options=list(name_to_legislature.keys()))
select_legislature = pn.widgets.Select(label='Legislatura', options=name_to_legislature[select_institution.value])


def show_data(name, legislature):
    if not legislature:
        return
    df = get_dataframe(name, legislature)
    return pn.pane.DataFrame(df.head())


# Callback per l'aggiornamento delle legislature disponibili
def update_select_legislature(name):
    select_legislature.options = name_to_legislature[name]


pn.bind(update_select_legislature, select_institution, watch=True)
root = pn.Column(
    select_institution,
    select_legislature,
    pn.bind(show_data, select_institution, select_legislature),
)
root.servable(title='Il parlamento')
