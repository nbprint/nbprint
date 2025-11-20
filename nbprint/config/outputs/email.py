from pathlib import Path
from typing import Literal, Tuple

from ccflow import BaseModel, PyObjectPath
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

    postprocess: PyObjectPath = Field(
        default=PyObjectPath("nbprint.config.outputs.email.email_postprocess"),
        description=("A callable hook that is called after all processing completes to email the results."),
    )

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

    def make_message(self, config: "Configuration") -> EmailMessage:
        output_path = self._output_path
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
        return output_path


def email_postprocess(configs: list[Configuration]) -> None:
    """A postprocess hook to email all output files after processing completes.
    NOTE: it is assumed that all EmailOutputs instances are configured identically,
    as happens in a multi run scenario.

    Args:
        configs (list[Configuration]): The list of nbprint configuration/s.

    """
    msgs: list[EmailMessage] = []
    smtp = None

    for config in configs:
        if isinstance(config.outputs, EmailOutputs):
            msgs.append(config.outputs.make_message(config=config))
            if smtp is None:
                smtp = config.outputs.smtp.model_dump(exclude_unset=True, exclude_none=True, exclude=["type_"])
                smtp["fail_silently"] = False
    if not msgs:
        return
    # Combine message contents, adjust email and body to be the common substring, and send
    msg = msgs[0]
    if len(msgs) > 1:
        # Concatenate bodies
        combined_body = "\n\n".join([m.html for m in msgs])
        msg.html = combined_body

        # Subject may be paramterized,
        # so find the overlapping parts of the strings
        # and replace the non-overlapping parts with "*"
        subjects = [m.subject for m in msgs]
        common_subject = subjects[0]
        for subject in subjects[1:]:
            # Find common prefix
            prefix_len = 0
            for a, b in zip(common_subject, subject, strict=True):
                if a == b:
                    prefix_len += 1
                else:
                    break
            # Find common suffix
            suffix_len = 0
            for a, b in zip(reversed(common_subject), reversed(subject), strict=True):
                if a == b:
                    suffix_len += 1
                else:
                    break
            # Build new common subject
            middle_len = max(len(common_subject), len(subject)) - prefix_len - suffix_len
            common_subject = common_subject[:prefix_len] + ("*" * middle_len) + common_subject[-suffix_len if suffix_len > 0 else None :]
        msg.subject = common_subject

        # Attach all attachements
        for m in msgs[1:]:
            for attachment in m.attachments:
                msg.attachments.append(attachment)

    # Send the email
    response = msg.send(to=config.outputs.to, smtp=smtp)
    if not response.success:
        err = f"Failed to send email: {response.error}"
        raise RuntimeError(err)
