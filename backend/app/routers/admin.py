import asyncio

from fastapi import APIRouter, Depends

from app.core.deps import get_current_admin_user
from app.core.logging import get_logger
from app.models.user import User
from app.services.scheduler import update_fixtures_job, update_odds_job

router = APIRouter(prefix="/admin", tags=["admin"])
logger = get_logger(__name__)

# Mantém referência forte às tasks em background — sem isso, o asyncio pode
# coletar a task antes dela terminar, já que nada mais a referencia depois
# que a requisição retorna.
_background_tasks: set[asyncio.Task] = set()


def _fire_and_forget(coro, job_name: str) -> None:
    task = asyncio.create_task(coro())
    _background_tasks.add(task)

    def _on_done(t: asyncio.Task) -> None:
        _background_tasks.discard(t)
        if t.cancelled():
            return
        exc = t.exception()
        if exc is not None:
            logger.error("admin_sync_job_failed", job=job_name, error=str(exc))

    task.add_done_callback(_on_done)


@router.post("/sync")
async def trigger_sync(current_user: User = Depends(get_current_admin_user)) -> dict:
    jobs = {
        "update_fixtures": update_fixtures_job,
        "update_odds": update_odds_job,
    }
    for job_name, job_fn in jobs.items():
        _fire_and_forget(job_fn, job_name)

    logger.info("admin_sync_triggered", admin_id=current_user.id, jobs=list(jobs))
    return {"jobs_triggered": list(jobs)}
