***************************************
Tools for Managing Asset Bank Backups
***************************************

-------------------
Development version
-------------------

The **latest development version** can be installed directly from GitHub:

.. code-block:: bash

    # Universal
    $ pip install --upgrade https://github.com/brightinteractive/s3backups/archive/devel.tar.gz


=====
Configuration
=====
s3backups uses the aws boto3 python sdk. There needs to be a profile definition called **s3backups** in **.aws/credentials**:


.. code-block:: bash

    [s3backups]
    aws_access_key_id = XXXXXXXXXXXXXXXXXXXXXXXXX
    aws_secret_access_key XXXXXXXXXXXXXXXXXXXXXXXX

**N.B. The credentials are held by the Hosting Circle**


=====
Usage
=====
To restore an entire **S3 Glacier** bucket just enter the name the name of bucket you would like to restore:  


.. code-block:: bash

    $ s3backups assetbank-aecom-backup

s3backups has a **dry-run** mode. A dry run will only make read requests to AWS. **No actual restore requests will be made**.  


.. code-block:: bash

    $ s3backups assetbank-aecom-backup --dry-run

