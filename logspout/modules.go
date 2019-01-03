// DO NOT REMOVE, file used by Logspout build process

package main

import (
	_ "github.com/gliderlabs/logspout/adapters/multiline"
	_ "github.com/gliderlabs/logspout/transports/tcp"
	_ "github.com/gliderlabs/logspout/transports/udp"
	_ "github.com/looplab/logspout-logstash"
)
