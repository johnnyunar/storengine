"""Richtext hooks."""
import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineStyleElementHandler,
)
from wagtail.core import hooks


@hooks.register("insert_global_admin_css")
def global_admin_css():
    """Adding extra css class for readonly fields"""
    return format_html(
        '<link rel="stylesheet" href="{}">', static("cms/css/readonly.css")
    )


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', static("cms/css/theme.css"))


@hooks.register("register_rich_text_features")
def register_centertext_feature(features):
    """Creates centered text in our richtext editor and page."""

    feature_name = "center"
    type_ = "CENTERTEXT"
    tag = "div"

    control = {
        "type": type_,
        "icon": "grip",
        "description": "Center Text",
        "style": {
            "display": "block",
            "text-align": "center",
        },
    }

    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.InlineStyleFeature(control)
    )

    db_conversion = {
        "from_database_format": {tag: InlineStyleElementHandler(type_)},
        "to_database_format": {
            "style_map": {
                type_: {"element": tag, "props": {"class": "d-block text-center"}}
            }
        },
    }

    features.register_converter_rule("contentstate", feature_name, db_conversion)

    features.default_features.append(feature_name)
