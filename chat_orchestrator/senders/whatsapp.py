"""Message sender for the WhatsApp Cloud API.

This module provides a `WhatsAppSender` class to send various types of messages
through the official WhatsApp Cloud API. It includes strictly typed dictionaries
for all supported message payloads, ensuring that the data sent to the API is
correctly formatted.

For more information on the message payloads, see the official WhatsApp Cloud API
documentation: https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages
"""
import requests
from typing import Any, Optional, TypedDict, Literal, Union, Dict, cast
from ..senders.base import MessageSender
from loguru import logger


class ContextPayload(TypedDict):
    """A payload for providing context to a message, such as replying to another message."""
    message_id: str


# --- TypedDicts for WhatsApp message payloads ---
class TextPayload(TypedDict, total=True):
    """Payload for sending a text message."""
    type: Literal["text"]
    text: Dict[str, Any]
    context: Optional[ContextPayload]


class ImagePayload(TypedDict, total=True):
    """Payload for sending an image message."""
    type: Literal["image"]
    image: Dict[str, Any]
    context: Optional[ContextPayload]


class AudioPayload(TypedDict, total=True):
    """Payload for sending an audio message."""
    type: Literal["audio"]
    audio: Dict[str, Any]
    context: Optional[ContextPayload]


class VideoPayload(TypedDict, total=True):
    """Payload for sending a video message."""
    type: Literal["video"]
    video: Dict[str, Any]
    context: Optional[ContextPayload]


class DocumentPayload(TypedDict, total=True):
    """Payload for sending a document message."""
    type: Literal["document"]
    document: Dict[str, Any]
    context: Optional[ContextPayload]


class StickerPayload(TypedDict, total=True):
    """Payload for sending a sticker message."""
    type: Literal["sticker"]
    sticker: Dict[str, Any]
    context: Optional[ContextPayload]


class LocationPayload(TypedDict, total=True):
    """Payload for sending a location message."""
    type: Literal["location"]
    location: Dict[str, Any]
    context: Optional[ContextPayload]


class ContactsPayload(TypedDict, total=True):
    """Payload for sending a contacts message."""
    type: Literal["contacts"]
    contacts: Any
    context: Optional[ContextPayload]


class ReactionPayload(TypedDict, total=True):
    """Payload for sending a reaction to a message."""
    type: Literal["reaction"]
    reaction: Dict[str, Any]
    context: Optional[ContextPayload]


class TemplatePayload(TypedDict, total=True):
    """Payload for sending a message template."""
    type: Literal["template"]
    template: Dict[str, Any]
    context: Optional[ContextPayload]


class InteractivePayload(TypedDict, total=True):
    """Payload for sending an interactive message."""
    type: Literal["interactive"]
    interactive: Dict[str, Any]
    context: Optional[ContextPayload]


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
"""A union of all supported WhatsApp message payload types."""


class WhatsAppSender(MessageSender):
    """Sends messages via the WhatsApp Cloud API.

    This class handles the sending of all supported WhatsApp message types,
    including text, media, interactive messages, and templates. It uses
    strictly typed dictionaries (`TypedDict`) to ensure that the payloads
    sent to the API are correctly formatted.

    Attributes:
        phone_number_id: The ID of the phone number to send messages from.
        access_token: The access token for the WhatsApp Cloud API.
        api_version: The version of the WhatsApp Cloud API to use.
        endpoint: The API endpoint for sending messages.
    """

    def __init__(
        self, phone_number_id: str, access_token: str, api_version: str = "v19.0"
    ):
        """Initializes the WhatsAppSender.

        Args:
            phone_number_id: The ID of the phone number to send messages from.
            access_token: The access token for the WhatsApp Cloud API.
            api_version: The version of the API to use. Defaults to "v19.0".
        """
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.api_version = api_version
        self.endpoint = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"

    def send_message(
        self,
        chat_id: str,
        text: Optional[str] = None,
        options: Optional[WhatsAppPayload] = None,
    ) -> None:
        """Sends a message to a WhatsApp user.

        This method constructs the appropriate payload and sends it to the
        WhatsApp Cloud API. If `options` are not provided, it sends a simple
        text message using the `text` argument.

        Args:
            chat_id: The recipient's WhatsApp ID.
            text: The text of the message. Required if `options` is not provided.
            options: A `WhatsAppPayload` dictionary containing the message details.
                This allows for sending complex message types like images, buttons, etc.

        Raises:
            requests.exceptions.HTTPError: If the API returns an error.
        """
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
        """Builds the payload for the WhatsApp API request.

        This private method constructs the JSON payload based on the provided
        message type and options.

        Args:
            chat_id: The recipient's WhatsApp ID.
            text: The text of the message. Used for default text messages.
            options: The `WhatsAppPayload` with the message details.

        Returns:
            A dictionary representing the JSON payload for the API request.

        Raises:
            ValueError: If `options` is not provided and `text` is None, or if
                the message type in `options` is unsupported.
        """
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
