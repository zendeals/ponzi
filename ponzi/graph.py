import logging
import time

import networkx


class Graph(object):

    def __init__(self, nodes, options):
        self.nodes = nodes
        self.options = options
        logging.info("Generating new graph:")
        logging.info("  nodes: {}".format(nodes))
        logging.info("  alpha: {}".format(self.options["alpha"]))
        logging.info("  beta: {}".format(self.options["beta"]))
        logging.info("  gamma: {}".format(self.options["gamma"]))
        logging.info("  delta_in: {}".format(self.options["delta_in"]))
        logging.info("  delta_out: {}".format(self.options["delta_out"]))

        start_time = time.clock()
        self.graph = networkx.scale_free_graph(
            nodes,
            alpha=self.options["alpha"],
            beta=self.options["beta"],
            gamma=self.options["gamma"],
            delta_in=self.options["delta_in"],
            delta_out=self.options["delta_out"]
        )
        duration = time.clock() - start_time
        logging.info("Graph completed in {}sec".format(duration))
        logging.info("Nodes: {} Edges: {}".format(self.graph.number_of_nodes(), self.graph.number_of_edges()))

    def get_node(self, node_id):
        inbound = self.graph.in_edges(node_id)
        outbound = self.graph.out_edges(node_id)
        if not inbound:
            logging.error("Node: {} in: {} out: {}".format(node_id, len(inbound), len(outbound)))
        return node_id
