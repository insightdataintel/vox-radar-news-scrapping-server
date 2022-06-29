import json

class VoxradarNewsSaveDataQueueDTO:
  title: str
  domain: str
  source: str
  content: str
  date: str
  category: str
  image: str
  url: str

  def __init__(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
    self.title = title
    self.domain = domain
    self.source = source
    self.content = content
    self.date = date
    self.category = category
    self.image = image
    self.url = url

  def __iter__(self):
      yield from {
          "title": self.title,
          "domain": self.domain,
          "source": self.source,
          "content": self.content,
          "date": self.date,
          "category": self.category,
          "image": self.image,
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