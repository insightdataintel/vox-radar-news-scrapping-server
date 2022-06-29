from src.repository.adapters.postgres.models.view_valor_log import ViewValorLog
from src.types.view_valor_log_dto import ViewValorLogDTO
 
class ViewValorLogRepository:

  def add_log(self, view_valor_log_dto:ViewValorLogDTO):    
    view_valor_log = ViewValorLog()
    view_valor_log.log = view_valor_log_dto.log
    view_valor_log.save()
