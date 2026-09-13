Usage Examples
==============

Verifying CLI Configuration
---------------------------

To confirm that you've properly configured ``ascender`` to point at the correct
Ascender host, and that your authentication credentials are correct, run:

.. code:: bash

    ascender config

.. note:: For help configuring authentication settings with the ascender CLI, see :ref:`authentication`.

Printing the History of a Particular Job
----------------------------------------

To print a table containing the recent history of any jobs named ``Example Job Template``:

.. code:: bash

    ascender jobs list --all --name 'Example Job Template' \
        -f human --filter 'name,created,status'

Creating and Launching a Job Template
-------------------------------------

Assuming you have an existing Inventory named ``Demo Inventory``, here's how
you might set up a new project from a GitHub repository, and run (and monitor
the output of) a playbook from that repository:

.. code:: bash

    ascender projects create --wait \
        --organization 1 --name='Example Project' \
        --scm_type git --scm_url 'https://github.com/ansible/ansible-tower-samples' \
        -f human
    ascender job_templates create \
        --name='Example Job Template' --project 'Example Project' \
        --playbook hello_world.yml --inventory 'Demo Inventory' \
        -f human
    ascender job_templates launch 'Example Job Template' --monitor -f human

Relaunching a Job or a Workflow
-------------------------------

Relaunching runs a job again with the parameters it already carries, so nothing
has to be restated. A workflow can be relaunched whole, or from the nodes that
did not succeed, which reruns those and their descendants and leaves the rest
alone:

.. code:: bash

    ascender jobs relaunch 42 --monitor -f human
    ascender jobs relaunch 42 --hosts failed
    ascender workflow_jobs relaunch 7 --nodes failed --wait

Cancelling a Running Job
------------------------

Cancelling is available on every job resource: ``jobs``, ``workflow_jobs``,
``project_updates``, ``inventory_updates``, ``ad_hoc_commands`` and
``system_jobs``. The platform accepts the request and stops the job shortly
after, so the status printed back can still read ``running``. Asking to cancel a
job that has already finished returns the platform's own refusal:

.. code:: bash

    ascender jobs cancel 42
    ascender workflow_jobs cancel 7 -f human
    ascender project_updates cancel 13

Approving or Denying a Workflow Approval
----------------------------------------

A workflow that reaches an approval node waits there until somebody answers it.
Approving lets the workflow past the node, denying refuses it and fails the
workflow. Both print the approval as it stands afterwards, so the status in the
output is the one it has once the answer has landed:

.. code:: bash

    ascender workflow_approvals list -f human
    ascender workflow_approvals approve 21
    ascender workflow_approvals deny 22

Testing a Notification Template or a Credential
-----------------------------------------------

Testing asks the platform to exercise a thing rather than describe it, on
``notification_templates``, ``credentials`` and ``credential_types``. Testing a
notification template sends one, and the reply names the notification it queued,
whose own record carries the delivery status. Testing a lookup credential
performs the lookup and reports what came back:

.. code:: bash

    ascender notification_templates test 3 -f human
    ascender credentials test 9

``--inputs`` and ``--metadata`` try values that are not saved yet, which is what
the endpoint is for: trying a configuration before committing to it. Both take
JSON or YAML, or ``@`` a file holding either:

.. code:: bash

    ascender credentials test 9 \
        --metadata '{"secret_path": "/kv/prod", "secret_key": "password"}'
    ascender credential_types test 12 \
        --inputs '{"url": "https://vault.example.org", "token": "@~/.vault-token"}' \
        --metadata @lookup.yml

Updating a Job Template with Extra Vars
---------------------------------------

.. code:: bash

    ascender job_templates modify 1 --extra_vars "@vars.yml"
    ascender job_templates modify 1 --extra_vars "@vars.json"

Importing an SSH Key
--------------------

.. code:: bash

    ascender credentials create --credential_type 'Machine' \
        --name 'My SSH Key' --user 'alice' \
        --inputs '{"username": "server-login", "ssh_key_data": "@~/.ssh/id_rsa"}'

Import/Export
-------------

Intended to be similar to `tower-cli send` and `tower-cli receive`.

Exporting everything:

.. code:: bash

    ascender export

Exporting everything of some particular type or types:

.. code:: bash

    ascender export --users

Exporting a particular named resource:

.. code:: bash

    ascender export --users admin

Exporting a resource by id:

.. code:: bash

    ascender export --users 42

Importing a set of resources stored as a file:

.. code:: bash

    ascender import < resources.json
