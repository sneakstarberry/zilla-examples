# mqtt.kafka.reflect (incubator)

Listens on mqtt port `1883` and will forward mqtt publish messages to Kafka, broadcasting to all subscribed mqtt clients.
Listens on mqtts port `8883` and will forward mqtt publish messages to Kafka, broadcasting to all subscribed mqtt clients.

### Requirements

- bash, jq, nc
- Zilla docker image local incubator build, `develop-SNAPSHOT` version
- Kubernetes (e.g. Docker Desktop with Kubernetes enabled)
- kubectl
- helm 3.0+
- mosquitto
- kcat

### Setup

The `setup.sh` script:

- installs Zilla to the Kubernetes cluster with helm and waits for the pod to start up
- starts port forwarding

```bash
$./setup.sh   
+ ZILLA_CHART=oci://ghcr.io/aklivity/charts/zilla
+ VERSION=0.9.46
+ helm install zilla-mqtt-kafka-reflect oci://ghcr.io/aklivity/charts/zilla --version 0.9.46 --namespace zilla-mqtt-kafka-reflect --create-namespace --wait [...]
NAME: zilla-mqtt-kafka-reflect
LAST DEPLOYED: [...]
NAMESPACE: zilla-mqtt-kafka-reflect
STATUS: deployed
REVISION: 1
NOTES:
Zilla has been installed.
+ helm install zilla-mqtt-kafka-reflect-kafka chart --namespace zilla-mqtt-kafka-reflect --create-namespace --wait
NAME: zilla-mqtt-kafka-reflect-kafka
LAST DEPLOYED: [...]
NAMESPACE: zilla-mqtt-kafka-reflect
STATUS: deployed
REVISION: 1
TEST SUITE: None
++ kubectl get pods --namespace zilla-mqtt-kafka --selector app.kubernetes.io/instance=kafka -o name
+ KAFKA_POD=pod/kafka-74675fbb8-g56l9
+ kubectl exec --namespace zilla-mqtt-kafka pod/kafka-74675fbb8-g56l9 -- /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic mqtt_messages --if-not-exists
Created topic mqtt_messages.
+ kubectl port-forward --namespace zilla-mqtt-kafka service/zilla-mqtt-kafka-reflect 1883 8883
+ nc -z localhost 1883
+ kubectl port-forward --namespace zilla-mqtt-kafka service/kafka 9092 29092
+ sleep 1
+ nc -z localhost 1883
Connection to localhost port 1883 [tcp/ibm-mqisdp] succeeded!
+ nc -z localhost 9092
Connection to localhost port 9092 [tcp/XmlIpcRegSvc] succeeded!
```

### Install mqtt client

Requires MQTT 5.0 client, such as Mosquitto clients.

```bash
brew install mosquitto
```

### Install kcat client

Requires Kafka client, such as `kcat`.

```bash
brew install kcat
```

### Verify behavior

Connect two subscribing clients first, then send `Hello, world` from publishing client. Verify that the message arrived to Kafka.

```bash
mosquitto_sub -V '5' -t 'zilla' -d
```

output:

```text
Client null sending CONNECT
Client 2b77314a-163f-4f18-908c-2913645e4f56 received CONNACK (0)
Client 2b77314a-163f-4f18-908c-2913645e4f56 sending SUBSCRIBE (Mid: 1, Topic: zilla, QoS: 0, Options: 0x00)
Client 2b77314a-163f-4f18-908c-2913645e4f56 received SUBACK
Subscribed (mid: 1): 0
Client 2b77314a-163f-4f18-908c-2913645e4f56 received PUBLISH (d0, q0, r0, m0, 'zilla', ... (12 bytes))
Hello, world
```

```bash
mosquitto_sub -V '5' -t 'zilla' --cafile test-ca.crt -d
```

output:

```text
Client null sending CONNECT
Client 26ab67d8-4a61-4e14-9d95-6a383c0cbdd7 received CONNACK (0)
Client 26ab67d8-4a61-4e14-9d95-6a383c0cbdd7 sending SUBSCRIBE (Mid: 1, Topic: zilla, QoS: 0, Options: 0x00)
Client 26ab67d8-4a61-4e14-9d95-6a383c0cbdd7 received SUBACK
Subscribed (mid: 1): 0
Client 26ab67d8-4a61-4e14-9d95-6a383c0cbdd7 received PUBLISH (d0, q0, r0, m0, 'zilla', ... (12 bytes))
Hello, world
```

```bash
mosquitto_pub -V '5' -t 'zilla' -m 'Hello, world' -d
```

output:

```text
Client null sending CONNECT
Client 44181407-f1bc-4a6b-b94d-9f37d37ea395 received CONNACK (0)
Client 44181407-f1bc-4a6b-b94d-9f37d37ea395 sending PUBLISH (d0, q0, r0, m1, 'zilla', ... (12 bytes))
Client 44181407-f1bc-4a6b-b94d-9f37d37ea395 sending DISCONNECT
```

```bash
kcat -C -b localhost:9092 -t mqtt_messages -J -u | jq .
{
  "topic": "mqtt_messages",
  "partition": 0,
  "offset": 0,
  "tstype": "create",
  "ts": 1683710037377,
  "broker": 1,
  "headers": [
    "zilla:topic",
    "zilla",
    "zilla:local",
    "44181407-f1bc-4a6b-b94d-9f37d37ea395",
    "zilla:format",
    "BINARY"
  ],
  "key": "zilla",
  "payload": "Hello, world"
}
```

output:

```text
% Reached end of topic mqtt_messages [0] at offset 1
```

### Teardown

The `teardown.sh` script stops port forwarding, uninstalls Zilla and Kafka and deletes the namespace.

```bash
./teardown.sh

```

output:

```text
+ pgrep kubectl
99998
99999
+ killall kubectl
+ helm uninstall zilla-mqtt-kafka-reflect zilla-mqtt-kafka-reflect-kafka --namespace zilla-mqtt-kafka
release "zilla-mqtt-kafka-reflect" uninstalled
release "zilla-mqtt-kafka-reflect-kafka" uninstalled
+ kubectl delete namespace zilla-mqtt-kafka
namespace "zilla-mqtt-kafka" deleted
```
