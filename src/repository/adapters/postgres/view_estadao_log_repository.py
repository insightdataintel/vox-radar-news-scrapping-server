from src.repository.adapters.postgres.models.view_estadao_log import ViewEstadaoLog
from src.types.view_estadao_log_dto import ViewEstadaoLogDTO
 
class ViewEstadaoLogRepository:

  def add_log(self, view_estadao_log_dto:ViewEstadaoLogDTO):    
    view_estadao_log = ViewEstadaoLog()
    view_estadao_log.log = view_estadao_log_dto.log
    view_estadao_log.save()
