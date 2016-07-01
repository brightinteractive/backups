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
Usage
=====


s3backups has a **dry-run** mode. A dry run will only make read requests to AWS. **No actual restore requests will be made**.  


.. code-block:: bash

    $ s3backups assetbank-aecom-backups --dry-run

