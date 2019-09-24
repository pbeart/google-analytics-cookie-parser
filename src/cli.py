"""
Becomes the executable which provides a command line interface for the parser
"""

import sys
import os

import csv

import click

import cookie_parser
import general_helpers

@click.group()
@click.option('--input', '-i', required=True, type=click.Path(exists=True,
                                                              dir_okay=False,
                                                              writable=False))
@click.option("--browser", "-b", required=True, type=click.Choice(["firefox.3+", "csv"]))
@click.pass_context
def cli(ctx, input, browser): # pylint: disable=redefined-builtin
    """
    Google Analytics Cookie Parser, developed by Patrick Beart.
    """
    click.echo(click.style("Processing cookie file...", "cyan"))
    cookies = ["_ga", "__utma", "__utmb", "__utmz"]

    # Provide all subcommands with the parser object
    ctx.obj = cookie_parser.get_cookie_fetcher(browser, input, cookies)
    if ctx.obj.error is not None:
        click.echo(click.style(ctx.obj.error, "red"))
        sys.exit()

@cli.command()
@click.pass_context
def info(ctx):
    """
    Shows information about parsed cookies and found domains
    """
    cookie_count = ctx.obj.get_cookie_count()
    domain_count = len(ctx.obj.get_domains())

    info_template = "Found {} GA cookies over {} domains"

    click.echo(click.style(info_template.format(cookie_count, domain_count),
                           fg="yellow"))

@cli.command()
@click.pass_context
def list_domains(ctx):
    """
    Shows a list of domains found in input file
    """
    click.echo(click.style("Found domains with GA cookies:\n", fg="cyan"))
    for domain in ctx.obj.get_domains():
        click.echo(domain)


@cli.command()
@click.option("--domain", "-d", required=True)
@click.pass_context
def domain_info(ctx, domain):
    """
    Shows information parsed from the input file for the specified domain
    """
    click.echo(click.style("Info found for selected domain:\n", fg="cyan"))
    info_dict = ctx.obj.get_domain_info(domain)

    formatted = general_helpers.format_string_default(general_helpers.DOMAIN_INFO_TEMPLATE,
                                                      info_dict)

    click.echo(formatted)

@cli.command()
@click.option("--output", "-o", required=True, type=click.Path(exists=True,
                                                               file_okay=False))
@click.pass_context
def export_csv(ctx, output):
    """
    Exports all found GA cookie data to the selected output directory
    """
    conflicts = []

    # Check whether any of the files we want to write already exists
    for filename in general_helpers.COOKIE_FILENAMES.values():
        # If we find a conflict...
        if os.path.exists(os.path.join(output, filename)):
            conflicts.append(filename) # Add it to the list

    if conflicts:
        click.confirm(click.style("{} already exist(s).\n"\
"Do you want to replace it/them?".format(", ".join(conflicts)), "yellow"),
                      abort=True) # If they say no then end the program

    # Didn't abort

    for cookie in general_helpers.COOKIE_FILENAMES:
        try:
            with open(os.path.join(output,
                                   general_helpers.COOKIE_FILENAMES[cookie]),
                      "w",
                      newline="\n") as csvfile:

                writer = csv.writer(csvfile,
                                    delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)

                writer.writerows(ctx.obj.get_cookies(cookie))
        except PermissionError: # Unable to write to cookie file
            message = "Could not export cookies because access\
was denied to {}.\n(You probably have it open in another program)\
".format(general_helpers.COOKIE_FILENAMES[cookie])

            click.echo(click.style(message, "red"))
            return

    click.echo(click.style("Successfully exported cookies", "green"))

cli() # pylint: disable=no-value-for-parameter
