import typing

import openhab
import openhab.types

class Thing:
  """Base thing class"""
  types = []

  def __init__(self, openhab_conn: 'openhab.client.OpenHAB', json_data: dict) -> None:
    """
    Args:
      openhab_conn (openhab.OpenHAB): openHAB object.
      json_data (dic): A dict converted from the JSON data returned by the openHAB
                       server.
    """
    self.openhab = openhab_conn
    self.type_ = None
    self.name = ''
    self._status = None  # type: typing.Optional[typing.Any]
    self.channels = []
    self.associated_items = []
    self.init_from_json(json_data)

  def init_from_json(self, json_data: dict):
    """Initialize this object from a json configuration as fetched from
    openHAB

    Args:
      json_data (dict): A dict converted from the JSON data returned by the openHAB
                        server.
    """
    self.name = json_data['UID']
    self.type_ = json_data['thingTypeUID']
    self.__set_status(json_data['statusInfo'])
    self.channels = json_data['channels']
    self.extract_items(json_data['channels'])


  def is_online(self):
    """Returns True if the thing is online. Else False will be returned
    """
    return self._status == 'ONLINE'

  def _parse_rest(self, value: str) -> str:
    """Parse a REST result into a native object."""
    return value

  def _rest_format(self, value: str) -> str:
    """Format a value before submitting to openHAB."""
    return value

  def __set_status(self, value: list):
    """Private method for setting the internal state."""
    if value in ('UNDEF', 'NULL'):
      self._status = None
    else:
      self._status = self._parse_rest(value['status'])

  def extract_items(self, channel_list: list):
    for channel_entry in channel_list:
      for item_name in channel_entry['linkedItems']:
        if not item_name in self.associated_items:
          self.associated_items.append(item_name)

  def __str__(self) -> str:
    return '<{0} - {1} : {2}>'.format(self.type_, self.name, self._status)


