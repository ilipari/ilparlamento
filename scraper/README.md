# scraper

il modulo è uno scraper web costruito con Scrapy per estrarre dati sui deputati italiani dal sito della [Camera dei Deputati](https://www.camera.it).

### Descrizione

Il progetto automatizza la raccolta di informazioni sui deputati attraverso l'analisi sistematica del portale ufficiale della Camera italiana. Lo scraper naviga per legislatura e lettera iniziale del cognome, raccogliendo dati strutturati su ciascun deputato.

### Caratteristiche

- **Spider specializzato**: `CameraSpider` per la Camera dei Deputati
- **Supporto multi-legislatura**: Consente di specificare quali legislature esaminare. Gestisce riferimenti relativi alle legislature (es. `0` per l'ultima legislatura, `-1` per la penultima legislatura)
- **Filtro per lettera**: Estrae deputati raggruppati per iniziale del cognome
- **Logging dettagliato**: Tracciamento completo delle operazioni di scraping
### Installazione

```bash
git clone https://github.com/ilipari/ilparlamento.git
cd ilparlamento/scraper
pip install
```

### Utilizzo

Eseguire lo spider con Scrapy:

```sh
scrapy crawl camera -O items.json
```


### Configurazione

Modificare i parametri nello spider per personalizzare lo scraping:

```python
self.legislature = [-1, 19, 20]  # Legislature da estrarre (0 = ultima, -1 = penultima ...)
self.letters = ['K']  # Lettere iniziali dei cognomi
```

### Struttura del progetto

```
scraper/
└── scraper/
    └── spiders/
        └── camera.py    # Spider principale
```

### Output

Lo scraper produce dizionari con i seguenti campi:

```python
{
    'nome': 'Nome Cognome',
    'legislatura': 20
}
```

### Tecnologie

- **Scrapy**: Framework per web scraping
- **Python 3.x**: Linguaggio di programmazione

### Licenza

Specificare la licenza appropriata (ad es. MIT, GPL, ecc.)

### Autore

ilipari

---

**Nota**: Assicurarsi di rispettare i termini di servizio del sito della Camera dei Deputati e di utilizzare questo strumento responsabilmente.