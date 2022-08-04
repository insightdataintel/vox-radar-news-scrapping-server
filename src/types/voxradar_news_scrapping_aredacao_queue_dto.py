import json

class VoxradarNewsScrappingARedacaoQueueDTO:
  url:str

  def __init__(self, url: str):
    self.url = url

  def __iter__(self):
      yield from {
          "url": self.url
      }.items()

  def __str__(self):
      return json.dumps(dict(self), ensure_ascii=False)

  def __repr__(self):
      return self.__str__()

  @classmethod
  def from_json(cls, json_str):
    json_dict = json.loads(json_str)
    return cls(**json_dict)