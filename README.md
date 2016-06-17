# Tools for Managing Asset Bank Backups

# Configuration
Environment variables are injected into a configuration file programmatically
by Ansible as part of the deploy process. Sensitive data is kept in Ansible
Vault, the key to which can be found in [root pasword manager](http://root.password3.intranet/password/password/add/7a).
To create a configuration file for development we can deploy to localhost using
the command:
```bash
# NB. You will be prompted for the Ansible Vault password.
ansible-playbook deploy.yml -i development --ask-vault-pass
```
