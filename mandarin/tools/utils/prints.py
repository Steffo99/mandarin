import click


def old_to_new(title, old, new, active=False) -> bool:
    old_display = f"{old}".split("\n")[0]
    new_display = f"{new}".split("\n")[0]

    click.secho(title, nl=False)
    click.secho(": ", nl=False)

    if old != new:
        if active:
            click.secho(old_display, fg="red", nl=False)
            click.secho(" -> ", nl=False)
            click.secho(new_display, fg="green", bold=True, nl=False)
            click.secho()
            return True
        else:
            click.secho(old_display, fg="yellow", bold=True, nl=False)
            click.secho(" != ", nl=False)
            click.secho(new_display, fg="red", nl=False)
            click.secho()
            return True
    else:
        click.secho(old_display, fg="blue", nl=False)
        click.secho(" == ", nl=False)
        click.secho(new_display, fg="blue", bold=True, nl=False)
        click.secho()
        return False


def tree(indent: int, text: str, has_children: bool) -> None:
    click.secho("    " * indent, nl=False)
    click.secho("- ", nl=False)
    if has_children:
        click.secho(f"{text} ", fg="cyan", bold=True, nl=False)
    else:
        click.secho(f"{text} ", fg="blue", nl=False)


def id_(number, success: bool):
    click.secho("[", nl=False)
    click.secho(f"{number}", fg="green" if success else "red", nl=False)
    click.secho("] ", nl=False)


__all__ = (
    "old_to_new",
)
