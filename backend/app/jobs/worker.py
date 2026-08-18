import logging
import asyncio
from typing import Optional, Dict, Any
from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.config.env import settings
from app.config.db import AsyncSessionLocal
from app.repositories.file import FileRepository
from app.repositories.complaint import ComplaintRepository, parse_flexible_date
from app.repositories.chat import ChatRepository
from app.schemas.complaint import ComplaintCreate
from app.models.chat import ChatMessage
from app.utils.pdf_loader import extract_text_from_file
from app.utils.structure_output import ComplaintStructuredParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_arq_pool: Optional[ArqRedis] = None


 
def get_arq_redis_settings() -> RedisSettings:
    """Returns ARQ RedisSettings instance configured from application settings."""
    host = settings.redis_host or "127.0.0.1"
    port = settings.redis_port or 6379
    if host in ("localhost", "::1"):
        host = "127.0.0.1"
    return RedisSettings(
        host=host,
        port=port,
    )


async def get_arq_pool() -> ArqRedis:
    """
    Retrieves or initializes the global ARQ Redis connection pool.
    """
    global _arq_pool
    if _arq_pool is None:
        redis_settings = get_arq_redis_settings()
        _arq_pool = await create_pool(redis_settings)
        logger.info(f"Initialized ARQ Redis connection pool at {settings.redis_host}:{settings.redis_port}")
    return _arq_pool


async def enqueue_file_processing(file_id: int) -> Optional[str]:
    """
    Enqueues background task for PDF/file extraction and LLM processing.
    
    :param file_id: Database ID of the FileAttachment record.
    :return: ARQ Job ID string or None if enqueuing fails.
    """
    try:
        pool = await get_arq_pool()
        job = await pool.enqueue_job("process_file_job", file_id, _keep_result=0)
        job_id = job.job_id if job else None
        logger.info(f"Enqueued ARQ process_file_job for file_id={file_id}, job_id={job_id}")
        return job_id
    except Exception as exc:
        logger.error(f"Failed to enqueue ARQ process_file_job for file_id={file_id}: {exc}")
        return None

 
async def process_file_job(ctx: Dict[str, Any], file_id: int, **kwargs) -> Dict[str, Any]:
    """
    ARQ Background Task for asynchronous PDF / file processing:
    1. Fetches file metadata by file_id and updates status to 'PROCESSING'.
    2. Extracts document text using LangChain PyPDFLoader / TextLoader.
    3. Runs LangChain/LangGraph LLM complaint structured parser on extracted text.
    4. Executes post-processing step:
       - Links and updates existing complaint record if linked directly or via chat session.
       - Auto-creates a new Complaint record if document describes a valid complaint and no complaint exists yet.
       - Appends structured AI response message into chat history if chat_id is present.
    5. Updates file status to 'COMPLETED' (or 'FAILED' on error).
    """
    logger.info(f"[ARQ Worker] Starting file processing job for file_id={file_id}")

    async with AsyncSessionLocal() as db:
        file_repo = FileRepository(db)
        complaint_repo = ComplaintRepository(db)
        chat_repo = ChatRepository(db)

        file_record = await file_repo.get_by_id(file_id)
        if not file_record:
            logger.error(f"[ARQ Worker] File attachment record with ID {file_id} not found.")
            return {"status": "failed", "error": f"File ID {file_id} not found"}

        file_record.status = "PROCESSING"
        await db.commit()
        await db.refresh(file_record)

        try:
            extracted_text = await asyncio.to_thread(
                extract_text_from_file, file_record.file_path, file_record.extension
            )
            file_record.extracted_text = extracted_text
            await db.commit()

            if not extracted_text:
                logger.warning(f"[ARQ Worker] Extracted text is empty for file_id={file_id}.")
                file_record.status = "COMPLETED"
                file_record.processing_error = "Extracted text was empty."
                await db.commit()
                return {"status": "completed", "warning": "Empty extracted text"}

            logger.info(f"[ARQ Worker] Passing extracted text ({len(extracted_text)} chars) to LLM parser...")
            parser = ComplaintStructuredParser()
            extracted_data = await parser.parse_complaint(extracted_text)

            target_complaint_id = file_record.complaint_id

            chat_record = None
            if file_record.chat_id:
                chat_record = await chat_repo.get_by_id(file_record.chat_id)
                if chat_record and chat_record.complaint_id and not target_complaint_id:
                    target_complaint_id = chat_record.complaint_id
                    file_record.complaint_id = target_complaint_id

            if target_complaint_id:
                logger.info(f"[ARQ Worker] Updating existing Complaint ID {target_complaint_id}")
                complaint = await complaint_repo.get_by_id(target_complaint_id)
                if complaint:
                    if extracted_data.customer_name:
                        complaint.customer_name = extracted_data.customer_name
                    if extracted_data.customer_contact_email:
                        complaint.customer_contact_email = extracted_data.customer_contact_email
                    if extracted_data.customer_contact_phone:
                        complaint.customer_contact_phone = extracted_data.customer_contact_phone
                    if extracted_data.complaint_source:
                        complaint.complaint_source = extracted_data.complaint_source
                    if extracted_data.product_name:
                        complaint.product_name = extracted_data.product_name
                    if extracted_data.product_code:
                        complaint.product_code = extracted_data.product_code
                    if extracted_data.dosage_form:
                        complaint.dosage_form = extracted_data.dosage_form
                    if extracted_data.product_strength:
                        complaint.product_strength = extracted_data.product_strength
                    if extracted_data.batch_number:
                        complaint.batch_number = extracted_data.batch_number
                    if extracted_data.affected_quantity:
                        complaint.affected_quantity = extracted_data.affected_quantity
                    if extracted_data.affected_quantity_unit:
                        complaint.affected_quantity_unit = extracted_data.affected_quantity_unit
                    if extracted_data.complaint_category:
                        complaint.complaint_category = extracted_data.complaint_category
                    if extracted_data.title:
                        complaint.title = extracted_data.title
                    if extracted_data.description:
                        complaint.description = extracted_data.description
                    if extracted_data.initial_severity:
                        complaint.initial_severity = extracted_data.initial_severity
                    if extracted_data.ai_risk_assessment:
                        complaint.ai_risk_assessment = extracted_data.ai_risk_assessment
                    if extracted_data.ai_suggested_next_action:
                        complaint.ai_suggested_next_action = extracted_data.ai_suggested_next_action

                    if extracted_data.manufacturing_date:
                        complaint.manufacturing_date = parse_flexible_date(extracted_data.manufacturing_date)
                    if extracted_data.expiry_date:
                        complaint.expiry_date = parse_flexible_date(extracted_data.expiry_date)
                    if extracted_data.incident_date:
                        complaint.incident_date = parse_flexible_date(extracted_data.incident_date)
                    
                    complaint.ai_extra_data = extracted_data.model_dump()
                    await db.commit()

            elif extracted_data.is_valid_complaint:
                logger.info(f"[ARQ Worker] Auto-creating Complaint record for file_id={file_id}")
                complaint_create = ComplaintCreate(
                    complaint_source=extracted_data.complaint_source or "File Upload",
                    customer_name=extracted_data.customer_name,
                    customer_contact_email=extracted_data.customer_contact_email,
                    customer_contact_phone=extracted_data.customer_contact_phone,
                    product_name=extracted_data.product_name,
                    product_code=extracted_data.product_code,
                    dosage_form=extracted_data.dosage_form,
                    product_strength=extracted_data.product_strength,
                    batch_number=extracted_data.batch_number,
                    affected_quantity=extracted_data.affected_quantity or 1.0,
                    affected_quantity_unit=extracted_data.affected_quantity_unit or "units",
                    complaint_category=extracted_data.complaint_category,
                    title=extracted_data.title or f"Complaint from {file_record.filename}",
                    description=extracted_data.description or extracted_text[:1000],
                    initial_severity=extracted_data.initial_severity,
                    ai_risk_assessment=extracted_data.ai_risk_assessment,
                    ai_suggested_next_action=extracted_data.ai_suggested_next_action,
                    manufacturing_date=extracted_data.manufacturing_date,
                    expiry_date=extracted_data.expiry_date,
                    incident_date=extracted_data.incident_date,
                )
                created_complaint = await complaint_repo.create(complaint_create)
                target_complaint_id = created_complaint.id
                file_record.complaint_id = target_complaint_id
                if chat_record:
                    chat_record.complaint_id = target_complaint_id

            if file_record.chat_id:
                logger.info(f"[ARQ Worker] Linking extraction to Chat ID {file_record.chat_id}")
                ai_msg = ChatMessage(
                    chat_id=file_record.chat_id,
                    sender="ai",
                    content=extracted_data.response_message or "Complaint details parsed from uploaded file.",
                    extra_data=extracted_data.model_dump(),
                )
                await chat_repo.add_message(ai_msg)

                if chat_record and chat_record.title in ["New Complaint Chat", None, ""]:
                    if extracted_data.product_name:
                        await chat_repo.update_title(chat_record.id, f"Complaint: {extracted_data.product_name}")
                    elif extracted_data.title:
                        await chat_repo.update_title(chat_record.id, extracted_data.title)

            file_record.status = "COMPLETED"
            file_record.processing_error = None
            await db.commit()

            logger.info(f"[ARQ Worker] Successfully completed file processing job for file_id={file_id}")
            return {"status": "completed", "file_id": file_id, "complaint_id": target_complaint_id}

        except Exception as exc:
            logger.error(f"[ARQ Worker] Error processing file_id={file_id}: {exc}", exc_info=True)
            file_record.status = "FAILED"
            file_record.processing_error = str(exc)
            await db.commit()
            return {"status": "failed", "file_id": file_id, "error": str(exc)}


async def startup(ctx: Dict[str, Any]) -> None:
    """ARQ worker startup hook."""
    logger.info("ARQ Worker starting up...")


async def shutdown(ctx: Dict[str, Any]) -> None:
    """ARQ worker shutdown hook."""
    logger.info("ARQ Worker shutting down...")


class WorkerSettings:
    """
    ARQ Worker configuration class executed via command line:
        arq app.jobs.worker.WorkerSettings
    """
    functions = [process_file_job]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = get_arq_redis_settings()
    max_tries = 2      
    keep_result = 0      


