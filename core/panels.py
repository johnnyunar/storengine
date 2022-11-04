from wagtail.admin.panels import HelpPanel


class ReadOnlyPanel(HelpPanel):
    def __init__(
            self,
            content="",
            template="wagtailadmin/panels/readonly_panel.html",
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.content = content
        self.template = template


class InvoiceLinkPanel(HelpPanel):
    def __init__(
            self,
            content="",
            template="wagtailadmin/panels/invoice_panel.html",
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.content = content
        self.template = template
