import sys
import click
import cookie_parser, general_helpers

@click.group()
@click.option('--input', '-i', required=True, type=click.Path(exists=True))
@click.option("--browser", "-b", required=True, type=click.Choice(["firefox.3+", "csv"]))
@click.pass_context
def cli(ctx, input, browser):
    """
    Google Analytics Cookie Parser, developed by Patrick Beart.
    """
    # TODO: seperately keep track of default cookie list
    cookies = ["_ga", "__utma", "__utmb", "__utmz"]
    ctx.obj = cookie_parser.get_cookie_fetcher(browser, input, cookies)
    if ctx.obj.error:
        click.echo(click.style(ctx.obj.error, "red"))
        sys.exit()


@cli.command()
@click.pass_context
def get_domains(ctx):
    """
    Returns a list of domains found in input file
    """
    click.echo(click.style("Found domains with GA cookies:\n", fg="yellow"))
    for domain in ctx.obj.get_domains():
        click.echo(domain)
    

@cli.command()
@click.option("--domain", "-d", required=True)
@click.pass_context
def domain_info(ctx, domain):
    """
    Shows information parsed from the input file for the specified domain
    """
    click.echo(click.style("Info found for selected domain:\n", fg="yellow"))
    info_dict = ctx.obj.get_domain_info(domain)

    formatted = general_helpers.format_string_default(general_helpers.DOMAIN_INFO_TEMPLATE,
                                                      info_dict)

    click.echo(formatted)

cli()