#!/usr/bin/env python
import os
import sys

import dotenv

if __name__ == "__main__":
    dotenv.read_dotenv()
    
    print('CLIENT ID: {} - AUTH SECRET: {} '.format(\
        os.getenv('SOCIAL_AUTH_CLIENT_ID'), 
        os.getenv('SOCIAL_AUTH_SECRET') )
    )

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drchrono.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)