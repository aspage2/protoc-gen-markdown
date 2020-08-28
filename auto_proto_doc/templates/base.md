{# Display an enum #}
{%- macro enum_section(enum) -%}
### Enum: {{ enum.name }}
{% if enum.description %}{{ description(enum.description) }}
{% endif %}
{% for v in enum.values -%}
 * **{{ v.name }}**{% if v.description %}
 {{ description(v.description) }}{% endif %}
{% endfor -%}
{%- endmacro -%}

{# Display a description as a markdown quote #}
{%- macro description(desc) %} > {{ "\n > ".join(desc.strip().split("\n")) }}{%- endmacro -%}

{# Display a message name as a link to the correct message section #}
{%- macro message_link(msg_name) -%}
[{{ msg_name }}](#message-{{ msg_name.strip(".").replace(".", "").lower() }})
{%- endmacro -%}

{# Display an enum name as a link to the correct enum section #}
{%- macro enum_link(enum_name) -%}
[{{ enum_name }}](#enum-{{ enum_name.strip(".").replace(".", "").lower() }})
{%- endmacro -%}

{# Display a field's type. Hyperlink message-types to the appropriate section. #}
{%- macro field_type(field) -%}
**{% if field.repeated %}repeated {% endif %}{% if field.type.is_primitive %}{{ field.type.name }}
{%- elif field.type.is_message -%}{{ message_link(field.type.name) }}{%- else -%}{{ enum_link(field.type.name) }}
{%- endif %}**
{%- endmacro -%}

{# Display MessageFields as a table. #}
{%- macro field_table(flds) -%}
{% for field in flds -%}
 * `{{ field.name }}`, {{ field_type(field) }}{% if field.oneof %} (oneof {{ field.oneof.name }}){% endif %}
 > {{ field.description|replace("\n", " ")|trim(" ") }}
 
{% endfor -%}
{%- endmacro -%}

{# Display all information regarding a message #}
{%- macro message_section(msg) -%}
### Message: {{ msg.name }}
{% if msg.description %}{{ description(msg.description) }}{% endif %}
{% if msg.fields %}
{{ field_table(msg.fields) }}
{%- endif %}
{% for m in msg.messages %}{{ message_section(m) }}{% endfor -%}
{% for e in msg.enums %}{{ enum_section(e) }}{% endfor %}
{% endmacro -%}

{#- ######## BEGIN TEMPLATE ######## #}

# {{ file.name }}
{% if file.enums %} * [Enums](#enums) {% endif %}
{% if file.messages %} * [Messages](#messages) {% endif %}
{% if file.services %} * [Services](#services) {% endif %}
{% if file.enums %}
## Enums

{% for enum in file.enums %}{{ enum_section(enum) }}
{% endfor -%}
{%- endif -%}
{% if file.messages %}
## Messages
{% for msg in file.messages|sort(attribute="name") %}
{{ message_section(msg) -}}
------
{% endfor %}
{%- endif -%}
{%- if file.services %}
## Services
{% for svc in file.services %}
### Service: {{ svc.name }}
{%- if svc.description %}
{{ description(svc.description) }}{% endif %}
{%- for method in svc.rpcs %}
#### Method `{{ method.name }}`: {{ message_link(method.input_type) }} -> {{ message_link(method.output_type) }}
{% if method.description %}{{ description(method.description) }}{% endif %}
{% endfor %}
{% endfor %}
{% endif %}