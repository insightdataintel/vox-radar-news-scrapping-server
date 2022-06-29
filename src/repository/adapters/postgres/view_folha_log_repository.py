from src.repository.adapters.postgres.models.view_folha_log import ViewFolhaLog
from src.types.view_folha_log_dto import ViewFolhaLogDTO
 
class ViewFolhaLogRepository:

  def add_log(self, view_folha_log_dto:ViewFolhaLogDTO):    
    view_folha_log = ViewFolhaLog()
    view_folha_log.log = view_folha_log_dto.log
    view_folha_log.save()
