#! bin/bash
PERSISTER_MEMORY_MAX=${PERSISTER_MEMORY_MAX:-1024m}

java -Dfile.encoding=UTF-8 -Xmx${PERSISTER_MEMORY_MAX} -cp /monasca-persister.jar monasca.persister.PersisterApplication server /config/persister-config.yml
