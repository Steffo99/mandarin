import click


def old_to_new(old, new) -> bool:
    old_display = f"{old}".split("\n")[0]
    new_display = f"{new}".split("\n")[0]

    if old != new:
        click.secho(old_display, fg="red", nl=False)
        click.secho(" -> ", nl=False)
        click.secho(new_display, fg="green", bold=True, nl=False)
        click.secho()
        return True
    else:
        click.secho(old_display, fg="blue", nl=False)
        click.secho(" == ", nl=False)
        click.secho(new_display, fg="blue", bold=True, nl=False)
        click.secho()
        return False


__all__ = (
    "old_to_new",
)
