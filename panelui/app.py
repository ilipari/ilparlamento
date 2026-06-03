import panel as pn

from service.data import get_dataframe

pn.extension()

data = get_dataframe('camera', 17)
component = pn.panel(data)
print(component)

component.servable()
