from django.conf import settings

import MySQLdb as Database

from django.db.backends.mysql.base import *

# setup pooling via SQLAlchemy for now
from sqlalchemy.pool import manage, QueuePool

pool_wait = getattr(settings,'DBPOOL_WAIT_TIMEOUT',28800)
pool_size = getattr(settings,'DBPOOL_SIZE',5)
pool_max = getattr(settings,'DBPOOL_MAX',100)
pool_giveup = getattr(settings,'DBPOOL_INTERNAL_CONN_TIMEOUT',5)


ManagedDatabase = manage(Database, 
                  echo = getattr(settings,'DEBUG',False),
                  poolclass = QueuePool,
                  recycle = pool_wait, 
                  pool_size = pool_size, 
                  max_overflow = pool_max,
                  timeout = pool_giveup)
                  
class FakeDatabaseWrapper(DatabaseWrapper):

    def _cursor(self):
        if not self._valid_connection():
            kwargs = {
                'conv': django_conversions,
                'charset': 'utf8',
                'use_unicode': True,
            }
            settings_dict = self.settings_dict
            if settings_dict['DATABASE_USER']:
                kwargs['user'] = settings_dict['DATABASE_USER']
            if settings_dict['DATABASE_NAME']:
                kwargs['db'] = settings_dict['DATABASE_NAME']
            if settings_dict['DATABASE_PASSWORD']:
                kwargs['passwd'] = settings_dict['DATABASE_PASSWORD']
            if settings_dict['DATABASE_HOST'].startswith('/'):
                kwargs['unix_socket'] = settings_dict['DATABASE_HOST']
            elif settings_dict['DATABASE_HOST']:
                kwargs['host'] = settings_dict['DATABASE_HOST']
            if settings_dict['DATABASE_PORT']:
                kwargs['port'] = int(settings_dict['DATABASE_PORT'])
            # We need the number of potentially affected rows after an
            # "UPDATE", not the number of changed rows.
            kwargs['client_flag'] = CLIENT.FOUND_ROWS
            kwargs.update(settings_dict['DATABASE_OPTIONS'])
            del(kwargs['conv'])
            self.connection = ManagedDatabase.connect(**kwargs)
            self.connection.encoders[SafeUnicode] = self.connection.encoders[unicode]
            self.connection.encoders[SafeString] = self.connection.encoders[str]
            connection_created.send(sender=self.__class__)
        cursor = CursorWrapper(self.connection.cursor())
        return cursor

DatabaseWrapper = FakeDatabaseWrapper