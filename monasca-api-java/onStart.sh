#! bin/bash
API_MEMORY_MAX=${API_MEMORY_MAX:-1024m}

java -Dfile.encoding=UTF-8 -Xmx${API_MEMORY_MAX} -cp /monasca-api.jar monasca.api.MonApiApplication server /config/api-config.yml
