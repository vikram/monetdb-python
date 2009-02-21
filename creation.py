from django.conf import settings
from django.db.backends.creation import BaseDatabaseCreation

class DatabaseCreation(BaseDatabaseCreation):
    # This dictionary maps Field objects to their associated MonetSQLdb column
    # types, as strings. 
    data_types = {
        'AutoField':         'int AUTO_INCREMENT',
        'BooleanField':      'boolean',
        'CharField':         'varchar(%(max_length)s)',
        'CommaSeparatedIntegerField': 'varchar(%(max_length)s)',
        'DateField':         'date',
        'DateTimeField':     'timestamp',
        'DecimalField':      'numeric(%(max_digits)s, %(decimal_places)s)',
        'FileField':         'varchar(%(max_length)s)',
        'FilePathField':     'varchar(%(max_length)s)',
        'FloatField':        'numeric(%(max_digits)s, %(decimal_places)s)',
        'IntegerField':      'int',
        'IPAddressField':    'char(15)',
        'NullBooleanField':  'boolean',
        'OneToOneField':     'int',
        'PositiveIntegerField': 'int UNSIGNED',
        'PositiveSmallIntegerField': 'smallint UNSIGNED',
        'SlugField':         'varchar(%(max_length)s)',
        'SmallIntegerField': 'smallint',
        'TextField':         'clob',
        'TimeField':         'time',
        'USStateField':      'varchar(2)',
    }

    def sql_table_creation_suffix(self):
        suffix = []
        if settings.TEST_DATABASE_CHARSET:
            suffix.append('CHARACTER SET %s' % settings.TEST_DATABASE_CHARSET)
        if settings.TEST_DATABASE_COLLATION:
            suffix.append('COLLATE %s' % settings.TEST_DATABASE_COLLATION)
        return ' '.join(suffix)

    def sql_for_inline_foreign_key_references(self, field, known_models, style):
        "All inline references are pending under MonetSQLdb"
        return [], True
        
    def sql_for_inline_many_to_many_references(self, model, field, style):
        from django.db import models
        opts = model._meta
        qn = self.connection.ops.quote_name
        
        table_output = [
            '    %s %s %s,' %
                (style.SQL_FIELD(qn(field.m2m_column_name())),
                style.SQL_COLTYPE(models.ForeignKey(model).db_type()),
                style.SQL_KEYWORD('NOT NULL')),
            '    %s %s %s,' %
            (style.SQL_FIELD(qn(field.m2m_reverse_name())),
            style.SQL_COLTYPE(models.ForeignKey(field.rel.to).db_type()),
            style.SQL_KEYWORD('NOT NULL'))
        ]
        deferred = [
            (field.m2m_db_table(), field.m2m_column_name(), opts.db_table,
                opts.pk.column),
            (field.m2m_db_table(), field.m2m_reverse_name(),
                field.rel.to._meta.db_table, field.rel.to._meta.pk.column)
            ]
        return table_output, deferred
        
