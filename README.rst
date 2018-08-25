[WIP]

python library for accessing the openHAB REST API
=================================================

This library allows for easily accessing the openHAB REST API.
A number of features are implemented but not all, this is work in progress.

Requirements
------------

  - python >= 3.5
  - python :: dateutil
  - python :: requests
  - python :: typing
  - TODO

Note on openHAB1:
-----------------

The current version is focused on OpenHAB 2.x; OpenHAB 1.x might still work, though this is not tested. If you require
older OpenHAB support, please use an older version of this library.

Example
-------

Example usage of the library:

.. code-block:: python

    from openhab import openHAB
    
    base_url = 'http://localhost:8080/rest'
    openhab = openHAB(base_url)
   
    # fetch all items
    items = openhab.fetch_all_items()
    
    # fetch all things
    things = openhab.fetch_all_things()
        
    sunset = items.get('Sunset')
    print(sunset.state)

    # fetch a single item
    item = openhab.get_item('light_switch')

    # turn a swith on
    item.on()

    # send a state update (this only update the state)
    item.state = 'OFF'

    # send a command
    item.command('ON')
    
    # check if item gets data from a thing
    item.has_associated_thing()
    
    # get thing and check if it is online
    thing = item.get_associated_thing()
    thing.is_online()
    
    
    
Rule engine
------------
[WIP] There might be breaking changes!

The rule engine offers a way to define rules with the OpenHAB like 'when', 'then' structure.
I extended this functionality with the two functions 'setup' and 'test'.

'setup' is the place where you can setup all the items that shall interact in the rule.
You may also define which actions (changes and commands) should trigger the rule.

In the 'when' function you may want to evaluate certain conditions on which the execution of 'then' depends.

The 'test' function offers the possibility to validate the result of the actions performed, e.g:
A light was switched on in the rule, so a lightsensor should read different values.

The rule engine depends on the mqtt-eventbus to receive updates from OpenHAB (better than continuous polling over REST).

    
    
    
