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

            # Perform BFS
            bfsResult = session.run("""
                MATCH (source) WHERE source.name = $start_node
                MATCH (target) WHERE target.name = $last_node
                CALL gds.bfs.stream('taxiGraph', {
                    sourceNode: source,
                    targetNodes: [target]
                })
                YIELD path
                RETURN [n IN nodes(path) | n.name] AS nodeNames
            """, start_node=int(start_node), last_node=int(last_node))

            record = bfsResult.single()
            if not record:
                raise Exception("BFS traversal did not return any results.")

            path = [{'name': int(node_name)} for node_name in record['nodeNames']]
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