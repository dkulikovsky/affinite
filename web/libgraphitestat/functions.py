import numpy as np
import libgraphite as lg

# get derivative
def get_derivative(d, f, xs):
    dy = []
    i = 0
    while (i <= len(xs)-2):
        dy.append(f(xs[i]) - f(xs[i+1]))
        i += 1
    # and count the last one
    dy.append(f(xs[-2]) - f(xs[-1]))
    xy = np.column_stack((xs,dy))
    return xy

def graphite_data(metric, pfrom, until):
    q = lg.Query('https://bsgraphite.yandex-team.ru') \
        .target('%s' % metric) \
        .pfrom(pfrom).puntil(until)
    print q._url()
    res = q.execute().astype(float)
    res_data = []
    for i in xrange(len(res.values)-1):
        res_data.append(res.values[i][0])
    return res_data

def graphite_data_mc(metric, pfrom, until):
    q = lg.Query('https://bsgraphite.yandex-team.ru') \
        .target('%s' % metric) \
        .pfrom(pfrom).puntil(until)
    print q._url()
    res = q.execute().astype(float)
    return res.values

def get_util(hosts, pfrom, until):
    hosts = hosts.replace("_yandex_ru", "_rt")
    util = graphite_data('keepLastValue(averageSeries(highestAverage(one_min.%s.phantom_stat.utilization.work_scheduler_pool,3)))' % hosts, pfrom, until)
    return util

def get_util_by_host(hosts, pfrom, until):
    hosts = hosts.replace("_yandex_ru", "_rt")
    util = graphite_data_mc('keepLastValue(one_min.%s.phantom_stat.utilization.work_scheduler_pool)' % hosts, pfrom, until)
    return util

def get_timings(cluster, pfrom, until):
    timings = graphite_data('keepLastValue(one_min.bs_rt_%s.timings.partners_timings.t99)' % cluster, pfrom, until)
    return timings

def get_timings_by_host(hosts, pfrom, until):
    hosts = hosts.replace("_yandex_ru", "_rt").replace("bsst","bs")
    timings = graphite_data_mc('keepLastValue(one_min.%s.timings.partners_timings.t99)' % hosts, pfrom, until)
    return timings

def get_rps(cluster, pfrom, until):
    rps = graphite_data('sumSeries(keepLastValue(one_min.bs_rt_%s.requests.*))' % cluster, pfrom, until)
    return rps

def hget_util(host, pfrom, until):
    host = host.replace("_yandex_ru", "_rt")
    util = graphite_data('keepLastValue(one_min.%s.phantom_stat.utilization.work_scheduler_pool)' % host, pfrom, until)
    return util

def hget_timings(host, pfrom, until):
    host = host.replace("_yandex_ru", "_rt")
    timings = graphite_data('keepLastValue(one_min.%s.timings.pmatch_timings.t99)' % host, pfrom, until)
    return timings

def hget_rps(host, pfrom, until):
    host = host.replace("_yandex_ru", "_rt")
    rps = graphite_data('keepLastValue(sumSeries(one_min.%s.requests.*))' % host, pfrom, until)
    return rps
