#!/usr/bin/env python
import re
import json
import socket
import time
import redis
import numpy as np

from random import sample
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flup.server.fcgi import WSGIServer
from libgraphitestat.frontstat_web import FrontStatModel

app = Flask(__name__)
app.config.from_object(__name__)
url_prefix = '/affinite'


@app.before_request
def before_request():
    try:
        r = redis.StrictRedis(host='localhost', port=6379, db=3)
    except Exception, e:
        app.logger.error("Failed to connect to redis %s" % e)
        abort(500)
    g.db = r
    pass

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        pass

@app.route(url_prefix+'/', methods = ['GET',])
def frontstat():
    return render_template("index.html")

@app.route(url_prefix+'/remove_graph', methods = ['GET',])
def remove_graph():
    try:
        name = request.args.get("graph_name")
    except Exception, e:
        app.logger.error("Graph name is not defined")
        abort(500)
    if g.db.sismember("graphs_list", name):
        g.db.srem("graphs_list", name)
        g.db.delete("graph:%s" % name)
        app.logger.debug("removed %s" % name)
    return "OK"

@app.route(url_prefix+'/save_graph', methods = ['POST',])
def save_graph():
    try:
        name = request.form.get("graph_name")
        graph = request.form.get("graph_settings")
    except Exception, e:
        app.logger.error("Some data is not defined")
        abort(500)

    g.db.set("graph:%s" % name, graph)
    g.db.sadd("graphs_list", "%s" % name)
    app.logger.debug("%s: [ %s ]" % (name, graph))
    return "OK"

@app.route(url_prefix+'/list_graphs', methods = ['GET', ])
def list_graphs():
    glist = g.db.smembers("graphs_list")
    return render_template("graphs_list.html", graphs_list = glist)

@app.route(url_prefix+'/show_graph', methods = ['GET', ])
def show_graph():
    try:
        name = request.args.get("graph_name")
    except Exception, e:
        app.logger.error("Failed to get name %s" % e)
        abort(500)
    if g.db.sismember("graphs_list", name):
        graph = g.db.get("graph:%s" % name)
        app.logger.debug("got graph %s" % graph)
    else:
        return list_graphs()
    return render_template("show_graph.html", graph = graph)

@app.route(url_prefix+'/data', methods =  ['GET', ])
def json_data():
    try:
        x = request.args.get('x_metric')
        y = request.args.get('y_metric')
        pfrom = request.args.get('from')
        delta = request.args.get('delta')
        renderer = request.args.get('renderer')
        gtype = request.args.get('type')
        color = request.args.get('color')
    except Exception, e:
        app.logger.error("Failed to get some data from request %(, %s" % e)
        abort(500)
    
    for item in [x, y, pfrom, delta, renderer, gtype, color]:
        app.logger.debug(item)
        if not item:
            app.logger.error("not all options defined")
            abort(500)

    # try to build frontstat module from this input
#    try:
    stat = FrontStatModel(debug=1)
    stat.calculate_polyf(x, y, int(pfrom), int(delta))
#    except Exception, e:
#        app.logger.error("Failed to build fronstat model %s" % e)
#        abort(500)
    if gtype == "raw":
        raw_data = np.column_stack((stat.d[:,0], stat.d[:,1]))
    elif gtype == "polyfit":
        raw_data = np.column_stack((stat.d[:,0], stat.f(stat.d[:,0])))

    if color == "random":
        color = "palette.color()"

    data = { "data": [ { "x": x, "y": y } for x,y in raw_data.tolist() ],
             "renderer": renderer,
             "color": color
            }

    return json.dumps(data)
    
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
