THINGSBOARD_HOST = 'mqtt.thingsboard.cloud'

class AttributeState:
  def __init__(self, ldrLowerBound, ldrUpdateFrequencySeconds, temperatureFanStatus):
    self.ldrLowerBound = ldrLowerBound
    self.ldrUpdateFrequencySeconds = ldrUpdateFrequencySeconds
    self.temperatureFanStatus = temperatureFanStatus

attributeState = AttributeState(150, 5, False)
attributeStateProcessUpdate = AttributeState(True, True, True)