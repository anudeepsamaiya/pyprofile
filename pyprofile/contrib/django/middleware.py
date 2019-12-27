# Original version taken from https://djangosnippets.org/snippets/605/
# Orignal version taken from http://www.djangosnippets.org/snippets/186/
# Original author: udfalkso, hauser
# Modified by: Anudeep Samaiya

import re

from django.conf import settings

from pyprofile import Profiler

words_re = re.compile(r"\s+")

group_prefix_re = [
    re.compile("^.*/django/[^/]+"),
    re.compile("^(.*)/[^/]+$"),  # extract module path
    re.compile(".*"),  # catch strange entries
]


class RequestProfilingMiddleware(object):
    """
    Displays cProfile profiling for any view.
    http://yoursite.com/yourview/?prof

    Add the "prof" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser.
    It's set up to only be available in django's debug mode, is available for superuser otherwise,
    but you really shouldn't add this middleware to any production configuration.

    WARNING: It uses cProfile profiler which is not thread safe.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.query_params = dict(request.GET)
        path = request.get_full_path()
        path = path.split("?")[0]

        if not (
            (settings.DEBUG and settings.PROFILING) and self.query_params.get("prof")
        ):
            return self.get_response(request)

        with Profiler(str(path).replace("/", "_")) as self.prof:
            response = self.get_response(request)
        stats_str = self.prof.stats_str

        if response and response.content and stats_str:
            response.content = "<pre>" + stats_str + "</pre>"
        response.content = "\n".join(response.content.decode().split("\n")[:100])
        response.content += str.encode(self.summary_for_files(stats_str))
        return response

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if (settings.DEBUG and settings.PROFILING) and self.query_params.get("prof"):
            return self.prof.profiler.runcall(
                callback, request, *callback_args, **callback_kwargs
            )

    def get_group(self, _file):
        for g in group_prefix_re:
            name = g.findall(_file)
            if name:
                return name[0]

    def get_summary(self, results_dict, _sum):
        list = [(item[1], item[0]) for item in results_dict.items()]
        list.sort(reverse=True)
        list = list[:40]

        res = "      tottime\n"
        for item in list:
            res += "%4.1f%% %7.3f %s\n" % (
                100 * item[0] / _sum if _sum else 0,
                item[0],
                item[1],
            )

        return res

    def summary_for_files(self, stats_str):
        stats_str = stats_str.split("\n")[5:]

        mystats = {}
        mygroups = {}

        _sum = 0

        for s in stats_str:
            fields = words_re.split(s)
            if len(fields) == 7:
                time = float(fields[2])
                _sum += time
                _file = fields[6].split(":")[0]

                if not _file in mystats:
                    mystats[_file] = 0
                mystats[_file] += time

                group = self.get_group(_file)
                if not group in mygroups:
                    mygroups[group] = 0
                mygroups[group] += time

        return (
            "<pre>"
            + " ---- By file ----\n\n"
            + self.get_summary(mystats, _sum)
            + "\n"
            + " ---- By group ---\n\n"
            + self.get_summary(mygroups, _sum)
            + "</pre>"
        )
