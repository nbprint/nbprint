from pathlib import Path
from typing import Literal, Optional

from ccflow_email import SMTP, Attachment, Email, Message
from nbformat import NotebookNode
from pydantic import Field, field_validator

from nbprint.config import Configuration

from .nbconvert import NBConvertOutputs

__all__ = ("EmailOutputs",)


class EmailOutputs(NBConvertOutputs):
    # revert this back
    target: Optional[Literal["ipynb", "html", "pdf", "webpdf"]] = "ipynb"

    body: Optional[str] = Field(default=None, description="Body of the email, defaults to output name")
    subject: Optional[str] = Field(default=None, description="Subject of the email, defaults to output name")
    to: list[str] = Field(description="Recipient email addresses")

    smtp: SMTP = Field()

    @field_validator("to", mode="before")
    @classmethod
    def _validate_to(cls, v) -> list[str]:
        if isinstance(v, str):
            return [v]
        return v

    def run(self, config: "Configuration", gen: NotebookNode) -> Path:
        # generate the output file
        output_path = super().run(config=config, gen=gen)

        default_output_name = self._output_name(config=config)

        # create the email message
        message = Message(
            content=self.body or default_output_name,
            subject=self.subject or default_output_name,
        )

        # create the email
        email = Email(
            message=message,
            smtp=self.smtp,
            attachments=[Attachment(filename=output_path.name, data=output_path.read_bytes())],
        )

        # send the email
        email.send(to=self.to)

        return output_path
