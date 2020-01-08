import cProfile
import functools
import pstats
from contextlib import contextmanager
from datetime import datetime
from io import StringIO
from time import time

from gprof2dot import (
    TEMPERATURE_COLORMAP,
    DotWriter,
    PstatsParser,
    TOTAL_TIME_RATIO,
    TIME_RATIO,
)


@contextmanager
def _timing(description: str) -> None:
    start = time()
    yield
    ellapsed_time = time() - start
    print(f"{description}: {ellapsed_time}")


def profile(func, *args, **kwargs):
    def decorator(func):
        try:
            func.__name__
        except AttributeError:
            # This decorator is on top of another decorator implemented as class
            func.__name__ = func.__class__.__name__
        try:
            functools.update_wrapper(decorator, func)
        except AttributeError:
            pass

        def wrapper(*args, **kwargs):
            try:
                functools.update_wrapper(wrapper, func)
            except AttributeError:
                pass

            with Profiler(profiler_name, profile_sql=profile_sql):
                to_return = prof.runcall(func, *args, **kwargs)
            return to_return


class Profiler(object):
    def __init__(self, name: str, dump_dir: str = None, *args, **kwargs):
        self.stats: str = None
        self.name: str = (
            f"stats_{name.strip()}_{int(datetime.now().timestamp())}"
        )
        self.dump_dir = dump_dir
        self._prof_file = f"{dump_dir}/{self.name}.prof"
        self._csv_file = f"{dump_dir}/{self.name}.csv"
        self._dot_file = f"{dump_dir}/{self.name}.dot"
        self._png_file = f"{dump_dir}/{self.name}.png"

    def __enter__(self, *args, **kwargs):
        self.start(*args, **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        self.stats_str = self.stop(*args, **kwargs)
        self._publish_stats_to_csv(self.stats_str)
        self._publish_stats_to_dot(self.stats_str)
        self._publish_stats_to_graph(self.stats_str)
        return True

    def stop(self, *args, **kwargs):
        self.profiler.disable()
        out = StringIO()
        stats = pstats.Stats(self.profiler, stream=out)
        self.dump_dir and stats.dump_stats(self._prof_file)
        stats.sort_stats("ncalls", "tottime", "cumtime")
        stats.print_stats()
        return out.getvalue()

    def start(self, *args, **kwargs):
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        return self

    def _publish_stats_to_dot(self, stats: str, *args, **kwargs):
        if not self.dump_dir:
            return
        with open(self._dot_file, "wt", encoding="UTF-8") as output:
            theme = TEMPERATURE_COLORMAP
            theme.skew = 1.0
            profile = PstatsParser(self._prof_file).parse()
            profile.prune(0.5 / 100.0, 0.1 / 100.0, None, False)
            dot = DotWriter(output)
            dot.strip = False
            dot.wrap = False
            dot.show_function_events = [TOTAL_TIME_RATIO, TIME_RATIO]
            dot.graph(profile, theme)

    def _publish_stats_to_graph(self, stats: str, *args, **kwargs):
        if not self.dump_dir:
            return
        return None

    def _publish_stats_to_csv(self, stats: str, *args, **kwargs):
        if not self.dump_dir:
            return
        # chop the string into a csv-like buffer
        res = "ncalls" + stats.split("ncalls")[-1]
        # save it to disk
        with open(self._csv_file, "w",) as f:
            f.write(
                "\n".join(
                    [
                        self._get_csv_line_item(ln.rstrip())
                        for ln in res.split("\n")
                    ]
                )
            )

    def _get_csv_line_item(self, line):
        line = line.split("{", 2)
        if len(line) < 2:
            return ",".join(line[0].split(None, 6))
        stats, function_name = line
        stats = stats.split(None, 6)
        stats.append("{" + function_name)
        return ",".join(stats)
