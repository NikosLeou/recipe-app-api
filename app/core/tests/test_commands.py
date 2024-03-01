"""
Test custom Django management commands.
"""

# we use patch to mock the behavior of the database bc we need to be able to simulate when the db is returning a response or not
from unittest.mock import patch

# OperationalError is one of the possible errors we might get when we try to connect to the DB before the DB is ready
from psycopg2 import OperationalError as Psycopg2Error

# call_command is a function by Django that allows us to call a command by its name; allows us to actually call the command that we 
# are testing
from django.core.management import call_command
# this is another operational error, which is another exception that might be thrown by the DB depending on what stage of the startup 
# process it is in
from django.db.utils import OperationalError
# this is the base test class that we'll use to create our unit tests. We use this for the case that the DB is not available and 
# therefore we dont need migrations etc to be applied.
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """ Test commands."""


    # 1st test case: the DB is ready
    def test_wait_for_db_ready(self, patched_check):
        """ test waiting for the database if database is ready """
        """ 
        so in this case, we wait for the db, and the db is already ready. So we dont want it to do anything,
        just continue with the execution of our application. To do this we need to mock the behavior of our DB. We do this with
        the @patch above. And we'll do this for all the different test methods, thats why we put the patch at the top of the 
        class above.
        The @patch contains the command we will be mocking. The path is: "core.management.commands.wait_for_db"; we will be using
        the Command.check which is actually provided by the BaseCommand: it has a check method that allows to check the status
        of the database. We will be mocking that check method to simulate the response, so we can simulate that method returning
        an exception or a value.
        Because of the @patch, we will have to add a new argument to each of the calls we make to the test methods: patched_check.
        """
        
        # The below says: when check is called inside our test case, we want it to return the True value.
        patched_check.return_value = True

        # this  will execute the code inside wait_for_db. It also checks that the command actually gets called. So it tests two
        # things: first, tests the situation where the db is ready, and 2nd that the command is set up correctly.
        call_command('wait_for_db')

        # we now check that the check method has been called. This basically ensures that the mocked object (i.e. the check
        # method inside the Command) is called with the "database" parameter and "default" value.
        patched_check.assert_called_once_with(databases=['default'])






    # 2nd test case: the DB isnt ready
    # here the check should return some exceptions
        
    @patch('time.sleep') # check below for explanation
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """ Test waiting for DB when getting OperationalError """

        # this is how  the mocking works when you want to raise an exception. In the method above, we wanted the mocked check
        # object there to return True. Here, we want it to raise an exception, as it would be the case if the DB wasnt ready.
        # To  make it raise an exception instead of actually returning a value you have to use side_effect; this allows you to
        # pass in various different items that are handled differently depending on their type. So if we pass in an exception, 
        # then the mocking library knows that it should raise that exception. If we pass in a boolean, then it will the boolean
        # value. So it allows us to define various different values that happen each time we call it in the order that we call it.
        # The below basically says: the first two times that we call the mocked method, we want it to raise the Psycopg2Error.
        # Then the next three times, we raise OperationalError. In general, there are different stages of PostgRES starting.
        # The first stage is that the applicaiton hasnt even started yet, so it's not ready to accept any connections and 
        # raises this Psycopg2Error. Then, there is the stage where the application is ready to accept connections, but it hasnt
        # set up the testing DB that we want to use; in that case, Django raises the OperationalError. We want to catch both of
        # them. The 2 and 3 are arbitrary, meant to simulate what you'd see in a real situation when you start the DB. Finally, 
        # the 6th time we call it, it should return True.
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]
    
        # call the command
        call_command('wait_for_db')

        # add the assertions
        # first, bc we raise 2 Psycopg2Error and then 3 OperationalError and then True, we expect to call the check 
        # method 6 times, bc it keeps calling it over and over again until it gets True. So if it's more than 6, it means we
        # called it an additional time  that wasnt necessary, and if i's less than 6 it means we are not checking properly.
        self.assertEqual(patched_check.call_count, 6)

        # like before, make sure that the check method has been called with "database=default"
        patched_check.assert_called_with(databases=['default'])

        # Last for this test case, we need to  mock the sleep method: we will be checking the DB and then be calling sleep, 
        # which waits for a period of time before it checks again (we dont want to make 1000 requests  to the DB while it tries 
        # to start). But we dont want to wait in our unit tests bc this will slow our tests down. So we add another patch to 
        # this method only (check above). It is important that all the arguments in the method are in the correct order: we 
        # go from the inside out. So the sleep patch goes first, then the check patch goes second.
        # So the sleep patch will replace the sleep function with a mock object (patched_sleep). So we are overwriting the
        # behavior of sleep so it doesnt weight and forces us to pause the execution of our unit test. It would just 
        # continue the execution of code and pass through immediatley without holding up the execution.