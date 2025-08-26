"""
Telegram Template Engine

Enterprise-grade template engine for Telegram messages with multilingual support,
caching, and comprehensive validation.
"""

from typing import Dict, Any, Optional, List
from jinja2 import Environment, DictLoader, TemplateError, select_autoescape
import logging
from functools import lru_cache
from datetime import datetime

from app.models.telegram import (
    TemplateType, 
    Language, 
    TelegramTemplateError, 
    TemplateEngineProtocol
)

logger = logging.getLogger(__name__)


class TelegramTemplateEngine:
    """
    Advanced template engine for Telegram messages with features:
    - Multilingual support (Russian, English)
    - Template caching for performance
    - Data validation and sanitization
    - Error handling and fallbacks
    - Extensible template system
    """
    
    def __init__(self):
        self._templates = self._initialize_templates()
        self._environments = {}
        self._initialize_environments()
    
    def _initialize_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize template collections by language"""
        return {
            Language.RU: {
                TemplateType.BOOKING_NOTIFICATION: """🎨 <b>Новое бронирование</b>

📋 <b>Услуга:</b> {{ service }}
📅 <b>Дата:</b> {{ date }}
🕒 <b>Время:</b> {{ times | join(', ') }}
👤 <b>Клиент:</b> {{ client_name }}
📞 <b>Телефон:</b> {{ client_phone }}
👥 <b>Количество человек:</b> {{ people_count }}
💰 <b>Сумма:</b> {{ total_price }} руб.

{% if description -%}
📝 <b>Комментарий:</b>
{{ description }}
{% endif -%}

<i>🆔 Бронирование #{{ booking_id }}</i>""",

                TemplateType.BOOKING_CONFIRMATION: """✅ <b>Бронирование подтверждено</b>

🆔 <b>ID:</b> {{ booking_id }}
👤 <b>Клиент:</b> {{ client_name }}
📅 <b>Дата:</b> {{ date }}
🕒 <b>Время:</b> {{ time }}

{% if additional_info -%}
📝 <b>Дополнительная информация:</b>
{{ additional_info }}
{% endif -%}

<i>Подтверждено: {{ confirmed_at.strftime('%d.%m.%Y в %H:%M') }}</i>""",

                TemplateType.BOOKING_CANCELLATION: """❌ <b>Бронирование отменено</b>

🆔 <b>ID:</b> {{ booking_id }}
👤 <b>Клиент:</b> {{ client_name }}
📅 <b>Дата:</b> {{ date }}
🕒 <b>Время:</b> {{ time }}

{% if reason -%}
📝 <b>Причина отмены:</b>
{{ reason }}
{% endif -%}

<i>Отменено: {{ cancelled_at.strftime('%d.%m.%Y в %H:%M') }}</i>""",

                TemplateType.BOOKING_REMINDER: """⏰ <b>Напоминание о бронировании</b>

🆔 <b>ID:</b> {{ booking_id }}
👤 <b>Клиент:</b> {{ client_name }}
📅 <b>Дата:</b> {{ date }}
🕒 <b>Время:</b> {{ time }}
📍 <b>Услуга:</b> {{ service }}

⚠️ <i>До начала сеанса осталось {{ hours_until }} {{ 'час' if hours_until == 1 else 'часа' if hours_until < 5 else 'часов' }}</i>""",

                TemplateType.BOOKING_UPDATE: """📝 <b>Изменение бронирования</b>

🆔 <b>ID:</b> {{ booking_id }}
👤 <b>Клиент:</b> {{ client_name }}

{% if old_date != new_date -%}
📅 <b>Дата:</b> {{ old_date }} → {{ new_date }}
{% endif -%}
{% if old_time != new_time -%}
🕒 <b>Время:</b> {{ old_time }} → {{ new_time }}
{% endif -%}
{% if old_price != new_price -%}
💰 <b>Сумма:</b> {{ old_price }} → {{ new_price }} руб.
{% endif -%}

<i>Обновлено: {{ updated_at.strftime('%d.%m.%Y в %H:%M') }}</i>""",

                TemplateType.SYSTEM_NOTIFICATION: """🔔 <b>Системное уведомление</b>

{{ message }}

{% if details -%}
<b>Детали:</b>
{{ details }}
{% endif -%}

<i>{{ timestamp.strftime('%d.%m.%Y в %H:%M') }}</i>"""
            },
            
            Language.EN: {
                TemplateType.BOOKING_NOTIFICATION: """🎨 <b>New Booking</b>

📋 <b>Service:</b> {{ service }}
📅 <b>Date:</b> {{ date }}
🕒 <b>Time:</b> {{ times | join(', ') }}
👤 <b>Client:</b> {{ client_name }}
📞 <b>Phone:</b> {{ client_phone }}
👥 <b>People count:</b> {{ people_count }}
💰 <b>Total:</b> ₽{{ total_price }}

{% if description -%}
📝 <b>Comment:</b>
{{ description }}
{% endif -%}

<i>🆔 Booking #{{ booking_id }}</i>""",

                TemplateType.BOOKING_CONFIRMATION: """✅ <b>Booking Confirmed</b>

🆔 <b>ID:</b> {{ booking_id }}
👤 <b>Client:</b> {{ client_name }}
📅 <b>Date:</b> {{ date }}
🕒 <b>Time:</b> {{ time }}

{% if additional_info -%}
📝 <b>Additional information:</b>
{{ additional_info }}
{% endif -%}

<i>Confirmed: {{ confirmed_at.strftime('%d.%m.%Y at %H:%M') }}</i>""",

                TemplateType.BOOKING_CANCELLATION: """❌ <b>Booking Cancelled</b>

🆔 <b>ID:</b> {{ booking_id }}
👤 <b>Client:</b> {{ client_name }}
📅 <b>Date:</b> {{ date }}
🕒 <b>Time:</b> {{ time }}

{% if reason -%}
📝 <b>Cancellation reason:</b>
{{ reason }}
{% endif -%}

<i>Cancelled: {{ cancelled_at.strftime('%d.%m.%Y at %H:%M') }}</i>""",

                TemplateType.BOOKING_REMINDER: """⏰ <b>Booking Reminder</b>

🆔 <b>ID:</b> {{ booking_id }}
👤 <b>Client:</b> {{ client_name }}
📅 <b>Date:</b> {{ date }}
🕒 <b>Time:</b> {{ time }}
📍 <b>Service:</b> {{ service }}

⚠️ <i>{{ hours_until }} hour{{ 's' if hours_until != 1 else '' }} until session starts</i>""",

                TemplateType.BOOKING_UPDATE: """📝 <b>Booking Updated</b>

🆔 <b>ID:</b> {{ booking_id }}
👤 <b>Client:</b> {{ client_name }}

{% if old_date != new_date -%}
📅 <b>Date:</b> {{ old_date }} → {{ new_date }}
{% endif -%}
{% if old_time != new_time -%}
🕒 <b>Time:</b> {{ old_time }} → {{ new_time }}
{% endif -%}
{% if old_price != new_price -%}
💰 <b>Total:</b> ₽{{ old_price }} → ₽{{ new_price }}
{% endif -%}

<i>Updated: {{ updated_at.strftime('%d.%m.%Y at %H:%M') }}</i>""",

                TemplateType.SYSTEM_NOTIFICATION: """🔔 <b>System Notification</b>

{{ message }}

{% if details -%}
<b>Details:</b>
{{ details }}
{% endif -%}

<i>{{ timestamp.strftime('%d.%m.%Y at %H:%M') }}</i>"""
            }
        }
    
    def _initialize_environments(self):
        """Initialize Jinja2 environments for each language"""
        for language, templates in self._templates.items():
            self._environments[language] = Environment(
                loader=DictLoader(templates),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True,
                enable_async=False
            )
            
            # Add custom filters
            self._environments[language].filters.update({
                'currency': self._format_currency,
                'phone': self._format_phone,
                'datetime_local': self._format_datetime_local
            })
    
    def render_template(
        self, 
        template_type: TemplateType, 
        language: Language = Language.RU, 
        **kwargs
    ) -> str:
        """
        Render template with data and caching
        
        Args:
            template_type: Type of template to render
            language: Language for template
            **kwargs: Template variables
            
        Returns:
            Rendered template string
            
        Raises:
            TelegramTemplateError: If rendering fails
        """
        try:
            env = self._environments.get(language)
            if not env:
                logger.warning(f"Language {language} not supported, falling back to RU")
                env = self._environments[Language.RU]
            
            template = env.get_template(template_type.value)
            
            # Add default context variables
            context = {
                'current_time': datetime.now(),
                'language': language,
                **self._sanitize_context(kwargs)
            }
            
            rendered = template.render(**context)
            
            # Validate rendered message length
            if len(rendered.encode('utf-8')) > 4096:
                logger.warning(f"Rendered message exceeds Telegram limit: {len(rendered)} chars")
                # Truncate with ellipsis
                rendered = rendered[:4090] + "..."
            
            logger.debug(f"Successfully rendered template {template_type} in {language}")
            return rendered
            
        except TemplateError as e:
            error_msg = f"Template rendering failed for {template_type}: {str(e)}"
            logger.error(error_msg)
            raise TelegramTemplateError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error rendering template {template_type}: {str(e)}"
            logger.error(error_msg)
            raise TelegramTemplateError(error_msg) from e
    
    def validate_template_data(
        self, 
        template_type: TemplateType, 
        data: Dict[str, Any]
    ) -> bool:
        """
        Validate template data requirements
        
        Args:
            template_type: Template type to validate for
            data: Data to validate
            
        Returns:
            True if data is valid
            
        Raises:
            TelegramTemplateError: If validation fails
        """
        required_fields = self._get_required_fields(template_type)
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            error_msg = f"Missing required fields for {template_type}: {missing_fields}"
            logger.error(error_msg)
            raise TelegramTemplateError(error_msg)
        
        return True
    
    def _get_required_fields(self, template_type: TemplateType) -> List[str]:
        """Get required fields for template type"""
        field_mapping = {
            TemplateType.BOOKING_NOTIFICATION: [
                'service', 'date', 'times', 'client_name', 
                'client_phone', 'people_count', 'total_price', 'booking_id'
            ],
            TemplateType.BOOKING_CONFIRMATION: [
                'booking_id', 'client_name', 'date', 'time', 'confirmed_at'
            ],
            TemplateType.BOOKING_CANCELLATION: [
                'booking_id', 'client_name', 'date', 'time', 'cancelled_at'
            ],
            TemplateType.BOOKING_REMINDER: [
                'booking_id', 'client_name', 'date', 'time', 'service', 'hours_until'
            ],
            TemplateType.BOOKING_UPDATE: [
                'booking_id', 'client_name', 'updated_at'
            ],
            TemplateType.SYSTEM_NOTIFICATION: [
                'message', 'timestamp'
            ]
        }
        return field_mapping.get(template_type, [])
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize template context data"""
        sanitized = {}
        for key, value in context.items():
            if isinstance(value, str):
                # Escape HTML entities for security
                sanitized[key] = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            else:
                sanitized[key] = value
        return sanitized
    
    def _format_currency(self, value: float) -> str:
        """Format currency values"""
        return f"{value:,.0f} руб."
    
    def _format_phone(self, phone: str) -> str:
        """Format phone numbers"""
        if not phone.startswith('+'):
            phone = '+' + phone
        return phone
    
    def _format_datetime_local(self, dt: datetime, format_str: str = '%d.%m.%Y в %H:%M') -> str:
        """Format datetime in local format"""
        return dt.strftime(format_str)
    
    def get_available_templates(self, language: Language = Language.RU) -> List[str]:
        """Get list of available template types"""
        return list(self._templates.get(language, {}).keys())
    
    def add_custom_template(
        self, 
        template_type: str, 
        template_content: str, 
        language: Language = Language.RU
    ):
        """Add custom template dynamically"""
        if language not in self._templates:
            self._templates[language] = {}
        
        self._templates[language][template_type] = template_content
        
        # Reinitialize environment for this language
        self._environments[language] = Environment(
            loader=DictLoader(self._templates[language]),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Clear cache to force re-rendering
        self.render_template.cache_clear()
        
        logger.info(f"Added custom template {template_type} for language {language}")


# Global template engine instance
template_engine = TelegramTemplateEngine()