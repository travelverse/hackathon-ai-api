# -*- coding: utf-8 -*-
import functools
import click

# with typer installed default group will raise assertion
try:
    from typer.core import TyperGroup as Group
except ImportError:
    from click import Group
from click._compat import get_text_stderr  # noqa


class PrettyHelpFormatter(click.HelpFormatter):
    """Extended click.HelpFormatter with styling support.

    :param styles: styles definition, see 'configuration' documentation for more information.
    :param column_width: the maximum width of the first column.
    :param column_spacing: the number of spaces between the first and second column.
    :param width: the width for the text. this defaults to the terminal width clamped to a maximum of 78.
    :param indent_increment: the additional increment for each level.
    """

    # pylint: disable=W1113
    def __init__(self, styles=None, column_width=None, column_spacing=None, *args, **kwargs):
        self.styles = styles
        self.column_width = column_width
        self.column_spacing = column_spacing
        super().__init__(*args, **kwargs)

    def prettify(self, target, message):
        """Apply styling to message if corresponding configuration is set.

        :param target: message string type.
        :param message: message string.
        """
        if target in self.styles:
            message = click.style(message, **self.styles[target])
        return message

    def write_usage(self, prog, args="", prefix="Usage: "):
        """Writes a usage line into the buffer.

        :param prog: the program name.
        :param args: whitespace separated list of arguments.
        :param prefix: the prefix for the first line.
        """
        parts = prefix.split(":")
        prefix = ":".join([self.prettify("usage-prefix", parts[0])] + parts[1:])
        prog = self.prettify("usage-prog", prog)
        args = self.prettify("usage-args", args)
        super().write_usage(prog, args, prefix=prefix)

    def write_heading(self, heading):
        """Writes a heading into the buffer."""
        super().write_heading(self.prettify("heading", heading))

    def write_dl(self, rows, col_max=30, col_spacing=2):
        """Writes a definition list into the buffer.  This is how options
        and commands are usually formatted.

        :param rows: a list of two item tuples for the terms and values.
        :param col_max: the maximum width of the first column.
        :param col_spacing: the number of spaces between the first and second column.
        """
        for idx, row in enumerate(rows):
            if row[0][:2] == "--":
                rows[idx] = (
                    self.prettify("option-name", row[0]),
                    self.prettify("option-description", row[1])
                )
            else:
                rows[idx] = (
                    self.prettify("command-name", row[0]),
                    self.prettify("command-description", row[1]))
        super().write_dl(rows, self.column_width or col_max, self.column_spacing or col_spacing)


class UnsortedGroup(Group):
    """Override click.Group to remove command sorting."""

    def list_commands(self, ctx):
        return self.commands


# The code below is a complete hack to click's internal classes, I know it
# smells bad, but currently it is the only way to achieve desired functionality,
# when(if) click will support this then it is also a subject to change.


def style_usage_error(style):
    """click.exceptions.UsageError override.

    :param style: 'error' style definition.
    """
    def show(self, params, file=None):
        if file is None:
            file = get_text_stderr()
        color = None
        if self.ctx is not None:
            color = self.ctx.color
            click.utils.echo(self.ctx.get_usage() + "\n", file=file, color=color)
        click.utils.echo(click.style(f"Error: {self.format_message()}", **params), file=file, color=color)

    click.exceptions.UsageError.show = functools.partialmethod(show, params=style)


def style_click_exception(style):
    """click.exceptions.ClickException override.

    :param style: 'exception' style definition.
    """
    def show(self, params, file=None):
        if file is None:
            file = get_text_stderr()
        click.utils.echo(click.style(f"Error: {self.format_message()}", **params), file=file)

    click.exceptions.ClickException.show = functools.partialmethod(show, params=style)


def swap_context_formatter(styles, max_content_width, column_width, column_spacing):
    """click.core.Context override.

    :param styles: 'formatter' style definitions set.
    :param max_content_width: the maximum width for content rendered by Click.
    :param column_width: the maximum width of the first column.
    :param column_spacing: the number of spaces between the first and second column.
    """
    def make_formatter(self):
        """Creates the formatter for the help and usage output."""
        return PrettyHelpFormatter(
            width=self.terminal_width, max_width=max_content_width,
            styles=styles, column_width=column_width, column_spacing=column_spacing)

    click.core.Context.make_formatter = functools.partialmethod(make_formatter)


def setup_click(settings):
    """Apply overrides to Click."""

    style_usage_error(settings["styles"]["error"])
    style_click_exception(settings["styles"]["exception"])
    swap_context_formatter({
        key: settings["styles"][key] for key in
        [
            "usage-prefix", "usage-prog", "usage-args",
            "heading",
            "option-name", "option-description",
            "command-name", "command-description"
        ]
        if key in settings["styles"]
    },
        settings.get("max-content-width", None),
        settings.get("column-width", None),
        settings.get("column-spacing", None)
    )
