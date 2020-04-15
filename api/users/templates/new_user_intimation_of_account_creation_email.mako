%if firstname and lastname:
Dear ${firstname.title()} ${lastname.title()},
%else:
Dear ${' '.join(email_id.split('@')[0].split('.')).title()},
%endif

A fresh account with following credential has been created for you by your Administrator.

    username : ${username}
    email_id : ${email_id}

Please reset your password at the portal to login.

Regards,

Team ImageFactory