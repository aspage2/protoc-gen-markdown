{# Display a description as a markdown quote #}
{%- macro description(desc) %} > {{ "\n > ".join(desc.strip().split("\n")) }}{%- endmacro -%}

{# Display a message name as a link to the correct message section #}
{%- macro message_link(msg_name) -%}
[{{ msg_name }}](#message-{{ msg_name.strip(".").replace(".", "").lower() }})
{%- endmacro -%}
{# Display a field's type. Hyperlink message-types to the appropriate section. #}
{%- macro field_type(field) -%}
**{% if field.repeated %}repeated {% endif %}{% if field.is_primitive %}{{ field.typ }}{% else %}{{ message_link(field.typ) }}{% endif %}**
{%- endmacro -%}
{# Display MessageFields as a table. #}
{%- macro field_table(flds) -%}
Name|Type|Description
-|-|-
{% for field in flds -%}
`{{ field.name }}`|{{ field_type(field) }}|{{ field.description|replace("\n", " ")|trim(" ") }}
{% endfor %}
{%- endmacro -%}

{# Display all information regarding a message #}
{%- macro message_section(msg) -%}
### Message: {{ msg.name }}
{% if msg.description %}{{ description(msg.description) }}{% endif %}
{% if msg.fields %}
**Non-Grouped Fields**

{{ field_table(msg.fields) }}
{%- endif %}
{% for o in msg.oneof_groups -%}
**OneOf Group**: {{ o.name }}
{% if o.description %}{{ description(o.description) }}{% endif %}
{{ field_table(o.fields) }}
{% endfor -%}
{%- for m in msg.messages %}{{ message_section(m) }}{% endfor -%}
{%- endmacro -%}

{#- ######## BEGIN TEMPLATE ######## #}

# MDL Protobuf - {{ file.name }}
{% if file.enums %} * [Enums](#enums) {% endif %}
{% if file.messages %} * [Messages](#messages) {% endif %}
{% if file.services %} * [Services](#services) {% endif %}
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