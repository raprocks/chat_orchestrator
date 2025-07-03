"""
WhatsAppSender: Send messages via the WhatsApp Cloud API.

Description:
    Sends all supported WhatsApp message types (text, media, interactive, template, reaction, contextual replies, location, contacts, etc.) using the official WhatsApp Cloud API.
    Strictly typed with TypedDict, Literal, and Union for payloads and options.

How to initialize:
    sender = WhatsAppSender(phone_number_id="<ID>", access_token="<TOKEN>", api_version="v19.0")

Options (WhatsAppPayload):
    The 'options' parameter must be one of the following TypedDicts, each corresponding to a WhatsApp message type:

    - TextPayload:      {"type": "text", "text": {"body": str, ...}, "context": dict | None}
    - ImagePayload:     {"type": "image", "image": {...}, "context": dict | None}
    - AudioPayload:     {"type": "audio", "audio": {...}, "context": dict | None}
    - VideoPayload:     {"type": "video", "video": {...}, "context": dict | None}
    - DocumentPayload:  {"type": "document", "document": {...}, "context": dict | None}
    - StickerPayload:   {"type": "sticker", "sticker": {...}, "context": dict | None}
    - LocationPayload:  {"type": "location", "location": {...}, "context": dict | None}
    - ContactsPayload:  {"type": "contacts", "contacts": [...], "context": dict | None}
    - ReactionPayload:  {"type": "reaction", "reaction": {...}, "context": dict | None}
    - TemplatePayload:  {"type": "template", "template": {...}, "context": dict | None}
    - InteractivePayload: {"type": "interactive", "interactive": {...}, "context": dict | None}

    See WhatsApp Cloud API docs for the exact structure of each payload type.
    If 'options' is None, a simple text message is sent using the 'text' argument.
"""

import requests
from typing import Any, Optional, TypedDict, Literal, Union, Dict, cast
from ..senders.base import MessageSender
from loguru import logger


class ContextPayload(TypedDict):
    message_id: str


# --- TypedDicts for WhatsApp message payloads ---
class TextPayload(TypedDict, total=True):
    type: Literal["text"]
    text: Dict[str, Any]
    context: ContextPayload | None


class ImagePayload(TypedDict, total=True):
    type: Literal["image"]
    image: Dict[str, Any]
    context: ContextPayload | None


class AudioPayload(TypedDict, total=True):
    type: Literal["audio"]
    audio: Dict[str, Any]
    context: ContextPayload | None


class VideoPayload(TypedDict, total=True):
    type: Literal["video"]
    video: Dict[str, Any]
    context: ContextPayload | None


class DocumentPayload(TypedDict, total=True):
    type: Literal["document"]
    document: Dict[str, Any]
    context: ContextPayload | None


class StickerPayload(TypedDict, total=True):
    type: Literal["sticker"]
    sticker: Dict[str, Any]
    context: ContextPayload | None


class LocationPayload(TypedDict, total=True):
    type: Literal["location"]
    location: Dict[str, Any]
    context: ContextPayload | None


class ContactsPayload(TypedDict, total=True):
    type: Literal["contacts"]
    contacts: Any
    context: ContextPayload | None


class ReactionPayload(TypedDict, total=True):
    type: Literal["reaction"]
    reaction: Dict[str, Any]
    context: ContextPayload | None


class TemplatePayload(TypedDict, total=True):
    type: Literal["template"]
    template: Dict[str, Any]
    context: ContextPayload | None


class InteractivePayload(TypedDict, total=True):
    type: Literal["interactive"]
    interactive: Dict[str, Any]
    context: ContextPayload | None


WhatsAppPayload = Union[
    TextPayload,
    ImagePayload,
    AudioPayload,
    VideoPayload,
    DocumentPayload,
    StickerPayload,
    LocationPayload,
    ContactsPayload,
    ReactionPayload,
    TemplatePayload,
    InteractivePayload,
]


class WhatsAppSender(MessageSender):
    """
    WhatsAppSender: Send messages via the WhatsApp Cloud API.

    Description:
        Sends all supported WhatsApp message types (text, media, interactive, template, reaction, contextual replies, location, contacts, etc.) using the official WhatsApp Cloud API.
        Strictly typed with TypedDict, Literal, and Union for payloads and options.

    How to initialize:
        sender = WhatsAppSender(phone_number_id="<ID>", access_token="<TOKEN>", api_version="v19.0")

    Options (WhatsAppPayload):
        The 'options' parameter must be one of the following TypedDicts, each corresponding to a WhatsApp message type:

        - TextPayload:      {"type": "text", "text": {"body": str, ...}, "context": dict | None}
        - ImagePayload:     {"type": "image", "image": {...}, "context": dict | None}
        - AudioPayload:     {"type": "audio", "audio": {...}, "context": dict | None}
        - VideoPayload:     {"type": "video", "video": {...}, "context": dict | None}
        - DocumentPayload:  {"type": "document", "document": {...}, "context": dict | None}
        - StickerPayload:   {"type": "sticker", "sticker": {...}, "context": dict | None}
        - LocationPayload:  {"type": "location", "location": {...}, "context": dict | None}
        - ContactsPayload:  {"type": "contacts", "contacts": [...], "context": dict | None}
        - ReactionPayload:  {"type": "reaction", "reaction": {...}, "context": dict | None}
        - TemplatePayload:  {"type": "template", "template": {...}, "context": dict | None}
        - InteractivePayload: {"type": "interactive", "interactive": {...}, "context": dict | None}

        See WhatsApp Cloud API docs for the exact structure of each payload type.
        If 'options' is None, a simple text message is sent using the 'text' argument.
    """

    def __init__(
        self, phone_number_id: str, access_token: str, api_version: str = "v19.0"
    ):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.api_version = api_version
        self.endpoint = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"

    def send_message(
        self,
        chat_id: str,
        text: Optional[str],
        options: Optional[WhatsAppPayload] = None,
    ):
        payload = self._build_payload(chat_id, text, options)
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        response = requests.post(self.endpoint, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(response.json())

    def _build_payload(
        self, chat_id: str, text: Optional[str], options: Optional[WhatsAppPayload]
    ) -> dict:
        base: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": chat_id,
        }
        if options is None:
            # Default to text message
            if text is None:
                raise ValueError("Text must be provided for default text message.")
            base["type"] = "text"
            base["text"] = {"body": text}
            return base
        # Contextual reply
        context = options.get("context") if isinstance(options, dict) else None
        if context is not None:
            base["context"] = context
        msg_type = options["type"]
        base["type"] = msg_type
        # Strict type narrowing using cast
        if msg_type == "text":
            text_opts = cast(TextPayload, options)
            base["text"] = text_opts["text"]
        elif msg_type == "image":
            image_opts = cast(ImagePayload, options)
            base["image"] = image_opts["image"]
        elif msg_type == "audio":
            audio_opts = cast(AudioPayload, options)
            base["audio"] = audio_opts["audio"]
        elif msg_type == "video":
            video_opts = cast(VideoPayload, options)
            base["video"] = video_opts["video"]
        elif msg_type == "document":
            doc_opts = cast(DocumentPayload, options)
            base["document"] = doc_opts["document"]
        elif msg_type == "sticker":
            sticker_opts = cast(StickerPayload, options)
            base["sticker"] = sticker_opts["sticker"]
        elif msg_type == "location":
            loc_opts = cast(LocationPayload, options)
            base["location"] = loc_opts["location"]
        elif msg_type == "contacts":
            contacts_opts = cast(ContactsPayload, options)
            base["contacts"] = contacts_opts["contacts"]
        elif msg_type == "reaction":
            react_opts = cast(ReactionPayload, options)
            base["reaction"] = react_opts["reaction"]
        elif msg_type == "template":
            template_opts = cast(TemplatePayload, options)
            base["template"] = template_opts["template"]
        elif msg_type == "interactive":
            interactive_opts = cast(InteractivePayload, options)
            base["interactive"] = interactive_opts["interactive"]
        else:
            raise ValueError(f"Unsupported WhatsApp message type: {msg_type}")
        return base
