import click
import cookie_parser, constants

@click.group()
@click.option('--input', '-i', required=True, type=click.Path(exists=True))
@click.option("--browser", "-b", required=True, type=click.Choice(["firefox.3+", "csv"]))
@click.pass_context
def cli(ctx, input, browser):
    """
    Handles all commands in group
    """
    # TODO: seperately keep track of default cookie list
    cookies = ["_ga", "__utma", "__utmb", "__utmz"]
    ctx.obj = cookie_parser.get_cookie_fetcher(browser, input, cookies)



@cli.command()
@click.pass_context
def get_domains(ctx):
    """
    Handles the get-domains command
    """
    click.echo("Found domains with GA cookies: ")
    for domain in ctx.obj.get_domains():
        click.echo(domain)

@cli.command()
@click.option("--domain", "-d", required=True)
@click.pass_context
def domain_info(ctx):
    click.echo(str(ctx))

cli()