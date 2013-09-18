import logging
import os
import multiprocessing
import time

import tornado.template

import ponzi.graph


class Ponzi(object):

    def __init__(self, options):
        logging.info("Starting Ponzi")
        self.options = options
        self.nodes = self.options["nodes"]
        self.idlen = len(str(self.nodes))
        print self.idlen
        self.pagecount = 0
        self.options['textset'] = self.load_textset()
        self.options['textlen'] = len(self.options['textset'])
        self.options['templates'] = self.load_templates()
        self.graph = self.generate_graph()
        self.queue = multiprocessing.Queue()
        for node in xrange(self.nodes):
            node_info = self.graph.get_node(node)
            self.queue.put(node_info)
        self.workers = []
        for i in range(multiprocessing.cpu_count()):
            worker = multiprocessing.Process(target=ponzi_worker, args=(i, self.queue, self.options))
            worker.start()
            self.workers.append(worker)

        for worker in self.workers:
            worker.join()
        logging.info("Completed site generation")

    def load_textset(self):
        file_path = self.options["text_file"]
        if not file_path:
            logging.info("Loading default Lorem Ipsum text")
            file_path = os.path.abspath(os.path.join("lorem.txt"))
        else:
            logging.info("Loading text file: {}".format(file_path))
        with open(file_path, "r") as f:
            textset = [line.strip() for line in f.readlines()]
        textset = filter(bool, textset)
        return textset

    def load_templates(self):
        file_paths = self.options["template_files"]
        templates = []
        if not file_paths:
            logging.info("Loading default template")
            file_paths = [os.path.abspath(os.path.join("template.html"))]
        else:
            logging.info("Loading template files: {}".format(file_paths))
        for file_path in file_paths:
            directory, file_name = os.path.split(file_path)
            template = tornado.template.Loader(directory).load(file_path)
            templates.append(template)
        return templates

    def generate_graph(self):
        return ponzi.graph.Graph(self.options["nodes"], self.options["graph"])


def ponzi_worker(worker_id, queue, options):
    logging.debug("{} initialized".format(worker_id))
    while queue.qsize() > 0:
        item = queue.get(timeout=1)
        logging.debug("{} got: {}".format(worker_id, item))
        ponzi_process(item)
    logging.info("{} finished".format(worker_id))
    return


def ponzi_process(item):
    print item
