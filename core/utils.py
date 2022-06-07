import pathlib
import re
import uuid

from django.conf import settings
from django.utils.html import strip_tags


def user_directory_path(self, filename: str, subdir="other") -> str:
    """
    Function that generates path of an uploaded file.
    File will be uploaded to MEDIA_ROOT/uploads/user_<id>/<subdir>/<uuid64 value of filename>.

    Use like this:

    submission_file = models.FileField(
        upload_to=partial(user_directory_path, subdir="submissions")
    )
    """

    ext = pathlib.Path(filename).suffix
    filename = f"{uuid.uuid4()}{ext}"

    if self.__class__.__name__ == "ShopUser":
        user_id = self.id
    else:
        try:
            user_id = f"user_{self.created_by.id}"
        except AttributeError:  # TODO: Find out why SiteConfiguration do not save the user properly
            user_id = "siteconfiguration"

    return f"uploads/{user_id}/{subdir}/{filename}"


def is_admin_logged_in(request) -> bool:
    """Return True if one of admins specified in settings.ADMINS is currently logged-in, else False"""
    return (
        True
        if [admin for admin in settings.ADMINS if request.user.email in admin]
        else False
    )


def textify_html(html):
    # Remove html tags and continuous whitespaces
    text_only = re.sub('[ \t]+', ' ', strip_tags(html))
    # Strip single spaces in the beginning of each line
    return text_only.replace('\n ', '\n').strip()


def camel_to_snake(name: str) -> str:
    """Converts string in CamelCase to snake_case"""
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
