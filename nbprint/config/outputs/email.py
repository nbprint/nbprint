from pathlib import Path
from typing import Literal, Tuple

from ccflow import BaseModel
from emails import Message as EmailMessage
from jinja2 import Environment
from nbformat import NotebookNode
from pydantic import Field, field_validator, model_validator

from nbprint.config import Configuration, OutputsProcessing

from .nbconvert import NBConvertOutputs

__all__ = ("SMTP", "EmailOutputs")


class SMTP(BaseModel):
    host: str = Field(..., description="SMTP server host")
    port: int | None = Field(default=25, description="SMTP server port")
    user: str | None = Field(default=None, description="SMTP server username")
    password: str | None = Field(default=None, description="SMTP server password")
    tls: bool | None = Field(default=False, description="Use TLS for SMTP connection")
    ssl: bool | None = Field(default=False, description="Use SSL for SMTP connection")
    timeout: int | None = Field(default=30, description="Timeout for SMTP connection in seconds")


class EmailOutputs(NBConvertOutputs):
    # revert this back
    target: Literal["ipynb", "html", "webhtml", "pdf", "webpdf"] | None = "ipynb"

    body: str | None = Field(default=None, description="Body of the email, defaults to output name")
    subject: str | None = Field(default=None, description="Subject of the email, defaults to output name")
    to: list[str] = Field(description="Recipient email addresses")
    from_: Tuple[str, str] | str | None = Field(default=None, description="Sender email address")
    cc: Tuple[str, str] | str | None = Field(default=None, description="CC email address")
    bcc: Tuple[str, str] | str | None = Field(default=None, description="BCC email address")

    smtp: SMTP = Field()

    @model_validator(mode="after")
    def _validate_from_or_user(self) -> "EmailOutputs":
        if not self.from_ and not self.smtp.user:
            err = "Either message.from_ or smtp.user must be set"
            raise ValueError(err)
        if not self.from_:
            self.from_ = self.smtp.user
        if not self.smtp.user:
            self.smtp.user = self.from_[1] if isinstance(self.from_, tuple) else self.from_
        return self

    @field_validator("to", mode="before")
    @classmethod
    def _validate_to(cls, v) -> list[str]:
        if isinstance(v, str):
            return [v]
        return v

    @field_validator("from_")
    @classmethod
    def _validate_from(cls, v) -> Tuple[str, str] | str | None:
        # If tuple, must be (name, email)
        if isinstance(v, tuple):
            if len(v) != 2:  # noqa: PLR2004
                err = "from_ tuple must be (name, email)"
                raise ValueError(err)
            if not v[0]:
                return v[1]
        return v

    @field_validator("cc")
    @classmethod
    def _validate_cc(cls, v) -> Tuple[str, str] | str | None:
        # If tuple, must be (name, email)
        if isinstance(v, tuple):
            if len(v) != 2:  # noqa: PLR2004
                err = "cc tuple must be (name, email)"
                raise ValueError(err)
            if not v[0]:
                return v[1]
        return v

    @field_validator("bcc")
    @classmethod
    def _validate_bcc(cls, v) -> Tuple[str, str] | str | None:
        # If tuple, must be (name, email)
        if isinstance(v, tuple):
            if len(v) != 2:  # noqa: PLR2004
                err = "bcc tuple must be (name, email)"
                raise ValueError(err)
            if not v[0]:
                return v[1]
        return v

    def make_message(self, config: "Configuration", output_path: Path) -> EmailMessage:
        default_output_name = self._output_name(config=config)

        env = Environment(autoescape=True)
        msg = EmailMessage(
            html=env.from_string(self.body or default_output_name).render(config.parameters.model_dump(exclude_unset=True)),
            subject=env.from_string(self.subject or default_output_name).render(config.parameters.model_dump(exclude_unset=True)),
            mail_from=self.from_,
            mail_to=self.to,
            cc=self.cc,
            bcc=self.bcc,
        )
        msg.attach(filename=output_path.name, content_disposition="attachment", data=output_path.read_bytes())
        return msg

    def run(self, config: "Configuration", gen: NotebookNode) -> Path:
        # generate the output file
        output_path = super().run(config=config, gen=gen)

        if output_path in (None, OutputsProcessing.STOP):
            return OutputsProcessing.STOP

        if not self._multi:
            msg = self.make_message(config=config, output_path=output_path)
            smtp_config = self.smtp.model_dump(exclude_unset=True, exclude_none=True, exclude=["type_"])
            smtp_config["fail_silently"] = False

            # TODO: deal with batch mode
            response = msg.send(to=self.to, smtp=smtp_config)
            if not response.success:
                err = f"Failed to send email: {response.error}"
                raise RuntimeError(err)
        return output_path
