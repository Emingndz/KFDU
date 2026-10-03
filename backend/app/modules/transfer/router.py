import json
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Form, Response, UploadFile, status

from app.core.deps import DbSession
from app.modules.transfer import service
from app.modules.transfer.schemas import ExportFormat, ImportJobOut, ImportSource, ImportStartOut
from app.modules.users.deps import CurrentUser

router = APIRouter(tags=["transfer"])


@router.get(
    "/users/me/export",
    response_class=Response,
    summary="Verilerimi dışa aktar",
    responses={
        200: {
            "description": "Dosya eki: JSON (profil, kütüphane, incelemeler, listeler) veya CSV",
            "content": {"application/json": {}, "text/csv": {}},
        }
    },
)
def export_data(user: CurrentUser, db: DbSession, format: ExportFormat = ExportFormat.JSON) -> Response:
    if format == ExportFormat.CSV:
        body = service.export_csv(db, user=user)
        media_type = "text/csv; charset=utf-8"
    else:
        body = json.dumps(service.export_json(db, user=user), ensure_ascii=False, indent=2)
        media_type = "application/json; charset=utf-8"
    filename = service.export_filename(user, format.value)
    return Response(
        content=body,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/users/me/import",
    response_model=ImportStartOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="İçe aktarma başlat (Letterboxd / Goodreads CSV)",
)
async def start_import(
    user: CurrentUser,
    db: DbSession,
    background_tasks: BackgroundTasks,
    source: Annotated[ImportSource, Form()],
    file: UploadFile,
) -> ImportStartOut:
    # Sınırın bir bayt fazlası okunur: dosya büyükse belleğe tamamı alınmadan anlaşılır
    content = await file.read(service.MAX_IMPORT_FILE_BYTES + 1)
    job, parsed = service.start_import(db, user=user, source=source, filename=file.filename, content=content)
    background_tasks.add_task(service.run_import_job, db.get_bind(), job.id, parsed.rows)
    return ImportStartOut(job_id=job.id)


@router.get("/users/me/import/{job_id}", response_model=ImportJobOut, summary="İçe aktarma durumu")
def get_import_job(job_id: int, user: CurrentUser, db: DbSession) -> ImportJobOut:
    return service.job_to_out(service.get_import_job(db, user=user, job_id=job_id))
