from jinja2 import Environment, FileSystemLoader
from pathlib import Path


def render_final_report_html(data: dict) -> str:
    """Render the final report HTML using the Jinja2 template."""
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("final_report_template.html")
    return template.render(**data)
