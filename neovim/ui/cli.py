"""CLI for accessing the gtk/tickit UIs implemented by this package."""
import shlex

import click

from .gtk_ui import GtkUI
from .ui_bridge import UIBridge
from .. import attach


@click.command(context_settings=dict(allow_extra_args=True))
@click.option('--nvim-command', default='nvim --embed')
@click.option('--profile',
              default='disable',
              type=click.Choice(['ncalls', 'tottime', 'percall', 'cumtime',
                                 'name', 'disable']))
@click.pass_context
def main(ctx, nvim_command, profile):
    """Entry point."""
    nvim = attach('child', argv=shlex.split(nvim_command) + ctx.args)
    ui = GtkUI()
    bridge = UIBridge()
    bridge.connect(nvim, ui, profile if profile != 'disable' else None)
