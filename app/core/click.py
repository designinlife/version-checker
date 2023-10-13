from click.core import Option
from click.formatting import join_options


class ClickStdOption(Option):

    def get_help_record(self, ctx):
        if self.hidden:
            return
        any_prefix_is_slash = []

        def _write_opts(opts):
            rv1, any_slashes = join_options(opts)
            if any_slashes:
                any_prefix_is_slash[:] = [True]

            return rv1

        rv = [_write_opts(self.opts)]
        if self.secondary_opts:
            rv.append(_write_opts(self.secondary_opts))

        help_s = self.help or ''
        extra = []

        if self.required:
            extra.append('*')
        if extra:
            help_s = '%s\033[38;5;196m%s\033[0m' % (help_s and help_s + ' ' or '', '; '.join(extra))

        return (any_prefix_is_slash and '; ' or ' / ').join(rv), help_s
