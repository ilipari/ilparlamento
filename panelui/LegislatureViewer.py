import panel as pn
import param
from service.data import data_index, get_dataframe


class LegislatureViewer(param.Parameterized):
    institution = param.Selector()
    legislature = param.Selector()
    name_to_legislature = data_index()

    def __init__(self, **params):
        super().__init__(**params)
        # Inizializza institution in base ai dati recuperati, legislature si aggiornano tramite la callback
        if LegislatureViewer.name_to_legislature:
            self.institution = next(iter(LegislatureViewer.name_to_legislature))  # Seleziona il primo valore
            self.param['institution'].objects = list(LegislatureViewer.name_to_legislature.keys())

    @param.depends('institution', watch=True)
    def _update_legislatures(self):
        # Aggiorna legislature disponibili
        if self.institution in LegislatureViewer.name_to_legislature:
            legislatures = LegislatureViewer.name_to_legislature[self.institution]
            self.param['legislature'].objects = legislatures
            self.legislature = legislatures[0]  # Seleziona la prima legislatura della lista

    @param.depends('legislature')
    def view(self):
        if not self.legislature:
            return
        df = get_dataframe(self.institution, self.legislature)
        return pn.pane.DataFrame(df.head())


viewer = LegislatureViewer(name='Legislature Viewer')
layout = pn.Column(viewer.param, viewer.view)
layout.servable(title='Il parlamento')
