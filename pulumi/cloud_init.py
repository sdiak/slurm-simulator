"""Cloud init template renders
"""
from jinja2 import Environment, PackageLoader, select_autoescape, StrictUndefined

env = Environment(
    loader=PackageLoader("cloud_init"),
    autoescape=select_autoescape(),
    trim_blocks=True,
    undefined=StrictUndefined
)

def cloud_init_rendered(*args, **kwargs) -> str:
    return env.get_template("cloud_init.cfg.jinja").render(*args, **kwargs)

def network_config_rendered(*args, **kwargs):
    return env.get_template("network_config.cfg.jinja").render(*args, **kwargs)