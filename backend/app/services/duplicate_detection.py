import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.complaint import ComplaintRepository
from app.schemas.duplicate_detection import (
    DuplicateCheckResponse,
    DuplicateMatch,
)

logger = logging.getLogger(__name__)


def _calculate_token_overlap_score(text1: str, text2: str) -> float:
    """Calculates Jaccard word token overlap ratio between two strings (0.0 to 1.0)."""
    if not text1 or not text2:
        return 0.0
    words1 = set(w.lower() for w in text1.split() if len(w) > 3)
    words2 = set(w.lower() for w in text2.split() if len(w) > 3)
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)


class DuplicateDetectionService:
    """Service evaluating duplicate complaint likelihood and batch clusters."""

    def __init__(self, db: AsyncSession):
        self.repo = ComplaintRepository(db)

    async def check_duplicates(
        self, form_data: Dict[str, Any], exclude_id: Optional[int] = None
    ) -> DuplicateCheckResponse:
        """
        Evaluates input form_data against saved database complaints and returns duplicate matches.
        """
        target_batch = str(form_data.get("batch_number") or "").strip()
        target_product = str(form_data.get("product_name") or "").strip()
        target_category = str(form_data.get("complaint_category") or "").strip()
        target_customer = str(form_data.get("customer_name") or "").strip()
        target_email = str(form_data.get("customer_contact_email") or "").strip()
        target_desc = str(form_data.get("description") or "").strip()

        candidates = await self.repo.find_candidates_for_duplicate_check(
            batch_number=target_batch,
            product_name=target_product,
            exclude_id=exclude_id,
            limit=50,
        )

        matches: List[DuplicateMatch] = []
        highest_score = 0.0

        for candidate in candidates:
            score = 0.0
            matched_fields = []

            # 1. Batch Number Match (50 points)
            if (
                target_batch
                and candidate.batch_number
                and target_batch.lower() == candidate.batch_number.strip().lower()
            ):
                score += 50.0
                matched_fields.append("batch_number")

            # 2. Product Name Match (20 points)
            if target_product and candidate.product_name:
                c_prod = candidate.product_name.strip().lower()
                t_prod = target_product.lower()
                if t_prod in c_prod or c_prod in t_prod:
                    score += 20.0
                    matched_fields.append("product_name")

            # 3. Complaint Category Match (15 points)
            if target_category and candidate.complaint_category:
                if target_category.strip().lower() == candidate.complaint_category.strip().lower():
                    score += 15.0
                    matched_fields.append("complaint_category")

            # 4. Customer Contact Match (10 points)
            if target_customer and candidate.customer_name and target_customer.lower() == candidate.customer_name.strip().lower():
                score += 10.0
                matched_fields.append("customer_name")
            elif target_email and candidate.customer_contact_email and target_email.lower() == candidate.customer_contact_email.strip().lower():
                score += 10.0
                matched_fields.append("customer_contact_email")

            # 5. Token overlap on description (up to 15 points)
            if target_desc and candidate.description:
                overlap_ratio = _calculate_token_overlap_score(target_desc, candidate.description)
                if overlap_ratio > 0.2:
                    add_pts = round(overlap_ratio * 15.0, 1)
                    score += add_pts
                    matched_fields.append("description_similarity")

            score = min(100.0, round(score, 1))

            # Filter candidates with score >= 50%
            if score >= 50.0:
                tier = "HIGH_CONFIDENCE_DUPLICATE" if score >= 75.0 else "POTENTIAL_RELATED_COMPLAINT"
                matches.append(
                    DuplicateMatch(
                        complaint_id=candidate.id,
                        complaint_number=candidate.complaint_number,
                        product_name=candidate.product_name,
                        batch_number=candidate.batch_number,
                        title=candidate.title,
                        status=candidate.status,
                        initial_severity=candidate.initial_severity,
                        similarity_score=score,
                        match_tier=tier,
                        matched_fields=matched_fields,
                    )
                )

        # Sort matches by similarity score descending
        matches.sort(key=lambda m: m.similarity_score, reverse=True)
        if matches:
            highest_score = matches[0].similarity_score

        has_duplicates = len(matches) > 0

        if highest_score >= 75.0:
            top_match = matches[0]
            recommended_action = (
                f"High-confidence duplicate detected! Matches open complaint {top_match.complaint_number} "
                f"(Batch #{top_match.batch_number}, {top_match.similarity_score}% match). "
                "Recommend linking to existing batch investigation cluster."
            )
        elif has_duplicates:
            recommended_action = (
                f"Found {len(matches)} potential related complaint(s) sharing batch or product details. "
                "Review sibling complaints before proceeding."
            )
        else:
            recommended_action = "No duplicate complaints or batch clusters detected."

        return DuplicateCheckResponse(
            has_duplicates=has_duplicates,
            highest_similarity_score=highest_score,
            total_matches_count=len(matches),
            duplicate_matches=matches,
            recommended_action=recommended_action,
        )
