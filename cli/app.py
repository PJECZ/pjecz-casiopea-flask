"""
CLI
"""

import importlib.util
import os
import sys

import click

CMD_FOLDER = os.path.join(os.path.dirname(__file__), "commands")
CMD_PREFIX = "cmd_"


class CLI(click.Group):
    """
    A custom Click Group that dynamically loads commands from Python files
    in the 'commands' directory that start with 'cmd_'.
    """

    def list_commands(self, ctx: click.Context) -> list[str]:
        """
        Lists command names by scanning the CMD_FOLDER.
        Command files are expected to be named like 'cmd_mycommand.py'.
        The returned command name would be 'mycommand'.
        """
        commands = []
        if not os.path.isdir(CMD_FOLDER):
            click.echo("Error: Directory 'commands' not found")
            sys.exit(1)
        for filename in os.listdir(CMD_FOLDER):
            if filename.endswith(".py") and filename.startswith(CMD_PREFIX):
                commands.append(filename[len(CMD_PREFIX) : -3])  # Remove prefix and .py suffix
        commands.sort()
        return commands

    def get_command(self, ctx: click.Context, name: str) -> click.Command:
        """
        Loads a command by its name.
        It looks for a file named 'cmd_<name>.py' in CMD_FOLDER,
        imports it, and expects to find a 'cli' attribute which is a Click command.
        """
        filename = os.path.join(CMD_FOLDER, CMD_PREFIX + name + ".py")
        if not os.path.isfile(filename):
            click.echo("Error: Command file not found")
            sys.exit(1)
        module_name_in_sys = f"__dynamic_cli_commands__.{CMD_PREFIX}{name}"
        # Use importlib to load the module from its file path
        spec = importlib.util.spec_from_file_location(module_name_in_sys, filename)
        if spec is None or spec.loader is None:
            click.echo(f"Error: Could not create module spec for command '{name}' from '{filename}'")
            sys.exit(1)
        module = importlib.util.module_from_spec(spec)
        # Add to sys.modules before execution
        sys.modules[module_name_in_sys] = module
        try:
            spec.loader.exec_module(module)
        except Exception as error:
            click.echo(f"Error: executing command module '{CMD_PREFIX}{name}.py': {error}")
            if module_name_in_sys in sys.modules:
                del sys.modules[module_name_in_sys]  # Clean up from sys.modules if loading failed
            sys.exit(1)
        if not hasattr(module, "cli"):
            click.echo(f"Error: Command module '{CMD_PREFIX}{name}.py' is missing the 'cli' attribute.")
            if module_name_in_sys in sys.modules:
                del sys.modules[module_name_in_sys]  # Clean up from sys.modules if loading failed
            sys.exit(1)
        command_obj = getattr(module, "cli")
        if not isinstance(command_obj, click.Command):
            click.echo(f"Error: The 'cli' attribute in '{CMD_PREFIX}{name}.py' is not a Click command instance")
            if module_name_in_sys in sys.modules:  # Cleanup
                del sys.modules[module_name_in_sys]
            sys.exit(1)
        return command_obj


@click.command(cls=CLI, name="cli")  # 'name' sets the invocation name of this group
def cli():
    """
    Herramienta CLI principal que carga comandos dinámicamente desde la carpeta 'commands'.

    Cada archivo .py en 'commands/' que comience con 'cmd_' se considera un comando.
    Por ejemplo, 'cmd_miorden.py' se cargará como el comando 'miorden'.
    """


if __name__ == "__main__":
    cli()
