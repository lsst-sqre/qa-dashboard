# Validating database migrations

Make sure the migrations you create work with the latest production database before committing them

## Restore a copy of the squash production database

```
    # Load your s3 credentials
    source creds.sh
    
    aws s3 cp s3://jenkins-prod-qadb.lsst.codes-backups/qadb/latest.sql.gz .
    gzip -d latest.sql.gz
    
    mysql -u root -e "DROP DATABASE qadb"
    mysql -u root -e "CREATE DATABASE qadb"

    mysql -u root qadb < latest.sql
```

## Test migrations
```
    python manage.py migrate

```