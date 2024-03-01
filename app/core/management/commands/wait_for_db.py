"""
Djando command to wait for the database to be available
"""
# we'll use this to make our execution sleep
import time 

# error when DB isnt ready
from psycopg2 import OperationalError as Psycopg2OpError

# the error Django throws when the DB isn't ready
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    
    """
    Django command to wait for database.
    """

    # this is standard syntax: the handle gets called when you call the Django command. 
    # Then the handle prints 'Waiting for database...'
    # Then we define the boolen db_up, assuming that the DB isn't up until we know that it is.
    def handle(self, *args, **options):
        """ Entrypoint for command. """

        # stdout is the standard output to log things to the screen as the command is executing
        self.stdout.write('Waiting for database...')

        # a boolean to track if the DB is up yet.
        db_up = False


        # The while logic here says that we'll call self.check(databases=...) and if the DB isn't ready then it throws an exception depending on the startup stage.
        while db_up is False:
            try:
                #this is the check method that we mock in the test
                self.check(databases=['default'])
                db_up = True
            # catch exceptions
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)


        self.stdout.write(self.style.SUCCESS('Database available!'))
