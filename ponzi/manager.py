import collections
import logging
import multiprocessing
import os
import random
import shutil
import zipfile

import tornado.template

import ponzi.s3


class Ponzi(object):
    def __init__(self, options):
        logging.info("Starting Ponzi")
        self.options = options
        self.nodes = self.options["nodes"]
        self.pagecount = 0
        self.options['textset'] = self.load_textset()
        self.options['textlen'] = len(self.options['textset'])
        self.options['templates'] = self.load_templates()
        self.options['output_dir'] = self.setup_outputdir()
        self.load_graph()
        self.queue = multiprocessing.Queue()
        for node, edges in self.graph.items():
            self.queue.put([node, edges])
        self.workers = []
        for i in range(20):
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

    def load_graph(self):
        graph_path = self.options["graph"]
        nodes = self.options["nodes"]
        maxnode = 0
        if os.path.exists(os.path.abspath(graph_path)):
            with zipfile.ZipFile(graph_path, "r") as zipf:
                infolist = zipf.infolist()
                rows = [row.strip() for row in zipf.read(infolist[0]).split("\n")]

            self.graph = collections.defaultdict(list)
            for row in rows:
                try:
                    node, edge = row.split("\t")
                    if int(node) > maxnode:
                        maxnode = int(node)
                except ValueError:
                    continue
                if int(node) > nodes or int(edge) > nodes:
                    continue
                self.graph[int(node)].append(int(edge))
        else:
            raise Exception("Dataset does not exist: {}".format(graph_path))
        logging.info("Max node: {}".format(maxnode))
        for x in range(nodes):
            logging.debug("Node test: {} {}".format(x, self.graph[x]))

    def setup_outputdir(self):
        dirpath = self.options["output_dir"]
        if not dirpath:
            dirpath = "/tmp/ponzi"
            logging.info("Using default temp directory: {}".format(dirpath))
        else:
            logging.info("Using temp directory: {}".format(dirpath))
        if os.path.isdir(dirpath):
            logging.info("Clearing directory: {}".format(dirpath))
            shutil.rmtree(dirpath)
        logging.info("Making directory: {}".format(dirpath))
        os.mkdir(dirpath)
        return dirpath


def ponzi_worker(worker_id, queue, options):
    logging.debug("{} initialized".format(worker_id))
    s3 = None
    if options["s3"]["use"]:
        s3 = ponzi.s3.S3(options["s3"])
        logging.warning("Setup S3")
    while queue.qsize() > 0:
        page_id, out_nodes = queue.get(timeout=1)
        logging.debug("{} got: {}".format(worker_id, page_id))
        ponzi_process(page_id, out_nodes, options, s3=s3)
    logging.info("{} finished".format(worker_id))
    return


def ponzi_process(page_id, out_nodes, options, s3=None):
    templates = options["templates"]
    text = options["textset"]
    output_dir = options["output_dir"]

    # select random template from templates
    template = random.choice(templates)
    content_len = random.randint(1, options["textlen"])
    content = ["<p>{}</p>".format(paragraph) for paragraph in [random.choice(text) for _ in range(content_len)]]
    for node in out_nodes:
        link = """<a href="/{0}.html">Node {0}</a>""".format(node)
        content.insert(random.randint(1, content_len), link)
    page = template.generate(title=page_id, content="\n".join(content))
    file_name = "{}.html".format(page_id)
    out_file = os.path.join(output_dir, file_name)
    with open(out_file, "w") as f:
        f.write(page)
    if options["s3"]["use"]:
        s3.send_file(out_file, file_name)
