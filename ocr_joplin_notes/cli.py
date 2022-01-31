# -*- coding: utf-8 -*-

"""Console script for ocr_joplin_notes."""
import sys
import click
from ocr_joplin_notes import run_ocr
import ocr_joplin_notes


def parse_argument(arg):
    """Helper function for wild arguments"""
    if arg in ["No", "N", "NO", "OFF", "off", "n", "no"]:
        return "no"
    else:
        return "yes"


@click.command()
@click.option(
    "--mode",
    "mode",
    default="",
    help="""Specify the mode""",
)
@click.option(
    "--tag",
    "tag",
    default=None,
    help="""Specify the Joplin tag""",
)
@click.option(
    "--exclude_tags",
    "exclude_tags",
    default=None,
    multiple=True,
    help="""Specify the Joplin tags to be excluded""",
)
@click.option(
    "-l",
    "--language",
    "language",
    default="eng",
    help="""Specify the OCR Language. Refer to the Tesseract documentation found here: 
    https://github.com/tesseract-ocr/tesseract/wiki""",
)
@click.option(
    "--add-previews",
    "add_previews",
    default="yes",
    help="""Specify whether to add preview images to the note, when a PDF file is processed. """
    """Default = yes (specify 'no' to disable). """,
)
@click.option(
    "--autorotation",
    "autorotation",
    default="yes",
    help="""Specify whether to rotate images."""
         """ Default = yes (specify 'no' to disable). """,
)
@click.version_option(version=ocr_joplin_notes.__version__)
def main(
        mode="",
        tag=None,
        exclude_tags=None,
        language="eng",
        add_previews="yes",
        autorotation="yes",
):
    f""" Console script for ocr_joplin_notes.
         ocr_joplin_nodes <mode> 
    """
    run_ocr.set_mode(mode)
    run_ocr.set_language(language)
    run_ocr.set_autorotation(parse_argument(autorotation))
    run_ocr.set_add_previews(parse_argument(add_previews))
    click.echo("Mode: " + mode)
    if tag is not None:
        click.echo("Tag: " + tag)
    if exclude_tags is not None:
        click.echo("Exclude Tags: " + str(exclude_tags))
    click.echo("Language: " + language)
    click.echo("Add previews: " + add_previews)
    click.echo("Autorotation: " + autorotation)
    res = run_ocr.run_mode(mode, tag, exclude_tags)
    if res == 0:
        click.echo("Finished")
        return 0
    else:
        click.echo("Aborted")
        return res


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
