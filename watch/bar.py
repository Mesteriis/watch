from progress.bar import Bar


class TimedBar(Bar):
    suffix = '%(pos_str)s / %(dur_str)s'

    def _nice_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours:
            return '{:d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
        else:
            return '{:02d}:{:02d}'.format(minutes, seconds)

    @property
    def dur_str(self):
        return self._nice_time(self.max)

    @property
    def pos_str(self):
        return self._nice_time(self.index)
