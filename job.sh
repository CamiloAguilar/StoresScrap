#!/usr/bin/env bash
cd /home/camilo/Documentos/EasyData/Projects

#!/bin/bash
source "easySearch/bin/activate"

#!/usr/bin/env bash
cd /home/camilo/Documentos/EasyData/Projects/easySearch/StoresScrap/alkosto_scraping_project
scrapy crawl alkosto_scraping -o "../results/alkosto.csv"
scrapy crawl ktronix_scraping -o "../results/ktronix.csv"

#!/usr/bin/env bash
cd /home/camilo/Documentos/EasyData/Projects/easySearch/StoresScrap/colsubsidio_scraping_project
scrapy crawl colsubsidio_scraping -o "../results/colsubsidio.csv"
scrapy crawl colsubsidio_scraping_drog -o "../results/colsubsidio_drog.csv"

#!/usr/bin/env bash
cd /home/camilo/Documentos/EasyData/Projects/easySearch/StoresScrap/justoybueno_scraping_project
scrapy crawl justoybueno_scraping -o "../results/justo_y_bueno.csv"

#!/usr/bin/env bash
cd /home/camilo/Documentos/EasyData/Projects/easySearch/StoresScrap/ara_scraping_project
scrapy crawl ara_scraping -o "../results/ara.csv"

#!/usr/bin/env bash
cd /home/camilo/Documentos/EasyData/Projects/easySearch/StoresScrap/scraping_stores
scrapy crawl exito_scraping -o "../results/exito.csv"

#!/usr/bin/env bash
cd /home/camilo/Documentos/EasyData/Projects/easySearch/StoresScrap/olimpica_scraping_project
scrapy crawl olimpica_scraping -o "../results/olimpica.csv"

#!/usr/bin/env bash
cd /home/camilo/Documentos/EasyData/Projects/easySearch/StoresScrap/falabella_scraping_project
scrapy crawl falabella_scraping -o "../results/falabella.csv"

#!/usr/bin/env bash
cd /home/camilo/Documentos/EasyData/Projects
exec bash
