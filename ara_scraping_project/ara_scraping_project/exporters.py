from scrapy.exporters import CsvItemExporter ## Esto lo utilice para modificar la manera en que se exporta a CSV, ya que por defecto el separador es ","


class CsvCustomSeperator(CsvItemExporter):
    def __init__(self, *args, **kwargs):
        #kwargs['encoding'] = 'utf-8'
        kwargs['encoding'] = 'cp1252'  ## Por defecto (en mi caso) esta es la decodificacion que maneja por defecto mi excel
        kwargs['delimiter'] = ';'
        super(CsvCustomSeperator, self).__init__(*args, **kwargs)

