from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def dropGraphIfExists(self, graphName):
        with self._driver.session() as session:
            result = session.run("""
                CALL gds.graph.exists($graphName) YIELD exists
                RETURN exists
            """, graphName=graphName)
            exists = result.single()["exists"]
            if exists:
                session.run("""
                    CALL gds.graph.drop($graphName) YIELD graphName
                """, graphName=graphName)

    def bfs(self, start_node, last_node):
        with self._driver.session() as session:

            self.dropGraphIfExists('taxiGraph')

            # Create an in-memory graph projecting all nodes and relationships
            session.run("""
                CALL gds.graph.project(
                    'taxiGraph',
                    '*',
                    '*',
                    {
                        relationshipProperties: 'distance'
                    }
                )
            """)

            # Get the internal node IDs for the start_node and last_node
            start_node_id_result = session.run("""
                MATCH (n) WHERE toString(n.name) = toString($start_node)
                RETURN id(n) AS nodeId
            """, start_node=start_node)
            start_node_record = start_node_id_result.single()
            if not start_node_record:
                raise ValueError(f"Start node with ID {start_node} does not exist in the graph.")
            start_node_id = start_node_record["nodeId"]

            last_node_id_result = session.run("""
                MATCH (n) WHERE toString(n.name) = toString($last_node)
                RETURN id(n) AS nodeId
            """, last_node=last_node)
            last_node_record = last_node_id_result.single()
            if not last_node_record:
                raise ValueError(f"Last node with ID {last_node} does not exist in the graph.")
            last_node_id = last_node_record["nodeId"]

            # Perform BFS
            bfs_result = session.run("""
                CALL gds.bfs.stream('taxiGraph', {
                    sourceNode: $start_node_id,
                    targetNodes: [$last_node_id],
                    concurrency: 4
                })
                YIELD nodeIds
                RETURN nodeIds
            """, start_node_id=start_node_id, last_node_id=last_node_id)

            # Extract the node IDs from the result
            record = bfs_result.single()
            if not record:
                raise Exception("BFS traversal did not return any results.")

            node_ids = record['nodeIds']

            # Get the traversal
            path = []
            for node_id in node_ids:
                node_name_result = session.run("""
                    MATCH (n) WHERE id(n) = $node_id
                    RETURN n.name AS name
                """, node_id=node_id)
                node_name_record = node_name_result.single()
                if node_name_record is None:
                    raise Exception(f"Node with id {node_id} not found")
                node_name = node_name_record['name']
                path.append({'name': int(node_name)})

            return [{'path': path}]


    def pagerank(self, max_iterations, weight_property):
        with self._driver.session() as session:
            
            self.dropGraphIfExists('taxiGraph')

            # Create an in-memory graph projecting all nodes and relationships
            session.run("""
                CALL gds.graph.project(
                    'taxiGraph',
                    '*',
                    '*',
                    {
                        relationshipProperties: $weight_property
                    }
                )
            """, weight_property=weight_property)

            # Perform pagerank
            query = """
                CALL gds.pageRank.stream('taxiGraph', {
                    maxIterations: $max_iterations,
                    dampingFactor: 0.85,
                    relationshipWeightProperty: $weight_property
                })
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name, score
            """

            result = session.run(query, max_iterations=max_iterations, weight_property=weight_property)
            resultList = [{"name": record["name"], "score": round(record["score"], 5)} for record in result]

            maxRank = max(resultList, key=lambda x: x['score'])
            minRank = min(resultList, key=lambda x: x['score'])

            session.run("""
                CALL gds.graph.drop('taxiGraph') YIELD graphName
            """)

            return [maxRank, minRank]