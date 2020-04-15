<%
from django.utils import timezone
%>
Dear ${' '.join(email_id.split('@')[0].split('.')).title()},

An illegal attempt was made to ${reason} with your email id at '${timezone.now().strftime("%A, %d %B %Y, %I:%M%p")} (UTC)'.

Regards,
Team ImageFactory