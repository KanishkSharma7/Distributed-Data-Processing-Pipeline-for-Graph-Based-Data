# Steps to Setup and Run the Project

The submission contains YAML configuration files for Kubernetes deployment and Python scripts for implementation and testing of graph algorithms.

## Prerequisites
- Minikube
- kubectl
- Helm
- Python 3.12.3 with required packages
- Neo4j GDS Library 2.12.0

## Setup Instructions

1. Start Minikube cluster with required resources:
```bash
minikube start --cpus=6 --memory=8192
```

For visualization (optional) run:
```bash
minikube dashboard
```

In another terminal, run the following command and **keep it running** (mandatory):
```bash
minikube tunnel
```

2. Deploy Kafka and Zookeeper:
```bash
kubectl apply -f zookeeper-setup.yaml
kubectl apply -f kafka-setup.yaml
```

3. Deploy Neo4j using Helm:
```bash
helm install neo4j-standalone neo4j/neo4j -f neo4j-values.yaml
kubectl apply -f neo4j-service.yaml
```

4. Setup Kafka-Neo4j connector:
```bash
kubectl apply -f kafka-neo4j-connector.yaml
```

5. Setup port forwarding:

In a new terminal run and **keep it running**:
```bash
kubectl port-forward svc/neo4j-service 7474:7474 7687:7687
```

In another terminal, run and **keep it running**:
```bash
kubectl port-forward svc/kafka-service 9092:9092
```

6. Install the required dependencies to run data_producer.py and tester.py:
```bash
pip install confluent-kafka pyarrow pandas requests
```

7. Load data into the database:
```bash
python3 data_producer.py
```

8. Run the provided test cases:
```bash
python3 tester.py
```

# Implemented Features

## Graph Algorithms
- PageRank implementation for node importance analysis
- Breadth-First Search (BFS) for path finding

# Results of the Provided Testcases

The following Google Drive link contains screenshots of:
- Terminal outputs showing successful test execution
- Neo4j browser visualizations of the graph
- Data loading confirmation

[(Google Drive Link)](https://drive.google.com/drive/folders/1MKCBHA-XO6rXQK_I7Fx6sElSKMeBkk9c?usp=sharing)

# Cleanup Instructions

To remove all deployed resources:
```bash
helm uninstall neo4j-standalone
kubectl delete -f ./kafka-neo4j-connector.yaml
kubectl delete -f ./kafka-setup.yaml
kubectl delete -f ./zookeeper-setup.yaml
minikube stop
```